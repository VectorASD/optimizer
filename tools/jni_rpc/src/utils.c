#include "utils.h"
#include <stdlib.h>


void check_bom(uint16_t **src_p, size_t *size_p) {
    if (*size_p == 0)
        return;
    uint16_t bom = (*src_p)[0];
    bool utf16_be = bom == 0xFEFF;
    bool utf16_le = bom == 0xFFEF;
    if (utf16_be || utf16_le) {
        (*src_p)++;
        (*size_p)--;
        if (utf16_le) {
            size_t size = *size_p;
            uint16_t *src = *src_p;
            for (size_t pos = 0; pos < size; pos++)
                src[pos] = __builtin_bswap16(src[pos]);
        }
    }
}

size_t utf16_size(uint16_t *src, size_t src_size, bool *eos) {
    size_t dst_size = 0, pos = 0;
    int codepoint = 0;
    while (pos < src_size) {
        uint16_t item = src[pos++];
        if (item == 0xFFEF || item == 0xFEFF) {
            fprintf(stderr, "Unexpected BOM\n");
            *eos = true; return 0;
        }
        if (item >= 0xDC00 && item <= 0xDFFF) {
            fprintf(stderr, "Unexpected low-surrogate\n");
            *eos = true; return 0;
        }
        if (item >= 0xD800 && item <= 0xDBFF) {
            if (pos >= src_size) {
                fprintf(stderr, "Unexpected eos after high-surrogate\n");
                *eos = true; return 0;
            }
            int high = (int) item, low = (int) src[pos++];
            if (low < 0xDC00 || low > 0xDFFF) {
                fprintf(stderr, "Invalid low-surrogate: 0x%X\n", low);
                *eos = true; return 0;
            }
            codepoint = (high - 0xD800) * 0x400 + (low - 0xDC00) + 0x10000;
            if (codepoint > 0x10FFFF) {
                fprintf(stderr, "Invalid codepoint: 0x%X\n", codepoint);
                *eos = true; return 0;
            }
        } else
            codepoint = (int) item;
        dst_size += codepoint <= 0x7F ? 1 : codepoint <= 0x7FF ? 2 : codepoint <= 0xFFFF ? 3 : 4;
    }
    return dst_size;
}

uint8_t* utf16_to_utf8(uint16_t *src, size_t src_size, size_t *dst_size, bool *eos) {
    check_bom(&src, &src_size);
    *dst_size = utf16_size(src, src_size, eos);
    if (*eos || *dst_size == 0)
        return NULL;

    uint8_t *dst = (uint8_t*) malloc(*dst_size);
    if (!dst) {
        perror("malloc utf16_to_utf8");
        *eos = true; return NULL;
    }
    size_t dst_pos = 0, src_pos = 0;
    int codepoint = 0;
    while (src_pos < src_size) {
        uint16_t item = src[src_pos++];
        if (item >= 0xD800 && item <= 0xDBFF) {
            int high = (int) item, low = (int) src[src_pos++];
            codepoint = (high - 0xD800) * 0x400 + (low - 0xDC00) + 0x10000;
        } else
            codepoint = (int) item;

        if (codepoint <= 0x7F)
            // 0xxxxxxx
            dst[dst_pos++] = (uint8_t) codepoint;
        else if (codepoint <= 0x7FF) {
            // 110xxxxx
            // 10xxxxxx
            dst[dst_pos++] = (uint8_t) (0xC0 | codepoint >> 6);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint & 0x3F);
        } else if (codepoint <= 0xFFFF) {
            // 1110xxxx
            // 10xxxxxx (x2)
            dst[dst_pos++] = (uint8_t) (0xE0 | codepoint >> 12);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint >> 6 & 0x3F);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint & 0x3F);
        } else {
            // 11110xxx
            // 10xxxxxx (x3)
            dst[dst_pos++] = (uint8_t) (0xF0 | codepoint >> 18);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint >> 12 & 0x3F);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint >> 6 & 0x3F);
            dst[dst_pos++] = (uint8_t) (0x80 | codepoint & 0x3F);
        }
    }
    return dst;
}
