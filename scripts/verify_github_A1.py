#!/usr/bin/env python3
"""Verify an advertised GitHub branch and its release files in a temporary repo.

Read-only towards GitHub and the user's checkout: never pushes or updates .git.
Run from a normal network-enabled terminal after importing/pushing the bundle.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remote', default='https://github.com/TomKuc/ASV1.git')
    parser.add_argument('--branch', default='final/a1-prototype-2026-10-29')
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'reports/github_verification_after_import.json')
    args = parser.parse_args()
    if not all(c in '0123456789abcdef' for c in args.expected_commit) or len(args.expected_commit) != 40:
        parser.error('--expected-commit must be the full 40-character SHA')
    report = {'checked_utc': datetime.now(timezone.utc).isoformat(),
              'remote': args.remote, 'branch': args.branch,
              'expected_commit': args.expected_commit,
              'status': 'NOT_VERIFIED', 'pushed_by_this_script': False,
              'main_checkout_modified': False}

    def run(*command):
        return subprocess.run(list(command), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=90, check=True)

    try:
        ref = 'refs/heads/'+args.branch
        advertised = run('git', 'ls-remote', args.remote, ref).stdout.decode().splitlines()
        matches = [line.split()[0] for line in advertised if line.split()[1] == ref]
        if matches != [args.expected_commit]:
            report.update(status='REMOTE_REF_MISMATCH', advertised_commits=matches)
        else:
            # All fetched objects stay in the temporary directory, not .git.
            with tempfile.TemporaryDirectory(prefix='asv1-remote-') as temp:
                run('git', 'init', '--bare', temp)
                git = ['git', '--git-dir='+temp]
                run(*git, 'fetch', '--depth=1', '--no-tags', args.remote, ref)
                fetched = run(*git, 'rev-parse', 'FETCH_HEAD').stdout.decode().strip()
                if fetched != args.expected_commit:
                    raise ValueError('Remote branch changed between advertisement and fetch')
                raw = run(*git, 'show', fetched+':reports/current_A1_manifest.json').stdout
                manifest = json.loads(raw)
                local = ROOT/'reports/current_A1_manifest.json'
                if raw != local.read_bytes():
                    raise ValueError('Remote and local current_A1_manifest.json differ')
                failures = []
                for rel, expected in manifest['files_sha256'].items():
                    blob = run(*git, 'show', fetched+':'+rel).stdout
                    if hashlib.sha256(blob).hexdigest() != expected:
                        failures.append(rel)
                report.update(status='PASS' if not failures else 'REMOTE_FILE_HASH_MISMATCH',
                              remote_commit=fetched, files_checked=len(manifest['files_sha256']),
                              mismatches=failures,
                              manifest_sha256=hashlib.sha256(raw).hexdigest())
    except subprocess.CalledProcessError as exc:
        # Avoid echoing credential-bearing URLs or arbitrary command stderr.
        report.update(status='NOT_VERIFIED_NETWORK_OR_ACCESS_ERROR', git_exit_code=exc.returncode)
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        report.update(status='NOT_VERIFIED', error=str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
