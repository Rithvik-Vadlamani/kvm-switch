from pathlib import Path
import json,shutil,subprocess,collections,re
r=Path('work/independent-audit');src=r/'economy';dst=r/'strict';dst.mkdir(exist_ok=True)
for name in ['KVM_Switch.kicad_pcb','KVM_Switch.kicad_dru','KVM_Switch.kicad_pro','fp-lib-table']:shutil.copy2(src/name,dst/name)
shutil.copytree(src/'KVM_Custom_Footprints.pretty',dst/'KVM_Custom_Footprints.pretty',dirs_exist_ok=True)
p=dst/'KVM_Switch.kicad_pro';j=json.load(open(p));j['board']['design_settings']['rule_severities']['track_not_centered_on_via']='warning';j['board']['design_settings']['drc_exclusions']=[];p.write_text(json.dumps(j))
cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';subprocess.run([cli,'pcb','drc','--format','json','-o',str(r/'all-enabled-drc.json'),str(dst/'KVM_Switch.kicad_pcb')],check=True)
d=json.load(open(r/'all-enabled-drc.json'));geom=json.load(open('outputs/revision-A2-Economy/verification/routing-geometry.json'));items={a['uuid']:a for k in ['pads','tracks','vias'] for a in geom[k]};hs=lambda n:bool(re.search(r'_D[0-3]_[PN]$',n) or re.match(r'USB_(HOST[12]|UP|D[1-4])_[PN]$',n));high=[]
for v in d['violations']:
 if v['type']=='track_not_centered_on_via' and any(hs(items.get(a['uuid'],{}).get('net','')) for a in v['items']):high.append(v)
report={'all_reported_counts':dict(collections.Counter(v['type'] for v in d['violations'])),'high_speed_off_center_flags':high,'excluded_items_cleared_for_diagnostic':True};(r/'strict-summary.json').write_text(json.dumps(report,indent=2));print(report)
