"""Finite-state exhaustive scheduler check against an independent Python oracle.
Actual C control.c is compiled as a host shared library. Time is normalized between
steps; test both normal and wrapping uint32 clocks. Includes all 1-ms timer ages,
late scheduling and repeated requests. Does not emulate CPU/USB electrical timing.
"""
import ctypes as C, subprocess,collections,json,sys
from pathlib import Path
root=Path('work/independent-audit/economy/firmware'); out=Path('work/independent-audit')
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/'control.c'
libpath=out/('control-'+source.stem+'.dylib')
subprocess.run(['cc','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror','-I'+str(root),str(source),'-o',str(libpath)],check=True)
class State(C.Structure):
 _fields_=[('deadline',C.c_uint32),('selected',C.c_uint8),('pending',C.c_uint8),('phase',C.c_int),('usb_enabled',C.c_bool),('video_enabled',C.c_bool),('hub_reset_n',C.c_bool),('hub_vbus',C.c_bool)]
l=C.CDLL(str(libpath.resolve()));l.kvm_tick.argtypes=[C.POINTER(State),C.c_uint32,C.c_bool,C.c_bool];l.kvm_request.argtypes=[C.POINTER(State),C.c_uint32,C.c_uint8]
# tuple: phase, remaining time, selected, pending, usb, video, reset release, vbus
initial=(0,150,0,0,False,False,False,False)
queue=collections.deque([initial]);seen={initial};checks=0
for base in [0,0xffffffc0]:
 s=State();l.kvm_init(C.byref(s),C.c_uint32(base));assert (s.deadline-base)&0xffffffff==150
while queue:
 state=queue.popleft();phase,left,selected,pending,usb,video,reset,vbus=state
 for elapsed in (0,1,99,100,149,150,151,250,1000):
  for request in (None,0,1):
   for hosts in (0,1,2,3):
    # Independent behavioural expectation, including one phase transition per tick.
    ph,rem,sel,pend,u,v,r,b=state; rem-=elapsed
    if request is not None:ph,rem,pend,u,v,r,b=0,150,request,False,False,False,False
    present=bool(hosts & (1<<sel))
    if ph==0 and rem<=0:ph,rem,sel,r=1,100,pend,True
    elif ph==1 and rem<=0:ph,rem,u,v,b=2,0,present,True,present
    elif ph==2 and present!=b:ph,rem,pend,u,v,r,b=0,150,sel,False,False,False,False
    if ph==2:rem=0
    expected=(ph,rem,sel,pend,u,v,r,b)
    for base in (0,0xffffffc0):
     s=State((base+left)&0xffffffff,selected,pending,phase,usb,video,reset,vbus);now=(base+elapsed)&0xffffffff
     if request is not None:l.kvm_request(C.byref(s),now,request)
     l.kvm_tick(C.byref(s),now,bool(hosts&1),bool(hosts&2));remaining=0 if s.phase==2 else C.c_int32(s.deadline-now).value
     actual=(s.phase,remaining,s.selected,s.pending,s.usb_enabled,s.video_enabled,s.hub_reset_n,s.hub_vbus)
     assert actual==expected,(state,elapsed,request,hosts,base,expected,actual)
     assert not s.usb_enabled or (s.phase==2 and s.hub_vbus and s.hub_reset_n and s.video_enabled)
     if s.selected!=selected:assert not (usb or video or s.usb_enabled or s.video_enabled)
     checks+=1
    if expected not in seen:seen.add(expected);queue.append(expected)
report={'status':'PASS','reachable_normalized_states':len(seen),'transition_cases_including_rollover':checks,'clock_step_ms':[0,1,99,100,149,150,151,250,1000],'scope':'Exhaustive for stated discrete event model; independent Python oracle compared with actual compiled C. No hardware or all possible CPU schedules claim.'}
print(json.dumps(report,indent=2))
if len(sys.argv)==1:(out/'firmware-exhaustive.json').write_text(json.dumps(report,indent=2))
