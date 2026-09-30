#include "context.h"


// Возвращает 0 при успехе, иначе положительный код ошибки:
// 1 - нет JNIEnv в контексте
// 2 - java/lang/Class не найден
// 3 - java/lang/reflect/Method не найден
// 4 - NewGlobalRef провалился (любой из двух)
// 5..11 - соответствующий GetMethodID вернул NULL
int init_reflection_cache(ClientCtx* ctx) {
    JNIEnv* env = ctx->env;
    if (!env) return 1;

    jclass classClass = (*env)->FindClass(env, "java/lang/Class");
    if (!classClass) {
        (*env)->ExceptionClear(env);
        return 2;
    }

    jclass methodClass = (*env)->FindClass(env, "java/lang/reflect/Method");
    if (!methodClass) {
        (*env)->ExceptionClear(env);
        (*env)->DeleteLocalRef(env, classClass);
        return 3;
    }

    jclass cc_g = (jclass)(*env)->NewGlobalRef(env, classClass);
    jclass mc_g = (jclass)(*env)->NewGlobalRef(env, methodClass);
    (*env)->DeleteLocalRef(env, classClass);
    (*env)->DeleteLocalRef(env, methodClass);

    if (!cc_g || !mc_g) {
        (*env)->ExceptionClear(env);
        if (cc_g) (*env)->DeleteGlobalRef(env, cc_g);
        if (mc_g) (*env)->DeleteGlobalRef(env, mc_g);
        return 4;
    }

    jmethodID gcn = (*env)->GetMethodID(env, cc_g, "getName",             "()Ljava/lang/String;");
    jmethodID gdm = (*env)->GetMethodID(env, cc_g, "getDeclaredMethods",  "()[Ljava/lang/reflect/Method;");
    jmethodID gms = (*env)->GetMethodID(env, cc_g, "getMethods",          "()[Ljava/lang/reflect/Method;");
    jmethodID mgn = (*env)->GetMethodID(env, mc_g, "getName",             "()Ljava/lang/String;");
    jmethodID mgd = (*env)->GetMethodID(env, mc_g, "getDeclaringClass",   "()Ljava/lang/Class;");
    jmethodID mgp = (*env)->GetMethodID(env, mc_g, "getParameterTypes",   "()[Ljava/lang/Class;");
    jmethodID mgr = (*env)->GetMethodID(env, mc_g, "getReturnType",       "()Ljava/lang/Class;");
    int error = !gcn ? 5 : !gdm ? 6 : !gms ? 7 : !mgn ? 8 : !mgd ? 9 : !mgp ? 10 : !mgr ? 11 : 0;
    if (error) {
        (*env)->ExceptionClear(env);
        (*env)->DeleteGlobalRef(env, cc_g);
        (*env)->DeleteGlobalRef(env, mc_g);
        return error;
    }

    ctx->classClass              = cc_g;
    ctx->methodClass             = mc_g;
    ctx->classGetName            = gcn;
    ctx->classGetDeclaredMethods = gdm;
    ctx->classGetMethods         = gms;
    ctx->methodGetName           = mgn;
    ctx->methodGetDeclaringClass = mgd;
    ctx->methodGetParameterTypes = mgp;
    ctx->methodGetReturnType     = mgr;
    return JNI_OK;
}

// Возвращает новую позицию в буфере или (size_t)-1 при ошибке/переполнении.
size_t append_class_type(ClientCtx* ctx, jobject clazz, char* buf, size_t pos, size_t cap) {
    JNIEnv* env = ctx->env;

    jstring name_j = (jstring)(*env)->CallObjectMethod(env, clazz, ctx->classGetName);
    if (!name_j) return (size_t)-1;

    const char* name = (*env)->GetStringUTFChars(env, name_j, NULL);
    if (!name) {
        (*env)->DeleteLocalRef(env, name_j);
        return (size_t)-1;
    }

    bool ok = true;
    char prim = 0;

    if      (strcmp(name, "void")    == 0) prim = 'V';
    else if (strcmp(name, "boolean") == 0) prim = 'Z';
    else if (strcmp(name, "byte")    == 0) prim = 'B';
    else if (strcmp(name, "char")    == 0) prim = 'C';
    else if (strcmp(name, "short")   == 0) prim = 'S';
    else if (strcmp(name, "int")     == 0) prim = 'I';
    else if (strcmp(name, "long")    == 0) prim = 'J';
    else if (strcmp(name, "float")   == 0) prim = 'F';
    else if (strcmp(name, "double")  == 0) prim = 'D';

    if (prim) {
        if (pos < cap) buf[pos++] = prim;
        else ok = false;
    } else if (name[0] == '[') {
        // Массивы: getName() уже даёт "[I" / "[Ljava.lang.String;"
        for (const char* p = name; *p; p++) {
            if (pos >= cap) { ok = false; break; }
            buf[pos++] = (*p == '.') ? '/' : *p;
        }
    } else {
        // Обычные классы: оборачиваем в L...;
        if (pos >= cap) ok = false;
        else buf[pos++] = 'L';

        for (const char* p = name; ok && *p; p++) {
            if (pos >= cap) { ok = false; break; }
            buf[pos++] = (*p == '.') ? '/' : *p;
        }
        if (ok) {
            if (pos >= cap) ok = false;
            else buf[pos++] = ';';
        }
    }

    (*env)->ReleaseStringUTFChars(env, name_j, name);
    (*env)->DeleteLocalRef(env, name_j);
    return ok ? pos : (size_t)-1;
}

// Строит "(params)return" прямо в ctx->scratch_mem->buffer.
// Возвращает строку с нулевым терминатором при успехе
char* build_method_signature(ClientCtx* ctx, jobject method_obj) {
    JNIEnv* env = ctx->env;
    char* buf = (char*) ctx->scratch_mem->buffer;
    size_t cap = sizeof(ctx->scratch_mem->buffer);
    size_t pos = 0;

    jobjectArray params = (jobjectArray)(*env)->CallObjectMethod(env, method_obj, ctx->methodGetParameterTypes);
    if (!params) return NULL;

    jobject ret = (*env)->CallObjectMethod(env, method_obj, ctx->methodGetReturnType);
    if (!ret) {
        (*env)->DeleteLocalRef(env, params);
        return NULL;
    }

    bool ok = true;

    if (pos >= cap) { ok = false; goto cleanup; }
    buf[pos++] = '(';

    jsize n = (*env)->GetArrayLength(env, params);
    for (jsize i = 0; i < n; i++) {
        jobject p = (*env)->GetObjectArrayElement(env, params, i);
        if (!p) { ok = false; goto cleanup; }
        pos = append_class_type(ctx, p, buf, pos, cap);
        (*env)->DeleteLocalRef(env, p);
        if (pos == (size_t)-1) { ok = false; goto cleanup; }
    }

    if (pos >= cap) { ok = false; goto cleanup; }
    buf[pos++] = ')';

    pos = append_class_type(ctx, ret, buf, pos, cap);
    if (pos == (size_t)-1) { ok = false; goto cleanup; }

    if (pos >= cap) { ok = false; goto cleanup; }
    buf[pos] = 0;

cleanup:
    (*env)->DeleteLocalRef(env, params);
    (*env)->DeleteLocalRef(env, ret);
    return ok ? buf : NULL;
}
