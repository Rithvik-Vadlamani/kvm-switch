/* Exercise the actual GPIO write routine against a BSRR register model. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
static uint32_t slot, pending_address, pins;
static int pending, require_video;
static void flush_write(void) {
 if (!pending) return;
 assert(pending_address == 0x48000018u);
 uint32_t next=(pins | (slot & 0xffffu)) & ~(slot >> 16);
 if ((next ^ pins) & (1u<<4)) {
  assert(!(pins & (1u<<3)));
  assert(pins & (1u<<8));
 }
 if (require_video) assert(next & (1u<<3));
 pins=next; pending=0;
}
static uint32_t *mock_register(uint32_t address) {
 flush_write(); pending_address=address; pending=1; slot=0;
 return &slot;
}
#define REG(a) (*mock_register(a))
#define main firmware_entry
#include "main.c"
#undef main
int main(void) {
 kvm_control s;
 kvm_init(&s,0);
 s.video_enabled=true; s.hub_reset_n=true;
 s.usb_enabled=false; s.hub_vbus=false;
 pins=VIDEO|USB_OFF|RESET_N; require_video=1;
 /* Video must remain continuously enabled when the USB cable is absent. */
 for (unsigned i=0;i<1000;i++) {outputs(&s);flush_write();}
 require_video=0;
 kvm_request(&s,1,1); outputs(&s);flush_write();
 assert(!(pins&VIDEO));assert(pins&USB_OFF);
 kvm_tick(&s,151,false,true);outputs(&s);flush_write();
 assert(pins&SELECT);assert(!(pins&VIDEO));assert(pins&USB_OFF);
 kvm_tick(&s,251,false,true);outputs(&s);flush_write();
 assert(pins&VIDEO);assert(!(pins&USB_OFF));assert(pins&VBUS);
 puts("GPIO sequencing and video-without-USB regression tests passed");
}
