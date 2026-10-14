from pathlib import Path
import numpy as np,json,sys,os
from scipy.ndimage import label
from collections import defaultdict
suffix='-original' if os.environ.get('AUDIT_LABEL')=='A2' else '';r=Path('work/independent-audit/gerber-raster'+suffix);D=json.load(open('outputs/revision-A2'+('' if suffix else '-Economy')+'/verification/routing-geometry.json'))
parents={};labels=[];counts=[]
def root(v):
 if v not in parents:parents[v]=v
 if parents[v]!=v:parents[v]=root(parents[v])
 return parents[v]
def union(a,b):parents[root(a)]=root(b)
for side in ['top','inner_1','inner_2','bottom']:
 a=np.fromfile(r/(side+'.raw'),dtype=np.uint8).reshape(5000,5000)>127
 if len(sys.argv)>1 and sys.argv[1]=='bridge' and side=='top':
  ps=[next(p for p in D['pads'] if p['ref']=='R1' and p['pin']==str(k))['xy'] for k in (1,2)]
  for x,y in np.linspace(ps[0],ps[1],100):a[int(y*50)-3:int(y*50)+4,int(x*50)-3:int(x*50)+4]=True
 z,n=label(a,structure=np.ones((3,3)));labels.append(z);counts.append(n)
def at(l,xy):
 x,y=xy;ix=min(4999,max(0,int(x*50)));iy=min(4999,max(0,int(y*50)));return int(labels[l][iy,ix])
for hole in json.load(open(r/'drills.json')):
 if len(sys.argv)>1 and sys.argv[1]=='missing_drill':
  v=next(v for v in D['vias'] if v['net']=='USB_UP_P')
  if np.linalg.norm(np.array(v['xy'])-hole['xy'])<.01:continue
 nodes=[(l,at(l,hole['xy'])) for l in range(4) if at(l,hole['xy'])]
 for a,b in zip(nodes,nodes[1:]):union(a,b)
netnodes=defaultdict(set);noderefs=defaultdict(set);missing=[]
for p in D['pads']:
 if not p['net'] or not p['pin']:continue
 for layer in p['layers']:
  l=0 if layer==0 else 3;n=at(l,p['xy'])
  if not n:missing.append({'pad':p['ref']+':'+p['pin'],'layer':l,'xy':p['xy']});continue
  node=root((l,n));net=p['net'].replace('{slash}','/');netnodes[net].add(node);noderefs[node].add(net)
shorts=[sorted(v) for v in noderefs.values() if len(v)>1]
opens={net:list(nodes) for net,nodes in netnodes.items() if len(nodes)>1}
report={'method':'Independent Gerbonara copper artwork + Excellon plated holes, 20um/pixel raster connectivity. Pad net labels come from PCB and are independently compared with schematic in separate audit. 8-neighbour pixels; no drill barrel/etch/copper-thickness fabrication model.','copper_islands_per_layer':counts,'nets_sampled':len(netnodes),'missing_pad_copper':missing,'shorted_net_groups':shorts,'split_nets':opens,'resolution_mm':.02,'status':'PASS' if not(shorts or opens or missing) else 'INVESTIGATE'}
Path('work/independent-audit/gerber-connectivity'+suffix+('-'+sys.argv[1] if len(sys.argv)>1 else '')+'.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2)[:8000])
