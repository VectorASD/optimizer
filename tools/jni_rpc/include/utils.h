#include "common.h"
#include "mem_pool.h"
#include <stdint.h> // uint16_t, size_t


#ifndef UTILS_H
#define UTILS_H


void utf16_check_bom(uint16_t **src_p, size_t *size_p);
size_t utf16_size(const uint16_t *src, size_t src_size, bool *eos);
text utf16_to_utf8(uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool);
text utf16_to_utf8_nobom(const uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool);


#endif // UTILS_H
