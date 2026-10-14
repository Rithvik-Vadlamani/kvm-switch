import json,itertools
from pathlib import Path
# Datasheet bounds, not a transistor-level supervisor simulation.
r50_min=1000*(1-.01-.0001*65);r3_min=10000*.99
cap_branch=3.6/r50_min;static_sink=3.6/r3_min+3.6/25000+5e-6+0.6e-6
truth=[]
for rail3,rail5,debug,request in itertools.product([False,True],repeat=4):
 nrst=rail3 and rail5 and not debug
 hub=nrst and request
 truth.append({'3V3_qualified':rail3,'5V_qualified':rail5,'external_reset_asserted':debug,'firmware_release_request':request,'hub_reset_released':hub})
report={'reset_logic_truth_table':truth,'assumption':'Digital qualification truth table only while supervisors/gate operate in specified supply range; threshold/delay history, rapid rail collapse, analog transient and back-power current are not simulated.', 'capacitor_discharge_current_bound':{'voltage_bound_V':3.6,'R50_min_ohm_including_1percent_and_65C_100ppm':r50_min,'bulk_cap_branch_peak_A':cap_branch,'pullups_and_input_leakage_A':static_sink,'sum_A':cap_branch+static_sink,'TPS3808_absolute_RESET_pin_current_A':.005,'R50_peak_power_W':3.6**2/r50_min,'R50_nominal_rating_W':.0625,'scope':'Bulk capacitor branch and DC pulls. Fast stray-capacitance spikes and actual RESET low-going waveform require measurement.'},'supervisor_thresholds_full_temperature':{'3V3_falling_min_V':3.07*.985,'3V3_falling_max_V':3.07*1.015,'3V3_conservative_rising_max_V':3.07*1.015*1.025,'5V_falling_min_V':4.65*.98,'5V_falling_max_V':4.65*1.02,'5V_conservative_rising_max_V':4.65*1.02*1.025,'release_delay_ms':[12,28]},'host_vbus_dividers':{'high_at_5V5_max_ratio_V':5.5*151.5/(99+151.5),'high_at_4V4_min_ratio_V':4.4*148.5/(101+148.5),'available_injection_current_per_host_if_core_unpowered_A':5.5/99000},'important_limits':['G33 senses near the regulator; remote IC voltage can be lower by copper/ground losses. Its minimum falling threshold does not guarantee all remote 3.0 V devices stay above their operating minimum until reset asserts. This is brownout recovery hardening, not a guaranteed uninterrupted operating envelope.','AP2112 temperature coefficient is typical, not a guaranteed maximum; do not turn it into a certified temperature-corner bound.','R50 preserves a series-RC reset filter but changes its high-frequency attenuation and discharge time. Reset waveforms and noise immunity are physical acceptance tests.']}
assert cap_branch+static_sink<.005
Path('work/independent-audit/reset-limits.json').write_text(json.dumps(report,indent=2));print(report['capacitor_discharge_current_bound'])
