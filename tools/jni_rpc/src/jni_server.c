#include <stdio.h>  // printf
#include <stdlib.h>  // malloc
#include <unistd.h>  // read, write, close
#include <pthread.h>  // pthread_create, pthread_detach
#include <sys/socket.h>  // socket, AF_UNIX, SOCK_STREAM, bind, listen, accept
#include <sys/un.h>  // struct sockaddr_un

#include <jni.h>


typedef int bool;
#define true 1
#define false 0
typedef const char* text;

char get_return_type(text src) {
    size_t pos = 0;
    while (src[pos] == '[')
        pos++;
    if (src[pos] == 0)
        fprintf(stderr, "Error: unexpected end of string while parsing signature\n");
    return src[pos];
}

size_t to_shorty(text src, char *dst, char *ret_t) {
    size_t src_pos = 0, dst_pos = 0;
    bool is_arr = false;
    while (true) {
        const char letter = src[src_pos++];
        switch (letter) {
        case ')':
            dst[dst_pos++] = 0;
            *ret_t = get_return_type(src + src_pos);
            if (*ret_t == 0)
                return (size_t) -1;
            return dst_pos;
        case 0:
            fprintf(stderr, "Error: unexpected end of string while parsing signature\n");
            return (size_t) -1;
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
    return (number >> 1) ^ (number & 1 ? -1 : 0);  // zigzag
}
jlong read_sleb128L(int fd, bool *eos) {
    jlong number = read_uleb128L(fd, eos);
    return (number >> 1) ^ (number & 1 ? -1 : 0);  // zigzag
}
char* read_str(int fd, bool *eos, char *buffer) {
    int size = read_uleb128(fd, eos);
    if (*eos)
        return NULL;
    if (read(fd, buffer, size) <= 0) {
        *eos = true;
        return NULL;
    }
    buffer[size] = 0;
    return buffer + (size + 1);  // next buffer
}
jvalue void_jvalue = (jvalue)(jint) 0;
jvalue read_value(int fd, bool *eos, const char type) {
    uint8_t byte;
    int number;

    jlong long_v;
    jfloat float_v;
    jdouble double_v;
    jobject object_v;

    switch (type) {
    case 'Z':
        if (read(fd, &byte, 1) <= 0) { *eos = true; return void_jvalue; }
        return (jvalue)(jboolean) (byte != 0);
    case 'B':
        if (read(fd, &byte, 1) <= 0) { *eos = true; return void_jvalue; }
        return (jvalue)(jbyte) byte;
    case 'C':
        number = read_uleb128(fd, eos);
        if (*eos) return void_jvalue;
        return (jvalue)(jchar) number;
    case 'S':
        number = read_sleb128(fd, eos);
        if (*eos) return void_jvalue;
        return (jvalue)(jshort) number;
    case 'I':
        number = read_sleb128(fd, eos);
        if (*eos) return void_jvalue;
        return (jvalue)(jint) number;
    case 'J':
        long_v = read_sleb128L(fd, eos);
        if (*eos) return void_jvalue;
        return (jvalue) long_v;
    case 'F':
        if (read(fd, &float_v, 4) <= 0) { *eos = true; return void_jvalue; }
        return (jvalue) float_v;
    case 'D':
        if (read(fd, &double_v, 8) <= 0) { *eos = true; return void_jvalue; }
        return (jvalue) double_v;
    case 'L':
        object_v = (jobject) read_ptr(fd, eos);
        if (*eos) return void_jvalue;
        return (jvalue) object_v;
    }
    return void_jvalue;
}
void read_args(int fd, bool *eos, text sig, jvalue *result) {
    int pos = 0;
    uint8_t byte;
    int number;

    jlong long_v;
    jfloat float_v;
    jdouble double_v;
    jobject object_v;

    while (1) {
        const char type = sig[pos];
        if (type == 0)
            return;
        result[pos++] = read_value(fd, eos, type);
        if (*eos)
            return;
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
void write_str(int fd, text str) {
    size_t size = strlen(str);
    write_uleb128(fd, size);
    write(fd, str, size);
}
void write_value(int fd, const char kind, jvalue value) {
    switch (kind) {
        case 'L': write_ptr(fd, value.l); break;
        case 'Z': write(fd, &value.z, 1); break;
        case 'B': write(fd, &value.b, 1); break;
        case 'C': write_uleb128(fd, value.c); break;
        case 'S': write_sleb128(fd, value.s); break;
        case 'I': write_sleb128(fd, value.i); break;
        case 'J': write_sleb128L(fd, value.j); break;
        case 'F': write(fd, &value.f, 4); break;
        case 'D': write(fd, &value.d, 8); break;
    }
}


typedef struct ClientCtx {
    JavaVM* vm;
    JNIEnv* env;
    JavaVM* vm_arr[16];
    int vm_count;
    JavaVMInitArgs* args;
    bool own_vm;
    char *buffer;
    jvalue *args_buffer;
} ClientCtx;


typedef struct jmethod {
    jmethodID ID;
    char ret_t;
    char shorty[];  // flexible array member
} jmethod;

jmethod* jmethod_init(jmethodID id, text shorty, const size_t shorty_size, const char ret_t, bool *eos) {
    jmethod *method = (jmethod*) malloc(sizeof(jmethod) + shorty_size);
    if (method == NULL) {
        perror("jmethod malloc");
        *eos = true; return NULL;
    }
    // TODO: save "method" to memory bank + "free" after disconnection
    method->ID = id;
    method->ret_t = ret_t;
    memcpy(method->shorty, shorty, shorty_size);
    return method;
}


typedef struct jfield {
    jfieldID ID;
    char type;
} jfield;

jfield* jfield_init(jfieldID id, const char type, bool *eos) {
    jfield *field = (jfield*) malloc(sizeof(jfield));
    if (field == NULL) {
        perror("jmethod malloc");
        *eos = true; return NULL;
    }
    field->ID = id;
    field->type = type;
    return field;
}


bool check_exception(int fd, JNIEnv* env) {
    jthrowable exc = (*env)->ExceptionOccurred(env);
    if (exc == NULL) {
        write_uleb128(fd, 0);  // empty exception string
        return false;
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
    return true;
}

bool handle_command(int fd, ClientCtx *ctx) {
    bool eos = false;
    jint error = JNI_EINVAL;  /* invalid arguments */
    uint8_t kind = read_byte(fd, &eos);
    if (eos)
        return eos;
    printf("(S) kind: %d\n", kind);

    JNIEnv *env = ctx->env;
    char *buffer = ctx->buffer, *buffer2;
    jvalue *args_buffer = ctx->args_buffer;

    jclass clazz;
    jmethod *method;
    jfield *field;
    jobject object;
    jvalue value;
    jstring string; jsize size;

    switch (kind) {
        case 0: {
            if (!ctx->vm) {
                error = JNI_CreateJavaVM(&ctx->vm, (void **) &ctx->env, ctx->args);
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
            if (ctx->vm)
                error = (*ctx->vm)->AttachCurrentThread(ctx->vm, (void **) &ctx->env, args);
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
            read_str(fd, &eos, buffer);
            if (eos) return eos;

            clazz = (*env)->FindClass(env, buffer);
            if (!check_exception(fd, env))
                write_ptr(fd, clazz);
            break;

        // 8..28

        case 29:
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            read_args(fd, &eos, method->shorty, args_buffer);
            if (eos) return eos;

            object = (*env)->NewObjectA(env, clazz, method->ID, args_buffer);
            if (!check_exception(fd, env))
                write_ptr(fd, object);
            break;

        // 30..31

        case 32: {
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, buffer);
            if (eos) return eos;
            char *shorty = read_str(fd, &eos, buffer2);
            if (eos) return eos;

            char ret_t;
            size_t shorty_size = to_shorty(buffer2, shorty, &ret_t);
            if (shorty_size == (size_t) -1) return true;

            jmethodID method_id = (*env)->GetMethodID(env, clazz, buffer, buffer2);
            if (!check_exception(fd, env)) {
                method = jmethod_init(method_id, shorty, shorty_size, ret_t, &eos);
                if (eos) return eos;
                write_ptr(fd, method);
            }
            break; }

        case 33 ... 42:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            read_args(fd, &eos, method->shorty, args_buffer);
            if (eos) return eos;

            switch (kind) {
                case 33: value = (jvalue) (*env)->CallObjectMethodA(env, object, method->ID, args_buffer); break;
                case 34: value = (jvalue) (*env)->CallBooleanMethodA(env, object, method->ID, args_buffer); break;
                case 35: value = (jvalue) (*env)->CallByteMethodA(env, object, method->ID, args_buffer); break;
                case 36: value = (jvalue) (*env)->CallCharMethodA(env, object, method->ID, args_buffer); break;
                case 37: value = (jvalue) (*env)->CallShortMethodA(env, object, method->ID, args_buffer); break;
                case 38: value = (jvalue) (*env)->CallIntMethodA(env, object, method->ID, args_buffer); break;
                case 39: value = (jvalue) (*env)->CallLongMethodA(env, object, method->ID, args_buffer); break;
                case 40: value = (jvalue) (*env)->CallFloatMethodA(env, object, method->ID, args_buffer); break;
                case 41: value = (jvalue) (*env)->CallDoubleMethodA(env, object, method->ID, args_buffer); break;
                case 42: (*env)->CallVoidMethodA(env, object, method->ID, args_buffer); break;
            }
            if (!check_exception(fd, env) && kind != 42)
                write_value(fd, method->ret_t, value);
            break;

        case 43 ... 52:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            read_args(fd, &eos, method->shorty, args_buffer);
            if (eos) return eos;

            switch (kind) {
                case 43: value = (jvalue) (*env)->CallNonvirtualObjectMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 44: value = (jvalue) (*env)->CallNonvirtualBooleanMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 45: value = (jvalue) (*env)->CallNonvirtualByteMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 46: value = (jvalue) (*env)->CallNonvirtualCharMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 47: value = (jvalue) (*env)->CallNonvirtualShortMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 48: value = (jvalue) (*env)->CallNonvirtualIntMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 49: value = (jvalue) (*env)->CallNonvirtualLongMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 50: value = (jvalue) (*env)->CallNonvirtualFloatMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 51: value = (jvalue) (*env)->CallNonvirtualDoubleMethodA(env, object, clazz, method->ID, args_buffer); break;
                case 52: (*env)->CallNonvirtualVoidMethodA(env, object, clazz, method->ID, args_buffer); break;
            }
            if (!check_exception(fd, env) && kind != 52)
                write_value(fd, method->ret_t, value);
            break;

        case 53: 
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            buffer2 = read_str(fd, &eos, buffer);
            if (eos) return eos;
            read_str(fd, &eos, buffer2);
            if (eos) return eos;

            char type = get_return_type(buffer2);
            if (type == 0) return true;

            jfieldID field_id = (*env)->GetFieldID(env, clazz, buffer, buffer2);
            if (!check_exception(fd, env)) {
                field = jfield_init(field_id, type, &eos);
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
            if (!check_exception(fd, env))
                write_value(fd, field->type, value);
            break;
        case 55 ... 62:
            fprintf(stderr, "Warning: use 54 (Get<type>Field) instead of 55..62\n");
            return true;  // eos

        case 63:
            object = (jobject) read_ptr(fd, &eos);
            if (eos) return eos;
            field = (jfield*) read_ptr(fd, &eos);
            if (eos) return eos;
            value = read_value(fd, &eos, field->type);
            if (eos) return eos;

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
            return true;  // eos

        // 72 (GetStaticMethodID)

        case 73 ... 82:
            clazz = (jclass) read_ptr(fd, &eos);
            if (eos) return eos;
            method = (jmethod*) read_ptr(fd, &eos);
            if (eos) return eos;
            read_args(fd, &eos, method->shorty, args_buffer);
            if (eos) return eos;

            switch (kind) {
                case 73: value = (jvalue) (*env)->CallStaticObjectMethodA(env, clazz, method->ID, args_buffer); break;
                case 74: value = (jvalue) (*env)->CallStaticBooleanMethodA(env, clazz, method->ID, args_buffer); break;
                case 75: value = (jvalue) (*env)->CallStaticByteMethodA(env, clazz, method->ID, args_buffer); break;
                case 76: value = (jvalue) (*env)->CallStaticCharMethodA(env, clazz, method->ID, args_buffer); break;
                case 77: value = (jvalue) (*env)->CallStaticShortMethodA(env, clazz, method->ID, args_buffer); break;
                case 78: value = (jvalue) (*env)->CallStaticIntMethodA(env, clazz, method->ID, args_buffer); break;
                case 79: value = (jvalue) (*env)->CallStaticLongMethodA(env, clazz, method->ID, args_buffer); break;
                case 80: value = (jvalue) (*env)->CallStaticFloatMethodA(env, clazz, method->ID, args_buffer); break;
                case 81: value = (jvalue) (*env)->CallStaticDoubleMethodA(env, clazz, method->ID, args_buffer); break;
                case 82: (*env)->CallStaticVoidMethodA(env, clazz, method->ID, args_buffer); break;
            }
            if (!check_exception(fd, env) && kind != 82)
                write_value(fd, method->ret_t, value);
            break;

        // 83..105

        // TODO: support MUTF8
        case 106:
            read_str(fd, &eos, buffer);
            if (eos) return eos;

            object = (*env)->NewStringUTF(env, buffer);
            if (!check_exception(fd, env))
                write_ptr(fd, object);
            break;
        case 107:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            size = (*env)->GetStringUTFLength(env, string);
            if (!check_exception(fd, env))
                write_uleb128(fd, size);
            break;
        case 108:
            string = (jstring) read_ptr(fd, &eos);
            if (eos) return eos;

            text mutf8 = (*env)->GetStringUTFChars(env, string, /*isCopy=*/NULL);
            if (!check_exception(fd, env)) {
                write_str(fd, mutf8);
                (*env)->ReleaseStringUTFChars(env, string, mutf8);
            }
            break;
        case 109:
            fprintf(stderr, "Warning: kind 109 (ReleaseStringUTFChars) is deprecated and not implemented\n");
            return true;  // eos

        // 110..173

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
    char buffer[8192];  // 8 КБ
    jvalue args_buffer[256];
    ClientCtx ctx = {
        .vm = NULL, .env = NULL, .vm_count = 0,
        .args = &args, .own_vm = false,
        .buffer = buffer, .args_buffer = args_buffer,
    };

    while (1)
        if (handle_command(client_fd, &ctx))
            break;

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
    init_socket_server();
    printf("Server is running. Use 'kill %d' or Ctrl+C to stop.\n", getpid());
    while (1)
        sleep(60);
    return 0; 
}
