#include "control.h"
#include <assert.h>
#include <stdio.h>
static void safe(const kvm_control *s) {
 assert(!s->usb_enabled || (s->hub_vbus && s->hub_reset_n && s->phase==KVM_RUN));
 assert(s->phase!=KVM_BREAK || (!s->video_enabled && !s->usb_enabled && !s->hub_reset_n));
}
int main(void) {
 kvm_control s;kvm_init(&s,0);
 for(uint32_t t=0;t<250;t++){kvm_tick(&s,t,true,true);safe(&s);assert(!s.usb_enabled);}
 kvm_tick(&s,250,true,true);assert(s.usb_enabled && s.video_enabled && s.selected==0);
 kvm_request(&s,260,1);assert(s.selected==0 && !s.usb_enabled);
 kvm_tick(&s,409,true,true);assert(s.selected==0);
 kvm_tick(&s,410,true,true);assert(s.selected==1 && !s.usb_enabled);
 kvm_tick(&s,510,true,true);assert(s.usb_enabled);
 kvm_tick(&s,511,true,false);safe(&s);assert(!s.usb_enabled);
 kvm_tick(&s,661,true,false);kvm_tick(&s,761,true,false);assert(!s.usb_enabled && s.video_enabled);
 kvm_tick(&s,762,true,true);assert(!s.usb_enabled);kvm_tick(&s,912,true,true);kvm_tick(&s,1012,true,true);assert(s.usb_enabled);
 /* Repeated request during disconnect extends the break and keeps actual select unchanged. */
 kvm_request(&s,1020,0);kvm_request(&s,1030,1);kvm_tick(&s,1170,true,true);assert(s.phase==KVM_BREAK && s.selected==1);
 /* Tick rollover must not shorten the disconnect. */
 kvm_init(&s,0xffffffc0u);kvm_tick(&s,20,true,true);assert(s.phase==KVM_BREAK);
 kvm_tick(&s,86,true,true);assert(s.phase==KVM_SETTLE);kvm_tick(&s,186,true,true);assert(s.usb_enabled);
 /* Exercise hot-plug and rapid button presses across many asynchronous event sequences. */
 uint32_t random=1;uint8_t prev=s.selected;bool was_usb=s.usb_enabled,was_video=s.video_enabled;
 for(uint32_t t=187;t<200000;t++) {
  random=random*1664525u+1013904223u;
  if((random&1023u)==0)kvm_request(&s,t,s.pending^1u);
  kvm_tick(&s,t,(random&0x10000u)!=0,(random&0x20000u)!=0);safe(&s);
  if(s.selected!=prev)assert(!was_usb && !was_video && !s.usb_enabled && !s.video_enabled);
  prev=s.selected;was_usb=s.usb_enabled;was_video=s.video_enabled;
 }
 puts("PASS: break-before-select, startup, reconnect, rapid requests, rollover, randomized events");
}
