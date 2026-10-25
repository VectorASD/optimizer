#include "common.h"
#include "mem_pool.h"
#include <stdint.h> // uint16_t, size_t


#ifndef UTILS_H
#define UTILS_H


void utf16_check_bom(uint16_t **src_p, size_t *size_p);
size_t utf16_size(const uint16_t *src, size_t src_size, bool *eos);
text utf16_to_utf8(uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool);
text utf16_to_utf8_nobom(const uint16_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool);

void utf8_check_bom(const uint8_t **src_p, size_t *size_p);
size_t utf8_size(const uint8_t *src, size_t src_size, bool *eos);
const uint16_t* utf8_to_utf16(const uint8_t *src, size_t src_size, size_t *dst_size, bool *eos, ScratchPool *pool);


static const size_t prim_esize[8] = {1, 1, 2, 2, 4, 8, 4, 8};

#define NEW_PRIM_ARRAY(base, env, size, out)                  \
switch (base) {                                               \
    case 0: out = (*env)->NewBooleanArray(env, size); break;  \
    case 1: out = (*env)->NewByteArray   (env, size); break;  \
    case 2: out = (*env)->NewCharArray   (env, size); break;  \
    case 3: out = (*env)->NewShortArray  (env, size); break;  \
    case 4: out = (*env)->NewIntArray    (env, size); break;  \
    case 5: out = (*env)->NewLongArray   (env, size); break;  \
    case 6: out = (*env)->NewFloatArray  (env, size); break;  \
    case 7: out = (*env)->NewDoubleArray (env, size); break;  \
}

#define GET_ARRAY_REGION(base, env, arr, start, len, buf)                                                   \
switch (base) {                                                                                             \
    case 0: (*env)->GetBooleanArrayRegion(env, (jbooleanArray)(arr), start, len, (jboolean*)(buf)); break;  \
    case 1: (*env)->GetByteArrayRegion   (env, (jbyteArray)   (arr), start, len, (jbyte*)(buf));    break;  \
    case 2: (*env)->GetCharArrayRegion   (env, (jcharArray)   (arr), start, len, (jchar*)(buf));    break;  \
    case 3: (*env)->GetShortArrayRegion  (env, (jshortArray)  (arr), start, len, (jshort*)(buf));   break;  \
    case 4: (*env)->GetIntArrayRegion    (env, (jintArray)    (arr), start, len, (jint*)(buf));     break;  \
    case 5: (*env)->GetLongArrayRegion   (env, (jlongArray)   (arr), start, len, (jlong*)(buf));    break;  \
    case 6: (*env)->GetFloatArrayRegion  (env, (jfloatArray)  (arr), start, len, (jfloat*)(buf));   break;  \
    case 7: (*env)->GetDoubleArrayRegion (env, (jdoubleArray) (arr), start, len, (jdouble*)(buf));  break;  \
}

#define SET_ARRAY_REGION(base, env, arr, start, len, buf)                                                   \
switch (base) {                                                                                             \
    case 0: (*env)->SetBooleanArrayRegion(env, (jbooleanArray)(arr), start, len, (jboolean*)(buf)); break;  \
    case 1: (*env)->SetByteArrayRegion   (env, (jbyteArray)   (arr), start, len, (jbyte*)(buf));    break;  \
    case 2: (*env)->SetCharArrayRegion   (env, (jcharArray)   (arr), start, len, (jchar*)(buf));    break;  \
    case 3: (*env)->SetShortArrayRegion  (env, (jshortArray)  (arr), start, len, (jshort*)(buf));   break;  \
    case 4: (*env)->SetIntArrayRegion    (env, (jintArray)    (arr), start, len, (jint*)(buf));     break;  \
    case 5: (*env)->SetLongArrayRegion   (env, (jlongArray)   (arr), start, len, (jlong*)(buf));    break;  \
    case 6: (*env)->SetFloatArrayRegion  (env, (jfloatArray)  (arr), start, len, (jfloat*)(buf));   break;  \
    case 7: (*env)->SetDoubleArrayRegion (env, (jdoubleArray) (arr), start, len, (jdouble*)(buf));  break;  \
}


#endif // UTILS_H
