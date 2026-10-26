#include "mem_pool.h"
#include "common.h"
#include "utils.h"
#include "context.h"
#include "jni.h"

#include <stdio.h> // printf
#include <stdlib.h> // malloc
#include <unistd.h> // read, write, close
#include <pthread.h> // pthread_create, pthread_detach
#include <sys/socket.h> // socket, AF_UNIX, SOCK_STREAM, bind, listen, accept
#include <sys/un.h> // struct sockaddr_un


size_t get_shorty_size(text src) {
    size_t src_pos = 0, dst_pos = 0;
    while (true) {
        const char letter = src[src_pos++];
        switch (letter) {
        case ')':
            dst_pos++; // null term
            return dst_pos;
        case 0:
            fprintf(stderr, "Error: unexpected end of string while parsing signature\n");
            return (size_t) -1;
        case 'L':
            while (src[src_pos] != ';' && src[src_pos] != 0 && src[src_pos] != ')')
                src_pos++;
            if (src[src_pos] == ';')
                src_pos++;
            dst_pos++; // 'L'
            break;
        case 'Z': case 'B': case 'C': case 'S':
        case 'I': case 'J': case 'F': case 'D':
            dst_pos++; // primitive or 'L'
            break;
        }
    }
}

text to_shorty(text src, char *dst) {
    size_t src_pos = 0, dst_pos = 0;
    bool is_arr = false;

    while (true) {
        const char letter = src[src_pos++];
        switch (letter) {
        case ')':
            dst[dst_pos] = 0;
            return src + src_pos;
        case '[':
            is_arr = true;
            break;
        case 'L':
            while (src[src_pos] != ';' && src[src_pos] != 0 && src[src_pos] != ')')
                src_pos++;
            if (src[src_pos] == ';')
                src_pos++;
            dst[dst_pos++] = 'L';
            is_arr = false;
            break;
        case 'Z': case 'B': case 'C': case 'S':
        case 'I': case 'J': case 'F': case 'D':
            if (is_arr) {
                dst[dst_pos++] = 'L';
                is_arr = false;
            } else
                dst[dst_pos++] = letter;
            break;
        }
    }
}

char get_return_type(text src, bool *eos) {
    size_t pos = 0;
    while (src[pos] == '[')
        pos++;
    if (src[pos] == 0) {
        *eos = true;
        fprintf(stderr, "Error: unexpected end of string while parsing signature\n");
    }
    return src[pos];
}

static const uint8_t TYPE_KIND[256] = {
    ['L'] = 0, ['Z'] = 1, ['B'] = 2, ['C'] = 3, ['S'] = 4,
    ['I'] = 5, ['J'] = 6, ['F'] = 7, ['D'] = 8, ['V'] = 255,
};


uint8_t read_byte(int fd, bool *eos) {
    uint8_t byte;
    if (read(fd, &byte, 1) <= 0)
        *eos = true;
    return byte;
}
int read_int(int fd, bool *eos) {
    int number;
    if (read(fd, &number, 4) <= 0)
        *eos = true;
    return number;
}
void* read_ptr(int fd, bool *eos) {
    size_t ptr;
    if (read(fd, &ptr, sizeof(size_t)) <= 0)
        *eos = true;
    return (void*) ptr;
}
int read_uleb128(int fd, bool *eos) {
    int number = 0, shift = 0;
    uint8_t byte = 0;
    do {
        if (read(fd, &byte, 1) <= 0) {
            *eos = true;
            break;
        }
        number |= (byte & 0x7f) << shift;
        shift += 7;
    } while (byte & 0x80);
    return number;
}
jlong read_uleb128L(int fd, bool *eos) {
    jlong number = 0, shift = 0;
    uint8_t byte = 0;
    do {
        if (read(fd, &byte, 1) <= 0) {
            *eos = true;
            break;
        }
        number |= (byte & 0x7f) << shift;
        shift += 7;
    } while (byte & 0x80);
    return number;
}
int read_sleb128(int fd, bool *eos) {
    int number = read_uleb128(fd, eos);
    return (number >> 1) ^ (number & 1 ? -1 : 0); // zigzag
}
jlong read_sleb128L(int fd, bool *eos) {
    jlong number = read_uleb128L(fd, eos);
    return (number >> 1) ^ (number & 1 ? -1 : 0); // zigzag
}
char* read_str(int fd, bool *eos, ScratchPool *pool) {
    int size = read_uleb128(fd, eos);
    if (*eos)
        return NULL;
    char* buffer = (char*) pool_alloc(pool, size+1);
    if (!buffer || read(fd, buffer, size) <= 0) {
        *eos = true;
        return NULL;
    }
    buffer[size] = 0;
    return buffer;
}
char* read_str_with_size(int fd, bool *eos, int *size_p, ScratchPool *pool) {
    int size = read_uleb128(fd, eos);
    if (*eos)
        return NULL;
    char* buffer = (char*) pool_alloc(pool, size+1);
    if (!buffer || read(fd, buffer, size) <= 0) {
        *eos = true;
        return NULL;
    }
    buffer[size] = 0;
    *size_p = size;
    return buffer;
}
#define READ_VALUE(fd, kind, out) do {                                                \
    uint8_t _b; bool _e = false;                                                      \
    switch (kind) {                                                                   \
        case 0: out.l = (jobject) read_ptr(fd, &_e);     if (_e) return true; break;  \
        case 1: if (read(fd, &_b, 1) <= 0) return true; out.z = (_b != 0);    break;  \
        case 2: if (read(fd, &_b, 1) <= 0) return true; out.b = (jbyte)_b;    break;  \
        case 3: out.c = (jchar)  read_uleb128(fd, &_e);  if (_e) return true; break;  \
        case 4: out.s = (jshort) read_sleb128(fd, &_e);  if (_e) return true; break;  \
        case 5: out.i = (jint)   read_sleb128(fd, &_e);  if (_e) return true; break;  \
        case 6: out.j =          read_sleb128L(fd, &_e); if (_e) return true; break;  \
        case 7: if (read(fd, &out.f, 4) <= 0) return true;                    break;  \
        case 8: if (read(fd, &out.d, 8) <= 0) return true;                    break;  \
        default: return true;                                                         \
    }                                                                                 \
} while (0);
bool read_args(int fd, text shorty, jvalue *result) {
    for (int pos = 0; ; pos++) {
        uint8_t type = shorty[pos];
        if (type == 0)
            return false;
        READ_VALUE(fd, TYPE_KIND[type], result[pos])
    }
}

void write_byte(int fd, uint8_t val) {
    write(fd, &val, 1);
}
void write_int(int fd, int val) {
    write(fd, &val, 4);
}
void write_ptr(int fd, void* ptr) {
    size_t val = (size_t) ptr;
    write(fd, &val, sizeof(size_t));
}
void write_uleb128(int fd, int val) {
    do {
        uint8_t byte = val & 0x7f;
        val >>= 7;
        if (val)
            byte |= 0x80;
        write(fd, &byte, 1);
    } while (val);
}
void write_uleb128L(int fd, jlong val) {
    do {
        uint8_t byte = val & 0x7f;
        val >>= 7;
        if (val)
            byte |= 0x80;
        write(fd, &byte, 1);
    } while (val);
}
void write_sleb128(int fd, int val) {
    int u = (val << 1) ^ -(val < 0);
    write_uleb128(fd, u);
}
void write_sleb128L(int fd, jlong val) {
    jlong u = (val << 1) ^ -(val < 0);
    write_uleb128L(fd, u);
}
void write_str_with_size(int fd, text str, size_t size) {
    write_uleb128(fd, size);
    write(fd, str, size);
}
void write_str(int fd, text str) {
    write_str_with_size(fd, str, strlen(str));
}
#define WRITE_VALUE(fd, kind, value) do {                                  \
    uint8_t _b;                                                            \
    switch (kind) {                                                        \
        case 0: write_ptr(fd, (value).l); break;                           \
        case 1: _b = (uint8_t)((value).z != 0); write(fd, &_b, 1); break;  \
        case 2: _b = (uint8_t)((value).b);      write(fd, &_b, 1); break;  \
        case 3: write_uleb128(fd, (value).c);                      break;  \
        case 4: write_sleb128(fd, (value).s);                      break;  \
        case 5: write_sleb128(fd, (value).i);                      break;  \
        case 6: write_sleb128L(fd, (value).j);                     break;  \
        case 7: write(fd, &(value).f, 4);                          break;  \
        case 8: write(fd, &(value).d, 8);                          break;  \
    }                                                                      \
} while (0);


typedef struct jmethod {
    jmethodID ID;
    jclass clazz;
    char ret_t;
    uint8_t ret_k;
    char shorty[]; // flexible array member
} jmethod;

jmethod* jmethod_init(jmethodID id, jclass clazz, text signature, bool *eos, BlockPool *pool) {
    size_t shorty_size = get_shorty_size(signature);
    if (shorty_size == (size_t) -1) {
        *eos = true;
        return NULL;
    }

    jmethod* method = (jmethod*) block_pool_alloc(pool, sizeof(jmethod) + shorty_size);
    if (method == NULL) {
        fprintf(stderr, "jmethod pool alloc\n");
        *eos = true; return NULL;
    }

    method->ID = id;
    method->clazz = clazz;
    text ret_s = to_shorty(signature, method->shorty);
    method->ret_t = get_return_type(ret_s, eos);
    method->ret_k = TYPE_KIND[method->ret_t];

    return method;
}


typedef struct jfield {
    jfieldID ID;
    char type;
    uint8_t kind;
} jfield;

jfield* jfield_init(jfieldID id, text type_s, bool *eos, BlockPool *pool) {
    jfield* field = (jfield*) block_pool_alloc(pool, sizeof(jfield));
    if (field == NULL) {
        fprintf(stderr, "jfield pool alloc\n");
        *eos = true; return NULL;
    }

    field->ID = id;
    field->type = get_return_type(type_s, eos);
    field->kind = TYPE_KIND[field->type];

    return field;
}


bool _check_exception(int fd, JNIEnv* env, bool send_ok) {
    jthrowable exc = (*env)->ExceptionOccurred(env);
    if (exc == NULL) {
        if (send_ok)
            write_uleb128(fd, 0); // empty exception string
        return true;
    }

    jclass excClass = (*env)->GetObjectClass(env, exc);
    text fallback = NULL;
    jstring msg = NULL;
    text utf = NULL;

    if (excClass) {
        jmethodID toString = (*env)->GetMethodID(env, excClass, "toString", "()Ljava/lang/String;");
        if (toString) {
            msg = (jstring)(*env)->CallObjectMethod(env, exc, toString);
            if (msg) {
                utf = (*env)->GetStringUTFChars(env, msg, NULL);
                fallback = utf ? utf : "Exception occurred, but cannot get UTF-8 string";
            } else
                fallback = "Exception occurred, but toString() returned NULL (or raised exception)";
        } else
            fallback = "Exception occurred, but toString() not found";
        (*env)->DeleteLocalRef(env, excClass);
    } else
        fallback = "Exception occurred, but cannot retrieve details";
    (*env)->DeleteLocalRef(env, exc);

    write_str(fd, fallback);

    if (msg) {
        if (utf)
            (*env)->ReleaseStringUTFChars(env, msg, utf);
        (*env)->DeleteLocalRef(env, msg);
    }

    (*env)->ExceptionClear(env);
    return false;
}
bool check_exception(int fd, JNIEnv* env) {
    return _check_exception(fd, env, /*send_ok=*/true);
}

bool handle_command(int fd, ClientCtx *ctx) {
    bool eos = false;
    jint error = JNI_EINVAL;  /* invalid arguments */
    uint8_t kind = read_byte(fd, &eos);
    if (eos)
        return eos;
    // printf("(S) kind: %d\n", kind);

    JNIEnv* env = ctx->env;
    ScratchPool* scratch_mem = ctx->scratch_mem;
    char *buffer, *buffer2;
    jvalue* args_buffer = ctx->args_buffer;

    jclass clazz;
    jmethod* method; jmethodID method_id;
    jfield* field; jfieldID field_id;
    jobject object;
    jvalue value;
    jstring string; jsize size;

    jarray array; jobjectArray object_arr;
    jsize start, len, span;
    jint end, step, last;
    void* region;
    size_t esize;

    switch (kind) {
        case 0: {
            if (!ctx->vm) {
                error = JNI_CreateJavaVM(&ctx->vm, (void **) &ctx->env, ctx->args);
                if (error == JNI_OK)
                    error = init_reflection_cache(ctx);
                ctx->own_vm = (error == JNI_OK && ctx->vm);
            }
            write_sleb128(fd, error);
            break; }
        case 1:
            error = JNI_GetCreatedJavaVMs(ctx->vm_arr, 16, &ctx->vm_count);
            write_sleb128(fd, error);
            if (error == JNI_OK)
                write_uleb128(fd, ctx->vm_count);
            break;
        case 2: {
            uint8_t index = read_byte(fd, &eos);
            if (eos)
                return eos;
            if (!ctx->vm && index < 16 && index < ctx->vm_count) {
                ctx->vm = ctx->vm_arr[index];
                ctx->own_vm = false;
                error = JNI_OK;
            }
            write_sleb128(fd, error);
            break; }
        case 3: {
            JavaVMAttachArgs* args = NULL;
            if (ctx->vm) {
                error = (*ctx->vm)->AttachCurrentThread(ctx->vm, (void **) &ctx->env, args);
                if (error == JNI_OK)
                    error = init_reflection_cache(ctx);
            }
            write_sleb128(fd, error);
            break; }
        case 4:
            if (ctx->vm) {
                error = (*ctx->vm)->DetachCurrentThread(ctx->vm);
                // if (ctx->own_vm)
                //     (*ctx->vm)->DestroyJavaVM(ctx->vm);
                ctx->vm = NULL;
                ctx->own_vm = false;
            }
            write_sleb128(fd, error);
            break;

        case 5: {
            jint version = (*env)->GetVersion(env);
            short major = version >> 16;
            short minor = version & 0xffff;
            write_uleb128(fd, major);
            write_uleb128(fd, minor);
            break; }

     // case 6: DefineClass...
        case 7:
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            clazz = (*env)->FindClass(env, buffer);
            if (check_exception(fd, env))
                write_ptr(fd, clazz);
            break;

        case 8:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            bool is_ctor = read_byte(fd, &eos);
            if (eos) return eos;

            method_id = (*env)->FromReflectedMethod(env, object);
            if (_check_exception(fd, env, /*send_ok=*/false)) {
                // clazz = (*env)->GetObjectClass(env, object);
                clazz = (jclass)(*env)->CallObjectMethod(env, object, ctx->methodGetDeclaringClass);
                jint modifiers = (*env)->CallIntMethod(env, object, ctx->methodGetModifiers);
                if (_check_exception(fd, env, /*send_ok=*/false)) {
                    jstring jname; text name;
                    if (!is_ctor) {
                        jname = (jstring)(*env)->CallObjectMethod(env, object, ctx->methodGetName);
                        name = jname ? (*env)->GetStringUTFChars(env, jname, NULL) : NULL;
                    }
                    if (_check_exception(fd, env, /*send_ok=*/false)) {
                        buffer = build_method_signature(ctx, object, is_ctor);
                        if (buffer == NULL) {
                           if (_check_exception(fd, env, /*send_ok=*/false))
                               write_str(fd, "signature is <null>");
                        } else if (check_exception(fd, env)) {
                            method = jmethod_init(method_id, clazz, buffer, &eos, ctx->block_mem);
                            if (eos) return eos;
                            write_ptr(fd, clazz);
                            if (!is_ctor)
                                write_str(fd, name);
                            write_str(fd, buffer);
                            write_uleb128(fd, modifiers);
                            write_ptr(fd, method);
                        }
                    }
                    if (!is_ctor && jname) {
                        if (name) (*env)->ReleaseStringUTFChars(env, jname, name);
                        (*env)->DeleteLocalRef(env, jname);
                    }
                }
            }
            break;

        case 9:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
        
            field_id = (*env)->FromReflectedField(env, object);
            if (_check_exception(fd, env, /*send_ok=*/false)) {
                clazz = (jclass)(*env)->CallObjectMethod(env, object, ctx->fieldGetDeclaringClass);
                jint modifiers = (*env)->CallIntMethod(env, object, ctx->fieldGetModifiers);
                if (_check_exception(fd, env, /*send_ok=*/false)) {
                    jstring jname = (jstring)(*env)->CallObjectMethod(env, object, ctx->fieldGetName);
                    text name = jname ? (*env)->GetStringUTFChars(env, jname, NULL) : NULL;
                    if (_check_exception(fd, env, /*send_ok=*/false)) {
                        jobject type_cls = (*env)->CallObjectMethod(env, object, ctx->fieldGetType);
                        if (_check_exception(fd, env, /*send_ok=*/false)) {
                            char* buf = (char*) ctx->scratch_mem->buffer;
                            size_t cap = sizeof(ctx->scratch_mem->buffer);
                            size_t pos = append_class_type(ctx, type_cls, buf, 0, cap);
                            if (pos == (size_t)-1) {
                                if (_check_exception(fd, env, /*send_ok=*/false))
                                    write_str(fd, "type is <null>");
                            } else if (check_exception(fd, env)) {
                                buf[pos] = 0;
                                field = jfield_init(field_id, buf, &eos, ctx->block_mem);
                                if (eos) return eos;
                                write_ptr(fd, clazz);
                                write_str(fd, name);
                                write_str(fd, buf);
                                write_uleb128(fd, modifiers);
                                write_ptr(fd, field);
                            }
                            (*env)->DeleteLocalRef(env, type_cls);
                        }
                        if (jname) {
                            if (name) (*env)->ReleaseStringUTFChars(env, jname, name);
                            (*env)->DeleteLocalRef(env, jname);
                        }
                    }
                }
            }
            break;

        // 10..28

        case 29:
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            if (read_args(fd, method->shorty, args_buffer))
                return true;

            object = (*env)->NewObjectA(env, method->clazz, method->ID, args_buffer);
            if (check_exception(fd, env))
                write_ptr(fd, object);
            break;

        // 30..31

        case 32:
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            method_id = (*env)->GetMethodID(env, clazz, buffer, buffer2);
            if (check_exception(fd, env)) {
                method = jmethod_init(method_id, clazz, buffer2, &eos, ctx->block_mem);
                if (eos) return eos;
                write_ptr(fd, method);
            }
            break;

        case 33:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            if (read_args(fd, method->shorty, args_buffer))
                return true;

            switch (method->ret_t) {
                case 'L': value = (jvalue) (*env)->CallObjectMethodA(env, object, method->ID, args_buffer); break;
                case 'Z': value = (jvalue) (*env)->CallBooleanMethodA(env, object, method->ID, args_buffer); break;
                case 'B': value = (jvalue) (*env)->CallByteMethodA(env, object, method->ID, args_buffer); break;
                case 'C': value = (jvalue) (*env)->CallCharMethodA(env, object, method->ID, args_buffer); break;
                case 'S': value = (jvalue) (*env)->CallShortMethodA(env, object, method->ID, args_buffer); break;
                case 'I': value = (jvalue) (*env)->CallIntMethodA(env, object, method->ID, args_buffer); break;
                case 'J': value = (jvalue) (*env)->CallLongMethodA(env, object, method->ID, args_buffer); break;
                case 'F': value = (jvalue) (*env)->CallFloatMethodA(env, object, method->ID, args_buffer); break;
                case 'D': value = (jvalue) (*env)->CallDoubleMethodA(env, object, method->ID, args_buffer); break;
                case 'V': (*env)->CallVoidMethodA(env, object, method->ID, args_buffer); break;
            }
            if (check_exception(fd, env) && method->ret_t != 'V')
                WRITE_VALUE(fd, method->ret_k, value)
            break;
        case 34 ... 42:
            fprintf(stderr, "Warning: use 33 (Call<type>MethodA) instead of 34..42\n");
            return true; // eos

        case 43:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            if (read_args(fd, method->shorty, args_buffer))
                return true;

            switch (method->ret_t) {
                case 'L': value = (jvalue) (*env)->CallNonvirtualObjectMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'Z': value = (jvalue) (*env)->CallNonvirtualBooleanMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'B': value = (jvalue) (*env)->CallNonvirtualByteMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'C': value = (jvalue) (*env)->CallNonvirtualCharMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'S': value = (jvalue) (*env)->CallNonvirtualShortMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'I': value = (jvalue) (*env)->CallNonvirtualIntMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'J': value = (jvalue) (*env)->CallNonvirtualLongMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'F': value = (jvalue) (*env)->CallNonvirtualFloatMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'D': value = (jvalue) (*env)->CallNonvirtualDoubleMethodA(env, object, method->clazz, method->ID, args_buffer); break;
                case 'V': (*env)->CallNonvirtualVoidMethodA(env, object, method->clazz, method->ID, args_buffer); break;
            }
            if (check_exception(fd, env) && method->ret_t != 'V')
                WRITE_VALUE(fd, method->ret_k, value)
            break;
        case 44 ... 52:
            fprintf(stderr, "Warning: use 43 (CallNonvirtual<type>MethodA) instead of 44..52\n");
            return true; // eos

        case 53: 
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            field_id = (*env)->GetFieldID(env, clazz, buffer, buffer2);
            if (check_exception(fd, env)) {
                field = jfield_init(field_id, buffer2, &eos, ctx->block_mem);
                if (eos) return eos;
                write_ptr(fd, field);
            }
            break;

        case 54:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            field = (jfield*) read_ptr(fd, &eos);
            if (eos) return eos;

            switch (field->type) {
                case 'L': value = (jvalue) (*env)->GetObjectField(env, object, field->ID); break;
                case 'Z': value = (jvalue) (*env)->GetBooleanField(env, object, field->ID); break;
                case 'B': value = (jvalue) (*env)->GetByteField(env, object, field->ID); break;
                case 'C': value = (jvalue) (*env)->GetCharField(env, object, field->ID); break;
                case 'S': value = (jvalue) (*env)->GetShortField(env, object, field->ID); break;
                case 'I': value = (jvalue) (*env)->GetIntField(env, object, field->ID); break;
                case 'J': value = (jvalue) (*env)->GetLongField(env, object, field->ID); break;
                case 'F': value = (jvalue) (*env)->GetFloatField(env, object, field->ID); break;
                case 'D': value = (jvalue) (*env)->GetDoubleField(env, object, field->ID); break;
            }
            if (check_exception(fd, env))
                WRITE_VALUE(fd, field->kind, value)
            break;
        case 55 ... 62:
            fprintf(stderr, "Warning: use 54 (Get<type>Field) instead of 55..62\n");
            return true; // eos

        case 63:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            field = (jfield*) read_ptr(fd, &eos);
            if (eos) return eos;
            READ_VALUE(fd, field->kind, value)

            switch (field->type) {
                case 'L': (*env)->SetObjectField(env, object, field->ID, value.l); break;
                case 'Z': (*env)->SetBooleanField(env, object, field->ID, value.z); break;
                case 'B': (*env)->SetByteField(env, object, field->ID, value.b); break;
                case 'C': (*env)->SetCharField(env, object, field->ID, value.c); break;
                case 'S': (*env)->SetShortField(env, object, field->ID, value.s); break;
                case 'I': (*env)->SetIntField(env, object, field->ID, value.i); break;
                case 'J': (*env)->SetLongField(env, object, field->ID, value.j); break;
                case 'F': (*env)->SetFloatField(env, object, field->ID, value.f); break;
                case 'D': (*env)->SetDoubleField(env, object, field->ID, value.d); break;
            }
            check_exception(fd, env);
            break;
        case 64 ... 71:
            fprintf(stderr, "Warning: use 63 (Set<type>Field) instead of 64..71\n");
            return true; // eos

        case 72:
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            method_id = (*env)->GetStaticMethodID(env, clazz, buffer, buffer2);
            if (check_exception(fd, env)) {
                method = jmethod_init(method_id, clazz, buffer2, &eos, ctx->block_mem);
                if (eos) return eos;
                write_ptr(fd, method);
            }
            break;

        case 73:
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            if (read_args(fd, method->shorty, args_buffer))
                return true;

            switch (method->ret_t) {
                case 'L': value = (jvalue) (*env)->CallStaticObjectMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'Z': value = (jvalue) (*env)->CallStaticBooleanMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'B': value = (jvalue) (*env)->CallStaticByteMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'C': value = (jvalue) (*env)->CallStaticCharMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'S': value = (jvalue) (*env)->CallStaticShortMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'I': value = (jvalue) (*env)->CallStaticIntMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'J': value = (jvalue) (*env)->CallStaticLongMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'F': value = (jvalue) (*env)->CallStaticFloatMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'D': value = (jvalue) (*env)->CallStaticDoubleMethodA(env, method->clazz, method->ID, args_buffer); break;
                case 'V': (*env)->CallStaticVoidMethodA(env, method->clazz, method->ID, args_buffer); break;
            }
            if (check_exception(fd, env) && method->ret_t != 'V')
                WRITE_VALUE(fd, method->ret_k, value)
            break;
        case 74 ... 82:
            fprintf(stderr, "Warning: use 73 (CallStatic<type>MethodA) instead of 74..82\n");
            return true; // eos

        case 83: 
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            field_id = (*env)->GetStaticFieldID(env, clazz, buffer, buffer2);
            if (check_exception(fd, env)) {
                field = jfield_init(field_id, buffer2, &eos, ctx->block_mem);
                if (eos) return eos;
                write_ptr(fd, field);
            }
            break;

        case 84:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            field = (jfield*) read_ptr(fd, &eos);
            if (eos) return eos;

            switch (field->type) {
                case 'L': value = (jvalue) (*env)->GetStaticObjectField(env, object, field->ID); break;
                case 'Z': value = (jvalue) (*env)->GetStaticBooleanField(env, object, field->ID); break;
                case 'B': value = (jvalue) (*env)->GetStaticByteField(env, object, field->ID); break;
                case 'C': value = (jvalue) (*env)->GetStaticCharField(env, object, field->ID); break;
                case 'S': value = (jvalue) (*env)->GetStaticShortField(env, object, field->ID); break;
                case 'I': value = (jvalue) (*env)->GetStaticIntField(env, object, field->ID); break;
                case 'J': value = (jvalue) (*env)->GetStaticLongField(env, object, field->ID); break;
                case 'F': value = (jvalue) (*env)->GetStaticFloatField(env, object, field->ID); break;
                case 'D': value = (jvalue) (*env)->GetStaticDoubleField(env, object, field->ID); break;
            }
            if (check_exception(fd, env))
                WRITE_VALUE(fd, field->kind, value)
            break;
        case 85 ... 92:
            fprintf(stderr, "Warning: use 84 (Get<type>Field) instead of 85..92\n");
            return true; // eos

        case 93:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            field = (jfield*) read_ptr(fd, &eos);
            if (eos) return eos;
            READ_VALUE(fd, field->kind, value)

            switch (field->type) {
                case 'L': (*env)->SetStaticObjectField(env, object, field->ID, value.l); break;
                case 'Z': (*env)->SetStaticBooleanField(env, object, field->ID, value.z); break;
                case 'B': (*env)->SetStaticByteField(env, object, field->ID, value.b); break;
                case 'C': (*env)->SetStaticCharField(env, object, field->ID, value.c); break;
                case 'S': (*env)->SetStaticShortField(env, object, field->ID, value.s); break;
                case 'I': (*env)->SetStaticIntField(env, object, field->ID, value.i); break;
                case 'J': (*env)->SetStaticLongField(env, object, field->ID, value.j); break;
                case 'F': (*env)->SetStaticFloatField(env, object, field->ID, value.f); break;
                case 'D': (*env)->SetStaticDoubleField(env, object, field->ID, value.d); break;
            }
            check_exception(fd, env);
            break;
        case 94 ... 101:
            fprintf(stderr, "Warning: use 93 (Set<type>Field) instead of 94..101\n");
            return true; // eos

        case 102: {
            int utf8_size;
            buffer = read_str_with_size(fd, &eos, &utf8_size, scratch_mem);
            if (eos) return eos;

            size_t utf16_size;
            const jchar* utf16 = utf8_to_utf16((uint8_t*) buffer, utf8_size, &utf16_size, &eos, scratch_mem);
            if (eos) return eos;

            object = (*env)->NewString(env, utf16, (jsize) utf16_size);
            if (check_exception(fd, env))
                write_ptr(fd, object);
            break; }
        case 103:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            size = (*env)->GetStringLength(env, string);
            if (check_exception(fd, env))
                write_uleb128(fd, size);
            break;
        case 104:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            size = (*env)->GetStringLength(env, string);
            if (_check_exception(fd, env, /*send_ok=*/false)) {
                const jchar* char_str = (*env)->GetStringChars(env, string, /*isCopy=*/NULL);
                if (check_exception(fd, env)) {
                    size_t utf8_size;
                    text utf8 = utf16_to_utf8_nobom(char_str, (size_t) size, &utf8_size, &eos, scratch_mem);
                    if (char_str)
                        (*env)->ReleaseStringChars(env, string, char_str);
                    if (eos) return eos;
                    write_str_with_size(fd, utf8, utf8_size);
                }
            }
            break;
        case 105:
            fprintf(stderr, "Warning: kind 105 (ReleaseStringChars) is deprecated and not implemented\n");
            return true; // eos

        // MUTF8 должен обрабатывать на стороне клиента, как массив байтов.
        // Для работы с UTF8 лучше всего использовать "NewString" и "GetStringChars" без "UTF"-суффикса
        case 106:
            buffer = read_str(fd, &eos, scratch_mem);
            if (eos) return eos;

            object = (*env)->NewStringUTF(env, buffer);
            if (check_exception(fd, env))
                write_ptr(fd, object);
            break;
        case 107:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            size = (*env)->GetStringUTFLength(env, string);
            if (check_exception(fd, env))
                write_uleb128(fd, size);
            break;
        case 108:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            text mutf8 = (*env)->GetStringUTFChars(env, string, /*isCopy=*/NULL);
            if (check_exception(fd, env)) {
                write_str(fd, mutf8);
                (*env)->ReleaseStringUTFChars(env, string, mutf8);
            }
            break;
        case 109:
            fprintf(stderr, "Warning: kind 109 (ReleaseStringUTFChars) is deprecated and not implemented\n");
            return true; // eos

        case 110:
            array = (jarray) read_ptr(fd, &eos);
            if (eos) return eos;

            size = (*env)->GetArrayLength(env, array);
            if (check_exception(fd, env))
                write_uleb128(fd, size);
            break;

        case 111:
            size = read_uleb128(fd, &eos);
            if (eos) return eos;
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;

            array = (*env)->NewObjectArray(env, /*len=*/size, clazz, /*init=*/object);
            if (check_exception(fd, env))
                write_ptr(fd, array);
            break;

        case 112:
            object_arr = (jobjectArray) read_ptr(fd, &eos);
            if (eos) return eos;
            size = read_sleb128(fd, &eos);
            if (eos) return eos;

            if (size < 0) {
                jsize arr_size = (*env)->GetArrayLength(env, (jarray) object_arr);
                if (!_check_exception(fd, env, /*send_ok=*/false))
                    break;
                size += arr_size;
            }

            object = (*env)->GetObjectArrayElement(env, object_arr, /*index=*/size);
            if (check_exception(fd, env))
                write_ptr(fd, object);
            break;

        case 113:
            object_arr = (jobjectArray) read_ptr(fd, &eos);
            if (eos) return eos;
            size = read_sleb128(fd, &eos);
            if (eos) return eos;
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;

            if (size < 0) {
                jsize arr_size = (*env)->GetArrayLength(env, (jarray) object_arr);
                if (!_check_exception(fd, env, /*send_ok=*/false))
                    break;
                size += arr_size;
            }

            (*env)->SetObjectArrayElement(env, object_arr, /*index=*/size, /*val=*/ object);
            check_exception(fd, env);
            break;

        case 114 ... 121:
            size = read_uleb128(fd, &eos);
            if (eos) return eos;

            NEW_PRIM_ARRAY(kind - 114, env, size, array);
            if (check_exception(fd, env))
                write_ptr(fd, array);
            break;

        case 122 ... 129: // Get<type>ArrayElement: base = kind - 122 (0..7)
            array = (jarray) read_ptr(fd, &eos);
            if (eos) return eos;
            start = read_uleb128(fd, &eos);
            if (eos) return eos;

            GET_ARRAY_REGION(kind - 122, env, array, start, 1, &value);
            if (check_exception(fd, env))
                WRITE_VALUE(fd, 1 + (kind - 122), value); // kind+1: Z=1..D=8
            break;

        case 130 ... 137: // Set<type>ArrayElement: base = kind - 130 (0..7)
            array = (jarray) read_ptr(fd, &eos);
            if (eos) return eos;
            start = read_uleb128(fd, &eos);
            if (eos) return eos;

            READ_VALUE(fd, 1 + (kind - 130), value); // kind+1: Z=1..D=8
            SET_ARRAY_REGION(kind - 130, env, array, start, 1, &value);
            check_exception(fd, env);
            break;

        case 138 ... 145: // Get<type>ArraySlice: start, end, step -> len, data
            array = (jarray) read_ptr(fd, &eos);
            if (eos) return eos;
            start = read_sleb128(fd, &eos);
            if (eos) return eos;
            end = read_sleb128(fd, &eos);
            if (eos) return eos;
            step = read_sleb128(fd, &eos);
            if (eos) return eos;

            esize = prim_esize[kind - 138];  // base = 4 для int

            if (step == 1) {
                len = end - start;
                if (len <= 0) {
                    write_uleb128(fd, 0); // OK
                    write_uleb128(fd, 0); // len
                    break;
                }
                region = pool_alloc(ctx->scratch_mem, len * esize);
                if (!region)
                    return true;
                GET_ARRAY_REGION(kind - 138, env, array, start, len, region);
                if (!check_exception(fd, env))
                    break;
                write_uleb128(fd, len);
                write(fd, region, len * esize);
            } else if (step > 0) {
                len = (end - start + step - 1) / step;
                if (len <= 0) {
                    write_uleb128(fd, 0); // OK
                    write_uleb128(fd, 0); // len
                    break;
                }
                span = (len - 1) * step + 1;
                region = pool_alloc(ctx->scratch_mem, span * esize);
                if (!region)
                    return true;
                GET_ARRAY_REGION(kind - 138, env, array, start, span, region);
                if (!check_exception(fd, env))
                    break;
                write_uleb128(fd, len);
                for (jsize i = 0; i < span; i += step)
                    write(fd, (uint8_t*)region + i * esize, esize);
            } else if (step < 0) {
                len = (end - start + step + 1) / step;
                if (len <= 0) {
                    write_uleb128(fd, 0); // OK
                    write_uleb128(fd, 0); // len
                    break;
                }
                last = start + (len - 1) * step;
                span = start - last + 1;
                region = pool_alloc(ctx->scratch_mem, span * esize);
                if (!region)
                    return true;
                GET_ARRAY_REGION(kind - 138, env, array, last, span, region);
                if (!check_exception(fd, env))
                    break;
                write_uleb128(fd, len);
                for (jsize i = span - 1; i >= 0; i += step)
                    write(fd, (uint8_t*)region + i * esize, esize);
            } else // step == 0
                eos = true;
            break;

        case 146 ... 153: // Set<type>ArraySlice: start, step, len, data
            array = (jarray) read_ptr(fd, &eos);
            if (eos) return eos;
            start = read_sleb128(fd, &eos);
            if (eos) return eos;
            step = read_sleb128(fd, &eos);
            if (eos) return eos;
            len = read_uleb128(fd, &eos);
            if (eos) return eos;

            esize = prim_esize[kind - 146];  // base = 4 для int

            if (len == 0)
                break;

            if (step == 1) {
                region = pool_alloc(ctx->scratch_mem, len * esize);
                if (!region)
                    return true;
                if (read(fd, region, len * esize) != len * esize)
                    return true;
                SET_ARRAY_REGION(kind - 146, env, array, start, len, region);
                check_exception(fd, env);
            } else if (step > 0) {
                span = (len - 1) * step + 1;
                region = pool_alloc(ctx->scratch_mem, span * esize);
                if (!region)
                    return true;
                GET_ARRAY_REGION(kind - 146, env, array, start, span, region);
                if (!_check_exception(fd, env, /*send_ok=*/false))
                    break;
                for (jsize i = 0; i < span; i += step)
                    if (read(fd, (uint8_t*)region + i * esize, esize) != esize)
                        return true;
                SET_ARRAY_REGION(kind - 146, env, array, start, span, region);
                check_exception(fd, env);
            } else {
                last = start + (len - 1) * step;
                span = start - last + 1;
                region = pool_alloc(ctx->scratch_mem, span * esize);
                if (!region)
                    return true;
                GET_ARRAY_REGION(kind - 146, env, array, last, span, region);
                if (!_check_exception(fd, env, /*send_ok=*/false))
                    break;
                for (jsize i = span - 1; i >= 0; i += step)
                    if (read(fd, (uint8_t*)region + i * esize, esize) != esize)
                        return true;
                SET_ARRAY_REGION(kind - 146, env, array, last, span, region);
                check_exception(fd, env);
            }
            break;

        // 154..170

        case 171:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;

            write_byte(fd, env ? (*env)->GetObjectRefType(env, object) : JNIInvalidRefType);
            break;

        // 172..173

        default:
            printf("unknown kind: %d\n", kind);
            eos = true;
    }
    return eos;
}

void* handle_client_thread(void* arg) {
    int client_fd = (int)(intptr_t) arg;

    JavaVMOption option = {
        .optionString = "-Djava.class.path=.",
        .extraInfo = NULL,
    };
    JavaVMInitArgs args = {
        .version = JNI_VERSION_1_6,
        .nOptions = 1,
        .options = &option,
        .ignoreUnrecognized = JNI_TRUE,
    };
    ScratchPool scratch_mem = pool_init();
    BlockPool block_mem = block_pool_init();
    jvalue args_buffer[256];
    ClientCtx ctx = {
        .vm = NULL, .env = NULL, .vm_count = 0,
        .args = &args, .own_vm = false,
        .scratch_mem = &scratch_mem, .block_mem = &block_mem,
        .args_buffer = args_buffer,
    };

    while (1)
        if (handle_command(client_fd, &ctx))
            break;
        pool_clear(&scratch_mem);

    pool_clear(&scratch_mem);
    block_pool_clear(&block_mem);

    JavaVM* vm = ctx.vm;
    if (vm) {
        jint err = (*vm)->DetachCurrentThread(vm);
        printf("detach error code: %d\n", err);
        /*if (ctx.own_vm) {
            err = (*vm)->DestroyJavaVM(vm);
            printf("destroy error code: %d\n", err);
        }*/
        // БАГ openjdk: нельзя создать вторую VM, даже если первая была разнесена в щепки!
        // Зато это фиксит противоречение, что и создать VM нельзя, и список VM пустой!
        // Т.е. получаем при создании VM ошибку "VM уже создана", а список VM говорит совершенно противоположное!
    }

    close(client_fd);
    return NULL;
}

void handle_client(int client_fd) {
    pthread_t thread;
    if (pthread_create(&thread, NULL, handle_client_thread, (void*)(intptr_t) client_fd) != 0) {
        perror("pthread_create (client)");
        close(client_fd);
    } else {
        pthread_detach(thread); // не ждём завершения потока
    }
}

void* socket_listener_thread(void* arg) {
    int server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return NULL;
    }

    text socket_path = "/data/data/com.termux/files/usr/tmp/jni.sock";
    unlink(socket_path);

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strcpy(addr.sun_path, socket_path);

    if (bind(server_fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
        perror("bind");
        close(server_fd);
        return NULL;
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        return NULL;
    }

    printf("Socket listener started!\n");

    while (1) {
        int client_fd = accept(server_fd, NULL, NULL);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }
        handle_client(client_fd);
    }

    close(server_fd);
    return NULL;
}

void init_socket_server() {
    pthread_t thread;
    if (pthread_create(&thread, NULL, socket_listener_thread, NULL) != 0) {
        perror("pthread_create (server)");
    } else {
        pthread_detach(thread);
        printf("Socket listener thread launched\n");
    }
}

/*__attribute__((constructor))
void init_lib() {
    init_socket_server();
}*/

int main() {
    printf("\n");
    init_socket_server();
    printf("Server is running. Use 'kill %d' or Ctrl+C to stop.\n", getpid());
    while (1)
        sleep(60);
    return 0; 
}
