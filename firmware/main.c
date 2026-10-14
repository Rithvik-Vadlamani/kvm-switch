/* STM32F030C8T6: HSI 8 MHz, SWD remains on PA13/PA14.
 * Register addresses/bits: ST RM0360 and cmsis-device-f0/stm32f030x8.h.
 * PA0 button (low), PA3 video OE (high), PA4 select (0=host 1),
 * PA6/7 host VBUS dividers, PA8 USB /OE, PA9 hub reset release request (U36 ANDs MCU_NRST), PA10 VBUS_DET.
 */
#include "control.h"
#ifndef REG
#define REG(a) (*(volatile uint32_t *)(a))
#endif
#define GPIOA 0x48000000u
#define RCC_AHBENR REG(0x40021014u)
#define MODER REG(GPIOA)
#define IDR REG(GPIOA+0x10u)
#define BSRR REG(GPIOA+0x18u)
#define IWDG_KR REG(0x40003000u)
#define IWDG_PR REG(0x40003004u)
#define IWDG_RLR REG(0x40003008u)
#define IWDG_SR REG(0x4000300cu)
#define VIDEO (1u<<3)
#define SELECT (1u<<4)
#define USB_OFF (1u<<8)
#define RESET_N (1u<<9)
#define VBUS (1u<<10)
static volatile uint32_t milliseconds;
void SysTick_Handler(void) { milliseconds++; }
static void outputs(const kvm_control *s) {
 /* Disconnect first; select can only change while both switches are off.
  * Hardware pulls disable both switches; U34/U35/U36 and R49 hold the hub
  * reset during supply faults, MCU reset and programming.
  */
 if (!s->video_enabled) BSRR=VIDEO<<16;
 if (!s->usb_enabled) BSRR=USB_OFF|(VBUS<<16);
 uint32_t v=(s->selected?SELECT:0u)|(s->usb_enabled?0u:USB_OFF)|
  (s->video_enabled?VIDEO:0u)|(s->hub_reset_n?RESET_N:0u)|(s->hub_vbus?VBUS:0u);
 BSRR=v|(((VIDEO|SELECT|USB_OFF|RESET_N|VBUS)&~v)<<16);
}
void Default_Handler(void) {
 BSRR=USB_OFF|((VIDEO|VBUS|RESET_N)<<16);
 for (;;) {} /* Independent watchdog resets after a fault. */
}
static void gpio_init(void) {
 RCC_AHBENR|=(1u<<17)|(1u<<18)|(1u<<19)|(1u<<22); (void)RCC_AHBENR;
 BSRR=USB_OFF|((VIDEO|SELECT|RESET_N|VBUS)<<16);
 uint32_t m=MODER;
 static const uint8_t outpins[]={3,4,8,9,10};
 for (unsigned i=0;i<sizeof(outpins);i++) {unsigned p=outpins[i]*2u;m=(m&~(3u<<p))|(1u<<p);}
 m&=~((3u<<0)|(3u<<12)|(3u<<14));
 /* Disable digital input buffers on unused pins (ST DS9773, I/O current).
  * Keep PA13/PA14 SWD. PB6/PB7 are reserved but unused by this firmware.
  */
 static const uint8_t unused_a[]={1,2,5,11,12,15};
 for (unsigned i=0;i<sizeof(unused_a);i++) m|=3u<<(unused_a[i]*2u);
 MODER=m;
 REG(0x48000400u)=0xffffffffu; /* GPIOB: no active firmware signals. */
 REG(0x48000800u)=0xffffffffu; /* GPIOC: unused, including unbonded pins. */
 REG(0x48001400u)=0xffffffffu; /* GPIOF: unused; HSI clock, no HSE crystal. */

}
int main(void) {
 gpio_init();
 REG(0xe000e014u)=7999u; REG(0xe000e018u)=0u; REG(0xe000e010u)=7u;
 /* Start first: this forces the LSI clock on before waiting for updates. */
 IWDG_KR=0xcccc; IWDG_KR=0x5555; IWDG_PR=4; IWDG_RLR=625;
 while(IWDG_SR){}
 IWDG_KR=0xaaaa; /* about 1 s at nominal 40 kHz LSI. */
 kvm_control s; kvm_init(&s,milliseconds); outputs(&s);
 uint32_t last=milliseconds; uint8_t btn_count=0, h1_count=0, h2_count=0;
 bool pressed=false,h1=false,h2=false;
 for (;;) {
  uint32_t now=milliseconds; if(now==last)continue; last=now;
  uint32_t in=IDR;
  if (!(in&1u)) {if(btn_count<30)btn_count++;} else {if(btn_count>0)btn_count--;}
  if(btn_count==30 && !pressed) {pressed=true;kvm_request(&s,now,s.pending^1u);}
  if(btn_count==0)pressed=false;
  if(in&(1u<<6)) {if(h1_count<20)h1_count++;} else {if(h1_count)h1_count--;}
  if(in&(1u<<7)) {if(h2_count<20)h2_count++;} else {if(h2_count)h2_count--;}
  if(h1_count==20)h1=true;
  if(h1_count==0)h1=false;
  if(h2_count==20)h2=true;
  if(h2_count==0)h2=false;
  kvm_tick(&s,now,h1,h2); outputs(&s); IWDG_KR=0xaaaa;
 }
}
