import json
from pathlib import Path
from shapely.geometry import LineString,box
r=Path('work/independent-audit');j=json.load(open(r/'pin-and-mechanical-audit.json'));dr=json.load(open(r/'drill-shapes.json'));out=[]
for flag in j['opposite_side_through_hole_proximity']:
 ref,pin=flag['lead'].split(':');shapes=[LineString([d['a'],d['b']]).buffer(d['radius']+.25) for d in dr if d['ref']==ref and d['pin']==pin];court=box(*flag['courtyard']);distance=min(s.distance(court) for s in shapes);out.append(dict(flag,oriented_slot_projection_clearance_mm=distance,overlap=any(s.intersects(court) for s in shapes)))
j['opposite_side_slot_refinement']=out;assert not any(q['overlap'] for q in out);(r/'pin-and-mechanical-audit.json').write_text(json.dumps(j,indent=2))
