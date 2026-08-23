#include "mem_pool.h"
#include <stdlib.h> // malloc, free


void* pool_alloc(ScratchPool* pool, size_t size) {
    if (size == 0)
        return NULL;

    size_t next_used = pool->used + size;
    if (next_used <= POOL_BUFFER_SIZE) {
        void* ptr = pool->buffer + pool->used;
        pool->used = next_used;
        return ptr;
    }

    if (pool->malloc_count >= POOL_MAX_MALLOCS)
        return NULL;

    void* ptr = malloc(size);
    if (!ptr) {
        perror("malloc pool_alloc");
        return NULL;
    }

    pool->malloc_ptrs[pool->malloc_count++] = ptr;
    return ptr;
}

void pool_clear(ScratchPool* pool) {
    for (int i = 0; i < pool->malloc_count; i++)
        free(pool->malloc_ptrs[i]);
    pool->malloc_count = 0;
    pool->used = 0;
}


void* block_pool_alloc(BlockPool* pool, size_t size) {
    if (size == 0 || size > POOL_BLOCK_SIZE)
        return NULL;

    if (pool->block_count == 0 || pool->used + size > POOL_BLOCK_SIZE) {
        if (pool->block_count >= POOL_MAX_BLOCKS)
            return NULL;

        uint8_t* new_block = malloc(POOL_BLOCK_SIZE);
        if (!new_block) {
            perror("malloc block_pool_alloc");
            return NULL;
        }

        pool->blocks[pool->block_count] = new_block;
        pool->block_count++;
        pool->used = 0;
    }

    uint8_t* last_block = pool->blocks[pool->block_count - 1];
    void* ptr = last_block + pool->used;
    pool->used += size;
    return ptr;
}

void block_pool_clear(BlockPool* pool) {
    for (int i = 0; i < pool->block_count; i++)
        free(pool->blocks[i]);
    pool->block_count = 0;
    pool->used = 0;
}
