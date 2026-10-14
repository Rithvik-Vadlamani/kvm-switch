from pathlib import Path
import shutil,json,subprocess
src=Path('work/independent-audit/economy');dst=Path('work/independent-audit/strict-manufacturing');shutil.copytree(src,dst,dirs_exist_ok=True)
p=dst/'KVM_Switch.kicad_pro';j=json.loads(p.read_text());j['board']['design_settings']['rules']['min_hole_clearance']=.3;j['board']['design_settings']['rules']['min_hole_to_hole']=.45
for cat in ['track_not_centered_on_via','footprint_filters_mismatch','footprint_type_mismatch','missing_courtyard','tuning_profile_track_geometries']:j['board']['design_settings']['rule_severities'][cat]='warning'
p.write_text(json.dumps(j,indent=2))
subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','pcb','drc','--format','json','-o','work/independent-audit/strict-manufacturing-drc.json',str(dst/'KVM_Switch.kicad_pcb')],capture_output=True,check=True)
m=json.load(open('outputs/revision-A2-Economy/verification/manufacturing-geometry.json'));ids={p['uuid'] for p in m['pads'] if p['drill'][0]>0 and p['attribute']==0};dr=json.load(open('work/independent-audit/strict-manufacturing-drc.json'));bad=[]
for v in dr['violations']:
 if v['type']=='hole_clearance' and any(i['uuid'] in ids for i in v['items']):bad.append(v)
 if v['type']=='hole_to_hole' and all(i['uuid'] in ids for i in v['items']):bad.append(v)
print('PTH hole to copper at 0.30 mm and PTH pair hole separation at 0.45 mm:',len(bad),'flags')
Path('outputs/revision-A2-Economy/verification/PTH-manufacturing-audit.json').write_text(json.dumps({'test':'PTH to copper >=0.30 mm; PTH hole separation >=0.45 mm; all-via tightened stress run filtered to actual plated component holes','flags':bad},indent=2))
for x in bad[:5]:print(x)
