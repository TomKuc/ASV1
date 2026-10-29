#!/usr/bin/env python3
"""Electrical corner calculation; not a hardware/safety certification.

References and caveats: docs/power_review.md.
NTC beta model is deliberately varied +/-3% in both R25 and B.
For the physical pack, enforce endpoint resistance requirements in the report.
"""
import itertools
import json
import math

SUPPLY_V = (2.955, 3.045)
SUPERVISOR_LOWEST_TRIP_V = 2.64 * .98
SUPERVISED_REFERENCE_V = (SUPERVISOR_LOWEST_TRIP_V, SUPPLY_V[1])
# Initial 0.1% + up to 50 ppm/K * 65 K = 0.425%; rounded outward.
RESISTOR_TOL = 0.005
CURRENT_A = (36.5e-6, 39.5e-6)
# 8 mV offset + half of 25 mV max hysteresis + 1.5 mV extra allowance
# for CMRR, reference/PCB errors. These terms are added conservatively.
COMPARATOR_ERROR_V = 0.022
R25_OHM = (9700.0, 10300.0)
BETA_K = (3435 * .97, 3435 * 1.03)


def divider_bounds(top, bottom, supply=SUPPLY_V):
    t = RESISTOR_TOL
    return (
        supply[0] * bottom * (1-t) / (top*(1+t)+bottom*(1-t)),
        supply[1] * bottom * (1+t) / (top*(1-t)+bottom*(1+t)),
    )


def threshold(name, top, bottom, supply=SUPPLY_V):
    vmin, vmax = divider_bounds(top, bottom, supply)
    vlow, vhigh = vmin-COMPARATOR_ERROR_V, vmax+COMPARATOR_ERROR_V
    values = []
    for v, current, r25, beta in itertools.product(
        (vlow, vhigh), CURRENT_A, R25_OHM, BETA_K
    ):
        resistance = v/current
        temp = 1/(1/298.15+math.log(resistance/r25)/beta)-273.15
        values.append(temp)
    return {
        "name": name,
        "divider_top_ohm": top,
        "divider_bottom_ohm": bottom,
        "nominal_reference_V": 3*bottom/(top+bottom),
        "effective_threshold_min_V": vlow,
        "effective_threshold_max_V": vhigh,
        "beta_model_trip_min_C": min(values),
        "beta_model_trip_max_C": max(values),
    }


hot_regulated = threshold("hot_regulated", 100000, 10000)
cold_regulated = threshold("cold_regulated", 27400, 10000)
hot = threshold("hot_supervised", 100000, 10000, SUPERVISED_REFERENCE_V)
cold = threshold("cold_supervised", 27400, 10000, SUPERVISED_REFERENCE_V)
endpoint_limits = {
    "minimum_R_at_0C_to_force_cold_fault_ohm":
        cold["effective_threshold_max_V"]/CURRENT_A[0],
    "maximum_R_at_45C_to_force_hot_fault_ohm":
        hot["effective_threshold_min_V"]/CURRENT_A[1],
    "pack_acceptance_min_R_at_0C_ohm": 24000,
    "pack_acceptance_max_R_at_45C_ohm": 5200,
}
result = {
    "status": "calculation_only_physical_validation_required",
    "hot": hot,
    "cold": cold,
    "hot_regulated_3V": hot_regulated,
    "cold_regulated_3V": cold_regulated,
    "endpoint_limits": endpoint_limits,
    "assumptions": {
        "LDO_V": SUPPLY_V,
        "supervised_reference_V": SUPERVISED_REFERENCE_V,
        "supervisor": "TLV803EA26DBZR; 2.64V +/-2%, excludes transient propagation sag",
        "reference_resistor_tolerance": RESISTOR_TOL,
        "TS_current_A": CURRENT_A,
        "comparator_error_allowance_V": COMPARATOR_ERROR_V,
        "R25_ohm": R25_OHM,
        "beta_K": BETA_K,
    },
}
assert hot["beta_model_trip_max_C"] < 45
assert cold["beta_model_trip_min_C"] > 0
assert 24000*CURRENT_A[0] > cold["effective_threshold_max_V"]
assert 5200*CURRENT_A[1] < hot["effective_threshold_min_V"]
print(json.dumps(result, indent=2))
