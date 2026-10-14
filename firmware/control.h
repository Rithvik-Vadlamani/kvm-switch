#ifndef KVM_CONTROL_H
#define KVM_CONTROL_H
#include <stdint.h>
#include <stdbool.h>
typedef enum { KVM_BREAK, KVM_SETTLE, KVM_RUN } kvm_phase;
typedef struct {
 uint32_t deadline; uint8_t selected, pending; kvm_phase phase;
 bool usb_enabled, video_enabled, hub_reset_n, hub_vbus;
} kvm_control;
void kvm_init(kvm_control *s, uint32_t now);
void kvm_request(kvm_control *s, uint32_t now, uint8_t host);
void kvm_tick(kvm_control *s, uint32_t now, bool host1_present, bool host2_present);
#endif
