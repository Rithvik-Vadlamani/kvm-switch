#include <stdint.h>
extern uint32_t _estack,_sidata,_sdata,_edata,_sbss,_ebss;
extern int main(void);
void SysTick_Handler(void); void Default_Handler(void);
void Reset_Handler(void) {
 uint32_t *d=&_sdata,*s=&_sidata;while(d<&_edata)*d++=*s++;
 for(d=&_sbss;d<&_ebss;)*d++=0;
 (void)main();Default_Handler();
}
__attribute__((section(".isr_vector"),used))
void (* const vectors[48])(void)={
 (void (*)(void))(&_estack),Reset_Handler,Default_Handler,Default_Handler,
 [11]=Default_Handler,[14]=Default_Handler,[15]=SysTick_Handler,
 [16 ... 47]=Default_Handler
};
