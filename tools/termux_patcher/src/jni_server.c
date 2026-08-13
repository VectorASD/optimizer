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

bool handle_command(int fd) {
    bool eos = false;
    uint8_t kind = read_byte(fd, &eos);
    if (eos)
        return eos;
    printf("kind: %d\n", kind);
    /* switch (kind) {
        case 0:
            jint err = JNI_CreateJavaVM(&vm, (void **) &env, &args);
            break;
    }*/
    return eos;
}

void* handle_client_thread(void* arg) {
    int client_fd = (int)(intptr_t) arg;

    while (1)
        if (handle_command(client_fd))
            break;

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
