#include "common.h"
#include <stdint.h> // uint16_t, size_t


#ifndef UTILS_H
#define UTILS_H


void check_bom(uint16_t **src_p, size_t *size_p);
size_t utf16_size(uint16_t *src, size_t src_size, bool *eos);
uint8_t* utf16_to_utf8(uint16_t *src, size_t src_size, size_t *dst_size, bool *eos);


#endif // UTILS_H
