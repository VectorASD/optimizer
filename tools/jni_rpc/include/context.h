#include "jni.h"
#include "utils.h" // bool, true, false


#ifndef CONTEXT_H
#define CONTEXT_H


typedef struct ClientCtx {
    JavaVM* vm;
    JNIEnv* env;
    JavaVM* vm_arr[16];
    int vm_count;
    JavaVMInitArgs* args;
    bool own_vm;
    ScratchPool* scratch_mem;
    BlockPool* block_mem;
    jvalue* args_buffer;

    // Кэш рефлексивных типов и методов
    jclass classClass; // java.lang.Class
    jclass methodClass; // java.lang.reflect.Method
    jmethodID classGetName;
    jmethodID classGetDeclaredMethods;
    jmethodID classGetMethods;
    jmethodID methodGetName;
    jmethodID methodGetDeclaringClass;
    jmethodID methodGetParameterTypes;
    jmethodID methodGetReturnType;
    jmethodID methodGetModifiers;
} ClientCtx;

int init_reflection_cache(ClientCtx* ctx);
size_t append_class_type(ClientCtx* ctx, jobject clazz, char* buf, size_t pos, size_t cap);
char* build_method_signature(ClientCtx* ctx, jobject method_obj, bool is_ctor);


#endif // CONTEXT_H
