import json,math,sys
from pathlib import Path
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
D=json.loads(Path(sys.argv[1]).read_text());ts=D['tracks'];pads=D['pads'];vs=D['vias']
# Geometry-only DC network; pads are ideal nodes, via barrels conservatively 6mOhm.
# 30um minimum assumed outer copper at 85C. Ground drop handled separately as budget.
rho=1.724e-5*(1+.00393*65);thick=.030
loads={('U'+str(i),'5'):.5 for i in range(20,24)};loads.update({('U32','1'):.15,('U33','1'):.15,('L2','1'):.22})
source=('L1','2')
net='+5V'
if len(sys.argv)>3:
 cfg=json.loads(Path(sys.argv[3]).read_text());net=cfg['net'];source=tuple(cfg['source']);loads={tuple(a[:2]):a[2] for a in cfg['loads']}
pn=lambda p:('pad',p['ref'],p['pin'])
ts=[t for t in ts if t['net']==net];ps=[p for p in pads if p['net']==net];vs=[v for v in vs if v['net']==net]
key=lambda p,l:(round(p[0],6),round(p[1],6),l)
points=set()
for t in ts:points|={key(t['a'],t['layer']),key(t['b'],t['layer'])}
for v in vs:points|={key(v['xy'],0),key(v['xy'],1)}
parent={p:p for p in points}
def root(x):
 if x not in parent:parent[x]=x
 if parent[x]!=x:parent[x]=root(parent[x])
 return parent[x]
def union(a,b):parent[root(a)]=root(b)
for p in ps:
 x0,y0,x1,y1=p['box']
 for q in points:
  if q[2] in p['layers'] and x0-1e-6<=q[0]<=x1+1e-6 and y0-1e-6<=q[1]<=y1+1e-6:union(q,pn(p))
edges=[]
for t in ts:
 a=t['a'];z=t['b'];dx=z[0]-a[0];dy=z[1]-a[1];ll=dx*dx+dy*dy
 if ll<1e-10:continue
 pp=[]
 for q in points:
  if q[2]!=t['layer']:continue
  u=((q[0]-a[0])*dx+(q[1]-a[1])*dy)/ll
  if -1e-6<=u<=1+1e-6 and math.hypot(q[0]-a[0]-u*dx,q[1]-a[1]-u*dy)<1e-5:pp.append((u,q))
 pp.sort()
 for (u,p),(v,q) in zip(pp,pp[1:]):
  r=(v-u)*math.sqrt(ll)*rho/(thick*t['width'])
  if root(p)!=root(q) and r>1e-10:edges.append((root(p),root(q),r))
for v in vs:edges.append((root(key(v['xy'],0)),root(key(v['xy'],1)),.006))
src=root(('pad',)+source); nodes={x for e in edges for x in e[:2]}|{root(pn(p)) for p in ps};nodes.discard(src);idx={p:i for i,p in enumerate(nodes)}
A=lil_matrix((len(idx),len(idx)));I=np.zeros(len(idx))
for a,b,r in edges:
 g=1/r
 if a!=src:A[idx[a],idx[a]]+=g
 if b!=src:A[idx[b],idx[b]]+=g
 if a!=src and b!=src:A[idx[a],idx[b]]-=g;A[idx[b],idx[a]]-=g
for refpin,current in loads.items():
 assert any((p['ref'],p['pin'])==refpin for p in ps), refpin
 node=root(('pad',)+refpin)
 if node!=src:I[idx[node]]+=current
V=spsolve(A.tocsr(),I); result=[]
for p in ps:
 if (p['ref'],p['pin']) in loads:
  node=root(pn(p)); result.append({'ref':p['ref'],'pin':p['pin'],'current_A':loads[p['ref'],p['pin']],'drop_V':float(V[idx[node]]) if node!=src else 0})
report={'assumptions':'Positive supply DC network at 85C; 30um copper; via 6mOhm, pads ideal, ground return excluded; no transient/SPICE claim','load_A':sum(loads.values()),'loads':result,'max_drop_V':max(x['drop_V'] for x in result)}
print(json.dumps(report,indent=2));Path(sys.argv[2]).write_text(json.dumps(report,indent=2))
