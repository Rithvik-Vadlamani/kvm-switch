import pcbnew as p,json
from pathlib import Path
b=p.LoadBoard('work/independent-audit/economy/KVM_Switch.kicad_pcb')
def points(c):
 return [[p.ToMM(c.CPoint(i).x),p.ToMM(c.CPoint(i).y)] for i in range(c.PointCount())]
result={}
for la in [p.In1_Cu,p.In2_Cu]:
 polys=[]
 for z in b.Zones():
  if z.GetNetname()!='GND' or not z.IsOnLayer(la):continue
  s=z.GetFilledPolysList(la)
  for i in range(s.OutlineCount()):polys.append({'outer':points(s.COutline(i)),'holes':[points(s.CHole(i,j)) for j in range(s.HoleCount(i))]})
 result[b.GetLayerName(la)]=polys
Path('work/independent-audit/planes.json').write_text(json.dumps(result))
print({k:len(v) for k,v in result.items()})
