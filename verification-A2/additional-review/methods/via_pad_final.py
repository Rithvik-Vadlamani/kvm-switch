import json
from shapely.geometry import Point,box
s=json.load(open('outputs/revision-A2-Economy/verification/routing-geometry.json'));bad=[]
for v in s['vias']:
 for a in s['pads']:
  # Effective bounding boxes conservatively bound rounded pads; paste-only apertures duplicate EP region.
  d=Point(v['xy']).distance(box(*a['box']))-v['drill']/2
  if d<.09:bad.append({'via':v['uuid'],'xy':v['xy'],'net':v['net'],'pad':a['ref']+':'+a['pin'],'gap':d})
print(json.dumps(bad,indent=2));open('work/independent-audit/via-pad-final-flags.json','w').write(json.dumps(bad,indent=2))
