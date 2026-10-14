/* Test actual GPIO initialization. Model register storage and BSRR side effects. */
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint32_t regs[7], addr_pending, slot, output;
static int pending, clock_reads, writes, bsrr_index, mode_index;
static unsigned idx(uint32_t a) {
 switch(a) {case 0x40021014u:return 0;case 0x48000000u:return 1;case 0x48000018u:return 2;case 0x48000004u:return 3;case 0x48000400u:return 4;case 0x48000800u:return 5;case 0x48001400u:return 6;default:assert(0);return 0;}
}
static void flush(void) {
 if(!pending)return;
 unsigned i=idx(addr_pending);
 if(slot!=regs[i] || i==2) {
  writes++;
  if(i==1){assert(bsrr_index>0);mode_index=writes;}
  if(i==2){output=(output|(slot&65535u))&~(slot>>16);bsrr_index=writes;}
  regs[i]=slot;
 }
 pending=0;
}
static uint32_t *reg(uint32_t a) {
 flush(); if(a==0x40021014u)clock_reads++;addr_pending=a;slot=regs[idx(a)];pending=1;return &slot;
}
#define REG(a) (*reg(a))
#define main firmware_entry
#include "main.c"
#undef main
int main(void) {
 /* Reset values include SWD alternate functions; preserve all unrelated pins. */
 const uint32_t reset_moder=0x28000000u;
 regs[1]=reset_moder; regs[0]=0x14u;output=0xffffu;
 gpio_init();flush();
 assert(regs[0]==(0x14u|(1u<<17)|(1u<<18)|(1u<<19)|(1u<<22)));assert(clock_reads>=2);
 assert(bsrr_index<mode_index);
 assert((output&(VIDEO|SELECT|USB_OFF|RESET_N|VBUS))==USB_OFF);
 const unsigned out[]={3,4,8,9,10},in[]={0,6,7};
 for(unsigned i=0;i<5;i++)assert(((regs[1]>>(2*out[i]))&3)==1);
 for(unsigned i=0;i<3;i++)assert(((regs[1]>>(2*in[i]))&3)==0);
 assert((regs[1]&0x3c000000u)==(reset_moder&0x3c000000u));
 const unsigned unused[]={1,2,5,11,12,15};
 for(unsigned i=0;i<6;i++)assert(((regs[1]>>(2*unused[i]))&3)==3);
 assert(regs[4]==0xffffffffu);assert(regs[5]==0xffffffffu);assert(regs[6]==0xffffffffu);
 assert(regs[3]==0); /* PA9 is push-pull into a separate Schmitt AND input. */
 puts("PASS: actual GPIO startup, clock readback, safe latch before output mode, SWD preservation");
}
