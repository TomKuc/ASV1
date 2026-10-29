#!/bin/sh
# Keep non-design KiCad settings inside the workspace in restricted environments.
set -eu
TASK_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
KICAD_APP=${ANKLE_KICAD_APP:-/Applications/KiCad/KiCad.app}
export KICAD_CONFIG_HOME="$TASK_ROOT/.work/kicad/config"
export XDG_CACHE_HOME="$TASK_ROOT/.work/cache"
export KICAD_CACHE_HOME="$TASK_ROOT/.work/cache"
export KICAD10_FOOTPRINT_DIR="$KICAD_APP/Contents/SharedSupport/footprints"
export KICAD10_SYMBOL_DIR="$KICAD_APP/Contents/SharedSupport/symbols"
export KICAD10_3DMODEL_DIR="$KICAD_APP/Contents/SharedSupport/3dmodels"
mkdir -p "$KICAD_CONFIG_HOME" "$XDG_CACHE_HOME"
exec "$KICAD_APP/Contents/MacOS/kicad-cli" "$@"
