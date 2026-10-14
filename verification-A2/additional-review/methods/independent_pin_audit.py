from pathlib import Path
import pcbnew as p,json,xml.etree.ElementTree as E,math
r=Path('work/independent-audit/economy');b=p.LoadBoard(str(r/'KVM_Switch.kicad_pcb'));root=E.parse('work/independent-audit/new-netlist.xml').getroot();expected={};comps={a.get('ref'):a for a in root.findall('./components/comp')}
for net in root.findall('./nets/net'):
 for n in net.findall('node'):expected[n.get('ref'),n.get('pin')]=net.get('name')
fs={f.GetReference():f for f in b.GetFootprints()};assert set(comps)<=set(fs);errors=[];count=0;mechanical=[]
for ref,f in fs.items():
 if ref not in comps:
  assert ref.startswith(('FID','H'));continue
 fields={v.get('name'):v.text for v in comps[ref].findall('./fields/field')}
 for k in ('MPN','LCSC Part'):
  if f.GetField(k).GetText()!=fields[k]:errors.append([ref,k,f.GetField(k).GetText(),fields[k]])
 for pad in f.Pads():
  pin=pad.GetNumber()
  if not pin:continue
  count+=1;exp=expected.get((ref,pin),'')
  if exp.replace('{slash}','/')!=pad.GetNetname().replace('{slash}','/'):errors.append([ref,pin,exp,pad.GetNetname()])
# Test opposite-side part bodies against through-hole lead/pad projections.
for ref,f in fs.items():
 for a in f.Pads():
  if not a.GetDrillSize().x or a.GetAttribute()!=p.PAD_ATTRIB_PTH:continue
  x,y=p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)
  for other,g in fs.items():
   if other==ref or g.GetLayer()==f.GetLayer():continue
   lay=p.B_CrtYd if g.GetLayer()==p.B_Cu else p.F_CrtYd;draws=[q for q in g.GraphicalItems() if q.GetLayer()==lay]
   if not draws:continue
   bs=[q.GetBoundingBox() for q in draws];x0=min(p.ToMM(z.GetLeft()) for z in bs);x1=max(p.ToMM(z.GetRight()) for z in bs);y0=min(p.ToMM(z.GetTop()) for z in bs);y1=max(p.ToMM(z.GetBottom()) for z in bs)
   radius=max(p.ToMM(a.GetDrillSize().x),p.ToMM(a.GetDrillSize().y))/2+.25
   if math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))<radius:mechanical.append({'lead':ref+':'+a.GetNumber(),'other':other,'lead_xy':[x,y],'courtyard':[x0,y0,x1,y1],'lead_plus_solder_radius_mm':radius})
report={'component_count':len(comps),'numbered_pads_checked':count,'pin_net_and_part_errors':errors,'opposite_side_through_hole_proximity':mechanical,'scope':'Initial conservative circular drill projection; flagged slots require oriented-shape refinement. Fresh XML netlist vs every numbered PCB pad and all MPN/LCSC fields; opposite-side through-hole drill radius +0.25mm vs courtyard screening, not 3D enclosure validation.'}
Path('work/independent-audit/pin-and-mechanical-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
