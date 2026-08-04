#include <stdio.h>
#include <jni.h>

int main_old() {
    JavaVM* vm = NULL;
    jsize count = 0;
    jint res = JNI_GetCreatedJavaVMs(&vm, 1, &count);
    
    printf("JNI_GetCreatedJavaVMs returned: %d\n", res);
    printf("Number of Java VMs in this process: %d\n", count);
    if (count > 0)
        printf("VM pointer: %p\n", vm);
    // увы и да ах!!!!!!!!!!!!!!!!!!!! Что count из termux ВСЕГДА будет равен 0
    return 0;
}

int main() {
    JavaVM *vm = NULL;
    JNIEnv *env = NULL;
    JavaVMInitArgs args;
    JavaVMOption options[2];
    jint res;

    // Подготовка аргументов
    args.version = JNI_VERSION_1_6; // можно JNI_VERSION_1_8
    options[0].optionString = "-Djava.class.path=.";
    // Можно добавить ещё опции, например, -verbose:jni для отладки
    args.nOptions = 1;
    args.options = options;
    args.ignoreUnrecognized = JNI_TRUE;

    // Создаём VM
    res = JNI_CreateJavaVM(&vm, (void **) &env, &args);
    if (res != JNI_OK) {
        fprintf(stderr, "JNI_CreateJavaVM failed with code %d\n", res);
        return 1;
    }
    printf("JVM created successfully!\n");

    // --- Работа с BigInteger ---
    jclass bigIntClass = (*env)->FindClass(env, "java/math/BigInteger");
    if (bigIntClass == NULL) {
        fprintf(stderr, "FindClass failed\n");
        if ((*env)->ExceptionCheck(env)) {
            (*env)->ExceptionDescribe(env);
            (*env)->ExceptionClear(env);
        }
        goto destroy;
    }

    jmethodID ctor = (*env)->GetMethodID(env, bigIntClass, "<init>", "(Ljava/lang/String;)V");
    if (ctor == NULL) {
        fprintf(stderr, "GetMethodID for constructor failed\n");
        goto destroy;
    }

    jstring baseStr = (*env)->NewStringUTF(env, "123456789");
    jstring expStr  = (*env)->NewStringUTF(env, "3");
    jstring modStr  = (*env)->NewStringUTF(env, "1000000007");
    if (baseStr == NULL || expStr == NULL || modStr == NULL) {
        fprintf(stderr, "NewStringUTF failed\n");
        goto destroy;
    }

    jobject base = (*env)->NewObject(env, bigIntClass, ctor, baseStr);
    jobject exponent = (*env)->NewObject(env, bigIntClass, ctor, expStr);
    jobject modulus = (*env)->NewObject(env, bigIntClass, ctor, modStr);
    if (base == NULL || exponent == NULL || modulus == NULL) {
        fprintf(stderr, "NewObject failed\n");
        goto destroy;
    }

    jmethodID modPow = (*env)->GetMethodID(env, bigIntClass, "modPow",
                                           "(Ljava/math/BigInteger;Ljava/math/BigInteger;)Ljava/math/BigInteger;");
    if (modPow == NULL) {
        fprintf(stderr, "GetMethodID for modPow failed\n");
        goto destroy;
    }

    jobject result = (*env)->CallObjectMethod(env, base, modPow, exponent, modulus);
    if (result == NULL) {
        fprintf(stderr, "CallObjectMethod returned NULL\n");
        if ((*env)->ExceptionCheck(env)) {
            (*env)->ExceptionDescribe(env);
            (*env)->ExceptionClear(env);
        }
        goto destroy;
    }

    jmethodID toString = (*env)->GetMethodID(env, bigIntClass, "toString", "()Ljava/lang/String;");
    jstring resultStr = (*env)->CallObjectMethod(env, result, toString);
    const char *chars = (*env)->GetStringUTFChars(env, resultStr, NULL);
    printf("Result of modPow: %s\n", chars);
    // python -c "print(pow(123456789, 3, 1000000007))"  # 350575129
    // Result of modPow: 350575129  # yappy!!!
    (*env)->ReleaseStringUTFChars(env, resultStr, chars);

destroy:
    if (vm) {
        (*vm)->DestroyJavaVM(vm);
    }
    return 0;
}

/*
DVM: clang -I./include -o test_jni test_jni.c /system/lib64/libandroid_runtime.so
JVM: clang -I./include -o test_jni test_jni.c $JAVA_HOME/lib/server/libjvm.so -Wl,-rpath,$JAVA_HOME/lib/server
*/

// for lib in /system/lib64/*.so /system/lib/*.so; do     readelf -Ws "$lib" 2>/dev/null | grep -E "JNI_GetCreatedJavaVMs" && echo "  $lib"; done
/*
    2844: 0000000000203554   160 FUNC    GLOBAL PROTECTED   15 JNI_GetCreatedJavaVMs
/system/lib64/libandroid_runtime.so
    106: 000000000000f6c4   160 FUNC    GLOBAL PROTECTED   14 JNI_GetCreatedJavaVMs
/system/lib64/libdataloader.so
    2837: 0015e979   112 FUNC    GLOBAL PROTECTED   14 JNI_GetCreatedJavaVMs
/system/lib/libandroid_runtime.so
    125: 0000b3c5   112 FUNC    GLOBAL PROTECTED   14 JNI_GetCreatedJavaVMs
/system/lib/libdataloader.so

Вывод:
точка входа в DVM - это /system/lib64/libandroid_runtime.so
а 32-ух битная версия только на случай отсутствия lib64.

Вывод2:
эта штука полностью неиспользуемая в termux :/
зато тот же функционал полностью работает из libjvm.so
установленного из termux-пакета java-21-openjdk
*/
