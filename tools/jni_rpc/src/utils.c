#include "utils.h"
#include <stdlib.h>


void utf16_check_bom(uint16_t **src_p, size_t *size_p) {
    if (*size_p == 0)
        return;
    uint16_t bom = (*src_p)[0];
    bool utf16_le = bom == 0xFEFF;
    bool utf16_be = bom == 0xFFFE;
    if (utf16_le || utf16_be) {
        if (utf16_be) {
            size_t size = *size_p;
            uint16_t *src = *src_p;
            for (size_t pos = 0; pos < size; pos++)
                src[pos] = __builtin_bswap16(src[pos]);
        }
        (*src_p)++;
        (*size_p)--;
    }
    // "•".encode("utf-16").hex() -> 'fffe2220'
    // chr(0x2220) -> '∠'  (incorrect)
    // chr(0x2022) -> '•'  (correct)

    // in le-machine: 'fffe2220' -> 0xFEFF, 0x2022 -> utf16_le=true, don't swap, 0x2022 is correct
    // in be-machine: 'fffe2220' -> 0xFFFE, 0x2220 -> utf16_be=true, swap -> 0xFEFF, 0x2022, 0x2022 is correct
}

size_t utf16_size(const uint16_t *src, size_t src_size, bool *eos) {
    if (!src)
        return 0;
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

text _utf16_to_utf8(const uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool) {
    *dst_size = utf16_size(src, src_size, eos);
    if (*eos || *dst_size == 0)
        return "";

    uint8_t *dst = (uint8_t*) pool_alloc(pool, *dst_size);
    if (!dst) {
        perror("pool_alloc in utf16_to_utf8");
        *eos = true; return "";
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
    return (text) dst;
}

text utf16_to_utf8(uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool) {
    utf16_check_bom(&src, &src_size);
    return _utf16_to_utf8(src, src_size, dst_size, eos, pool);
}

text utf16_to_utf8_nobom(const uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool) {
    return _utf16_to_utf8(src, src_size, dst_size, eos, pool);
}


void utf8_check_bom(const uint8_t **src_p, size_t *size_p) {
    // utf16_le = 0xFEFF
    // 1110 1111 = EF
    // 10 111011 = BB
    // 10 111111 = BF
    if (*size_p < 3)
        return;
    const uint8_t *src = *src_p;
    if (src[0] != 0xEF || src[1] != 0xBB || src[2] != 0xBF)
        return;
    (*src_p) += 3;
    (*size_p) -= 3;
}

size_t utf8_size(const uint8_t *src, size_t src_size, bool *eos) {
    if (!src)
        return 0;
    size_t dst_size = 0, pos = 0;
    int codepoint = 0;
    while (pos < src_size) {
        size_t start_pos = pos;
        uint8_t item = src[pos++], b2, b3, b4;
        switch (item) {
        case 0x00 ... 0x7F:
            // 00000000..01111111
            dst_size++;
            break;
        case 0x80 ... 0xBF:
            fprintf(stderr, "Can't decode byte 0x%02X in position %zu: invalid start byte\n", item, start_pos);
            *eos = true; return 0;
        case 0xC0 ... 0xC1:
            fprintf(stderr, "Overlong 2-byte sequence at position %zu\n", start_pos);
            *eos = true; return 0;
        case 0xC2 ... 0xDF:
            // 11000000..11011111
            if (pos >= src_size) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: unexpected end of data\n", item, start_pos);
                *eos = true; return 0;
            }
            b2 = src[pos++];
            if ((b2 & 0xC0) != 0x80) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: invalid continuation byte\n", item, start_pos);
                *eos = true; return 0;
            }
            dst_size++;
            break;
        case 0xE0 ... 0xEF:
            // 11100000..11101111
            if (pos+1 >= src_size) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: unexpected end of data\n", item, start_pos);
                *eos = true; return 0;
            }
            b2 = src[pos++];
            b3 = src[pos++];
            if ((b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: invalid continuation byte\n", item, start_pos);
                *eos = true; return 0;
            }
            codepoint = ((item & 0x0F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
            if (codepoint >= 0xD800 && codepoint <= 0xDFFF) {
                fprintf(stderr, "Surrogate codepoint U+%04X at position %zu\n", codepoint, start_pos);
                *eos = true; return 0;
            }
            dst_size++;
            break;
        case 0xF0 ... 0xF4:
            // 11110000..11110111
            if (pos+2 >= src_size) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: unexpected end of data\n", item, start_pos);
                *eos = true; return 0;
            }
            b2 = src[pos++];
            b3 = src[pos++];
            b4 = src[pos++];
            if ((b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80 || (b4 & 0xC0) != 0x80) {
                fprintf(stderr, "Can't decode byte 0x%02X in position %zu: invalid continuation byte\n", item, start_pos);
                *eos = true; return 0;
            }
            codepoint = ((item & 0x07) << 18) | ((b2 & 0x3F) << 12) | ((b3 & 0x3F) << 6) | (b4 & 0x3F);
            if (codepoint < 0x10000) {
                fprintf(stderr, "Overlong 4-byte sequence at position %zu\n", start_pos);
                *eos = true; return 0;
            }
            if (codepoint > 0x10FFFF) {
                fprintf(stderr, "Codepoint > 0x10FFFF at position %zu\n", start_pos);
                *eos = true; return 0;
            }
            dst_size += 2;
            break;
        case 0xF5 ... 0xFF:
            // 0xF5, 0xF6, 0xF7: unicode overflow
            fprintf(stderr, "Can't decode byte 0x%02X in position %zu: invalid start byte\n", item, start_pos);
            *eos = true; return 0;
        }
    }
    return dst_size;
}

const uint16_t* _utf8_to_utf16(const uint8_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool) {
    *dst_size = utf8_size(src, src_size, eos);
    if (*eos || *dst_size == 0)
        return (const uint16_t*) ""; // void string for (*env)->NewString(env, ...)

    uint16_t *dst = (uint16_t*) pool_alloc(pool, (*dst_size) * sizeof(uint16_t));
    if (!dst) {
        perror("pool_alloc in utf8_to_utf16");
        *eos = true; return NULL;
    }
    size_t dst_pos = 0, src_pos = 0;
    int codepoint = 0;
    while (src_pos < src_size) {
        uint8_t item = src[src_pos++], b2, b3, b4;
        switch (item) {
        case 0x00 ... 0x7F:
            // 0xxxxxxx
            dst[dst_pos++] = item;
            break;
        case 0xC2 ... 0xDF:
            // 110xxxxx
            b2 = src[src_pos++]; 
            dst[dst_pos++] = ((item & 0x1F) << 6) | (b2 & 0x3F);
            break;
        case 0xE0 ... 0xEF:
            // 1110xxxx
            b2 = src[src_pos++];
            b3 = src[src_pos++];
            dst[dst_pos++] = ((item & 0x0F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
            break;
        case 0xF0 ... 0xF4:
            // 11110xxx
            b2 = src[src_pos++];
            b3 = src[src_pos++];
            b4 = src[src_pos++];
            codepoint = ((item & 0x07) << 18) | ((b2 & 0x3F) << 12) | ((b3 & 0x3F) << 6) | (b4 & 0x3F);
         // codepoint = (high - 0xD800) * 0x400 + (low - 0xDC00) + 0x10000;
            codepoint -= 0x10000;
            dst[dst_pos++] = 0xD800 | (codepoint >> 10); // high
            dst[dst_pos++] = 0xDC00 | (codepoint & 0x3FF); // low
            break;
        default:
            fprintf(stderr, "Invalid behaviour in utf8_size...\n");
            *eos = true; return NULL;
        }
    }
    return dst;
}

const uint16_t* utf8_to_utf16(const uint8_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool) {
    utf8_check_bom(&src, &src_size);
    return _utf8_to_utf16(src, src_size, dst_size, eos, pool);
}
