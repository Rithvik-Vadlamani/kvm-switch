import json,re,math
from pathlib import Path
from collections import defaultdict
import numpy as np,shapely
from shapely.geometry import Polygon,LineString,Point
D=json.load(open('outputs/revision-A2-Economy/verification/routing-geometry.json'));P=json.load(open('work/independent-audit/planes.json'))
planes=[shapely.union_all([Polygon(q['outer'],q['holes']).buffer(0) for q in v]) for v in P.values()]
hs=lambda n:bool(re.search(r'_D[0-3]_[PN]$',n) or re.match(r'USB_(HOST[12]|UP|D[1-4])_[PN]$',n))
ts=[t for t in D['tracks'] if hs(t['net'])];vs=[v for v in D['vias'] if hs(v['net'])]
own={}
for n in {t['net'] for t in ts}:
 pair=n[:-1];own[n]=shapely.union_all([Point(v['xy']).buffer(v['diameter']/2+.2+.03) for v in vs if v['net'][:-1]==pair])
missing=[];total=0
for t in ts:
 line=LineString([t['a'],t['b']]);total+=line.length
 # Exclude only each pair's own via antipad regions. Other-net voids remain reportable.
 gap=line.difference(planes[t['layer']]).difference(own[t['net']])
 if gap.length>.005:missing.append({'net':t['net'],'track_uuid':t['uuid'],'length_mm':gap.length,'geometry':shapely.to_geojson(gap)})
close=[]
for i,t in enumerate(ts):
 a=np.array(t['a']);d=np.array(t['b'])-a;l=np.linalg.norm(d)
 if l<2:continue
 u=d/l
 for z in ts[i+1:]:
  if t['layer']!=z['layer'] or t['net'][:-1]==z['net'][:-1]:continue
  za=np.array(z['a']);zd=np.array(z['b'])-za;zl=np.linalg.norm(zd)
  if zl<2 or abs(u@zd/zl)<.9999:continue
  delta=za-a;distance=abs(u[0]*delta[1]-u[1]*delta[0]);gap=distance-(t['width']+z['width'])/2
  pro=sorted([u@(za-a),u@(za+zd-a)]);overlap=max(0,min(l,pro[1])-max(0,pro[0]))
  if gap<5*max(t['width'],z['width']) and overlap>2:
   close.append({'net_a':t['net'],'net_b':z['net'],'gap_mm':float(gap),'parallel_overlap_mm':float(overlap),'a':t['a'],'b':t['b'],'za':z['a'],'zb':z['b']})
rr=json.load(open('outputs/revision-A2-Economy/verification/return-via-audit.json'))
out={'plane_count':len(planes),'plane_areas_mm2':[p.area for p in planes],'high_speed_track_segments':len(ts),'aggregate_signal_centerline_length_mm':total,'signal_centerline_over_unrelated_plane_voids':missing,'parallel_segments_below_5W_with_over_2mm_overlap':sorted(close,key=lambda q:-q['parallel_overlap_mm']),'max_return_via_mm':rr['max_distance_mm'],'TI_return_via_distance_guideline_mm':5.08,'scope':'Actual filled plane polygons and routed centerlines. Own differential-pair via antipads excluded from plane-void flags. 5W spacing is a layout screening guideline; connector/IC escapes need individual interpretation. Not a field/crosstalk certification.'}
Path('work/independent-audit/reference-audit.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if not isinstance(v,list)});print('unrelated voids',len(missing),'close parallel segments',len(close));print(sorted(close,key=lambda q:-q['parallel_overlap_mm'])[:5])
