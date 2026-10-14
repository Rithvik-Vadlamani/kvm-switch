from pathlib import Path
import subprocess,json,struct,shutil
r=Path('work/independent-audit/economy/firmware');w=Path('work/independent-audit');results=[]
for name in ['test_control','test_outputs','test_startup']:
 z=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined',str(r/(name+'.c')),str(r/'control.c'),'-o',str(w/name)],capture_output=True,text=True);assert z.returncode==0,z.stderr
 z=subprocess.run([str(w/name)],capture_output=True,text=True);assert z.returncode==0,z.stderr;results.append({'test':name,'stdout':z.stdout.strip(),'undefined_behavior_sanitizer':'enabled'})
b=(r/'kvm.bin').read_bytes();v=struct.unpack('<48I',b[:192]);assert v[0]==0x20002000;reserved={4,5,6,7,8,9,10,12,13}
for i,a in enumerate(v[1:],1):
 if i in reserved:assert a==0
 else:assert 0x08000000<=a<0x08010000 and a&1,(i,hex(a))
assert len(b)<65536;results.append({'binary_bytes':len(b),'vector_count':len(v),'initial_stack_pointer':hex(v[0]),'Cortex_M0_reserved_vectors_zero':True,'all_nonreserved_handler_addresses_in_flash_and_thumb':True})
(w/'firmware-tests.json').write_text(json.dumps(results,indent=2));shutil.copytree(r,w/'original/firmware',dirs_exist_ok=True);print(results)
