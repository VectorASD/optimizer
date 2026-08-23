#include <stdint.h> // uint8_t, size_t


#ifndef MEM_POOL_H
#define MEM_POOL_H


#define POOL_BUFFER_SIZE  0x10000 // 64 Kb
#define POOL_MAX_MALLOCS  16

#define POOL_BLOCK_SIZE  0x10000 // 64 Kb
#define POOL_MAX_BLOCKS  64

typedef struct ScratchPool {
    uint8_t buffer[POOL_BUFFER_SIZE];
    size_t used;
    void* malloc_ptrs[POOL_MAX_MALLOCS];
    int malloc_count;
} ScratchPool;

static inline ScratchPool pool_init() {
    ScratchPool pool;
    pool.used = 0;
    pool.malloc_count = 0;
    return pool;
}
void* pool_alloc(ScratchPool* pool, size_t size);
void pool_clear(ScratchPool* pool);


typedef struct BlockPool {
    uint8_t* blocks[POOL_MAX_BLOCKS];
    int block_count;
    size_t used;
} BlockPool;

static inline BlockPool block_pool_init(void) {
    BlockPool pool;
    pool.block_count = 0;
    pool.used = 0;
    return pool;
}
void* block_pool_alloc(BlockPool* pool, size_t size);
void block_pool_clear(BlockPool* pool);


#endif // MEM_POOL_H
