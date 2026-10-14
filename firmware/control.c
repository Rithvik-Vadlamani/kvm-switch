#include "control.h"
static bool expired(uint32_t now, uint32_t deadline) {return (int32_t)(now-deadline)>=0;}
void kvm_request(kvm_control *s, uint32_t now, uint8_t host) {
 s->usb_enabled=false; s->video_enabled=false; s->hub_vbus=false; s->hub_reset_n=false;
 s->pending=host&1u; s->phase=KVM_BREAK; s->deadline=now+150u;
}
void kvm_init(kvm_control *s, uint32_t now) {s->selected=0; kvm_request(s,now,0);}
void kvm_tick(kvm_control *s, uint32_t now, bool h1, bool h2) {
 bool present=s->selected ? h2 : h1;
 if (s->phase==KVM_BREAK && expired(now,s->deadline)) {
  s->selected=s->pending; s->hub_reset_n=true; s->phase=KVM_SETTLE; s->deadline=now+100u;
 } else if (s->phase==KVM_SETTLE && expired(now,s->deadline)) {
  s->phase=KVM_RUN; s->video_enabled=true; s->hub_vbus=present; s->usb_enabled=present;
 } else if (s->phase==KVM_RUN && present!=s->hub_vbus) {
  kvm_request(s,now,s->selected);
 }
}
