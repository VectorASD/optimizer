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
int read_sleb128(int fd, bool *eos) {
    int number = read_uleb128(fd, eos);
    return (number >> 1) ^ (number & 1 ? -1 : 0);  // zigzag
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
void write_sleb128(int fd, int val) {
    int u = (val << 1) ^ -(val < 0);
    write_uleb128(fd, u);
}


typedef struct ClientCtx {
    JavaVM* vm;
    JNIEnv* env;
    JavaVM* vm_arr[16];
    int vm_count;
    JavaVMInitArgs* args;
    bool own_vm;
} ClientCtx;

bool handle_command(int fd, ClientCtx *ctx) {
    bool eos = false;
    jint error = JNI_EINVAL;  /* invalid arguments */
    uint8_t kind = read_byte(fd, &eos);
    if (eos)
        return eos;
    printf("kind: %d\n", kind);
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
    ClientCtx ctx = {
        .vm = NULL, .env = NULL, .vm_count = 0,
        .args = &args, .own_vm = false
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

    const char* socket_path = "/data/data/com.termux/files/usr/tmp/jni.sock";
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
