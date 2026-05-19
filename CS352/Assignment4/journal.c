#include <stdio.h>
#include "journal.h"
#include <pthread.h>
#include <unistd.h>

#define MAX_WRITES 16

/*
Project Overview
@author Evan Litzer
December 7th, 2025

This file is the assigned implementation of a 3-stage journaling pipeline that uses
3 threads and 3 buffers.

Thread 1:
The first thread is the journal-metadata-write-thread.
This thread utilizes write_ids from the first buffer and issues a data write, journal TXB, journal bitmap, and a journal inode.
The thread waits for all 4 issues to complete and then produces write_ids into the second buffer for the next stage of the process.

Thread 2:
The second thread is the journal-commit-write-thread. This utilizes write_ids from the second buffer and isses the TXE which is the commit block.
This thread waits for the completion of the TXE and then produces write_ids into the third buffer.

Thread 3:
The third thread is the checkpoint-metadata thread. This thread utilizes the write_ids from the third buffer and issues the final bitmap and inode writes.
This thread waits for both writes to complete and then calls the write_complete(write_id) function.

Concurrency:
Each of the three buffers has the same size and is circular. They are controlled through a mutex lock and two variables indicating condition, which are 
the not_full and not_empty variables. The producers block only when there is a full buffer, and the consumers block only when the buffer is empty.
This therefore gurantees concurrency, as each thread is either doing work, is blocked due to empty or full buffer, or is waiting for an I/O job to complete.
This is the required condition that the assignment specifies.

Race Condition Avoidance:
For each of the write_id, a write_state_t with flags describes which I/O operations are done, also with a mutex and condition variable.
The three threads wait on the condition variables until the corresponding complete callbacks will set the flags. 
All accesses to the per-write state are guarded by the per-write mutex lock, which will prevent race condition errors between the working threads and the completion callbacks.

Testing and Full Buffer Printing:
All of the testing and back pressure is completed through the block_service.c file.
The first TXE write is delayed by a second before the journal_txe_complete() function is called.
This results in buffer 2 filling and causes thread 1 to block the action of putting into buffer 2.
When this happens, a print message is executed indicating the thread is stuck due to a full buffer.

*/


// Circular Buffer definition
typedef struct {
        int buf[BUFFER_SIZE];       // BUFFER SIZE array of write_ids
        int head;                   // Index of next element to remove
        int tail;                   // Index of next element to insert.
        int count;                  // Number of elements currently in buffer
        pthread_mutex_t lock;       // Mutex lock that protects buffer state
        pthread_cond_t not_full;    // Signaled when buffer transitions from full to not full
        pthread_cond_t not_empty;   // Signaled when buffer transitions from empty to not empty
} buffer_t ;

static buffer_t buffer1; //FileSystem to stage 1 (metadata thread)
static buffer_t buffer2; // stage 1 --> stage 2 (metadata-completed -> commit thread)
static buffer_t buffer3; // stage 2 --> stage 3 (commit-completed -> checkpoint thread)

typedef struct {
    int data_done;      // Var indicating the data write to the final location is done
    int txb_done;       // Var indicating the journal TXB write is done
    int j_bitmap_done;       // Var indicating the journal bitmap write is done
    int j_inode_done;       // Var indicating the journal inode write is done
    int txe_done;       // Var indicating the journal txe write is done. 
    int c_bitmap_done;       // Var indicating the final bitmap write is done
    int c_inode_done;       // Var indicating the final inode write is done
    pthread_mutex_t lock;   //mutex lock for threads
    pthread_cond_t cv;      // Per-write condition vars for waiting on flags
} write_state_t;

static write_state_t writes[MAX_WRITES];       // Filesystem.c uses write_ids 0-15

// Initialize the buffers and set default values.
static void buffer_init(buffer_t *b) {
    b->head = b->tail = b->count = 0;
    pthread_mutex_init(&b->lock, NULL);
    pthread_cond_init(&b->not_full, NULL);
    pthread_cond_init(&b->not_empty, NULL);
}

// Place an id into a bounded buffer, blocking the action if the buffer is full.
static void buffer_put(buffer_t *b, int id) {
    pthread_mutex_lock(&b->lock);
    while (b->count == BUFFER_SIZE) {
        // Test message when buffer 2 backs up due to the TXE slowness.
        if (b == &buffer2) {
            printf("thread stuck from full buffer\n");
        }
        pthread_cond_wait(&b->not_full, &b->lock);
    }

    // Insert element at tail
    b->buf[b->tail] = id;
    b->tail = (b->tail + 1) % BUFFER_SIZE;
    b->count++;

    // Wake up any consumer waiting for not empty
    pthread_cond_signal(&b->not_empty);
    pthread_mutex_unlock(&b->lock);
}

// Get an ID from the bounded buffer, blocking it if the buffer is empty.
static int buffer_get(buffer_t *b) {
    pthread_mutex_lock(&b->lock);
    while (b->count == 0) {
        pthread_cond_wait(&b->not_empty, &b->lock);
    }

    int id = b->buf[b->head];
    b->head = (b->head + 1) % BUFFER_SIZE;
    b->count--;

    pthread_cond_signal(&b->not_full);
    pthread_mutex_unlock(&b->lock);
    return id;
}

// STAGE 1
static int stage1_done(write_state_t *ws) {
    return ws->data_done &&
           ws->txb_done &&
           ws->j_bitmap_done &&
           ws->j_inode_done;
}

// Thread 1: Journal-metadata write thread.
static void *metadata_thread(void *arg) {
    while (1) {
        // Wait for a request from the filesystem (buffer 1)
        int id = buffer_get(&buffer1);
        printf("[stage1] got %d\n", id);

        write_state_t *ws = &writes[id];

        // Clear stage 1 flags for this write (defensive)
        pthread_mutex_lock(&ws->lock);
        ws->data_done = 0;
        ws->txb_done = 0;
        ws->j_bitmap_done = 0;
        ws->j_inode_done = 0;
        pthread_mutex_unlock(&ws->lock);

        // Issue the four writes
        issue_write_data(id);
        issue_journal_txb(id);
        issue_journal_bitmap(id);
        issue_journal_inode(id);

        // Wait until all four complete
        pthread_mutex_lock(&ws->lock);
        while (!stage1_done(ws)) {
            pthread_cond_wait(&ws->cv, &ws->lock);
        }
        pthread_mutex_unlock(&ws->lock);

        // Now stage 1 is really finished for this id
        buffer_put(&buffer2, id);
    }
    return NULL;
}


// STAGE 2 (journal-commit write thread)
static void *commit_thread(void *arg) {
    while (1) {
        // Wait for metadata-completed request
        int id = buffer_get(&buffer2);
        printf("[stage2] got %d\n", id);

        write_state_t *ws = &writes[id];

        // Clear TXE flag for this write
        pthread_mutex_lock(&ws->lock); 
        ws->txe_done = 0;
        pthread_mutex_unlock(&ws->lock);

        // Issue the TXE write
        issue_journal_txe(id);

        // Wait until TXE completes
        pthread_mutex_lock(&ws->lock);
        while (!ws->txe_done)
        {
            pthread_cond_wait(&ws->cv, &ws->lock);
        }
        pthread_mutex_unlock(&ws->lock);

        // later: issue_journal_txe and wait
        buffer_put(&buffer3, id);
    }
    return NULL;
}

// STAGE 3 Checkpoint the metadata to the final locations
static int stage3_done(write_state_t *ws) {
    return ws->c_bitmap_done && ws->c_inode_done;
}

// Thread 3: Checkpoint metadata thread
static void *checkpoint_thread(void *arg) {
    while (1) {
        // Wait for a committed request
        int id = buffer_get(&buffer3);
        printf("[stage3] got %d\n", id);

        write_state_t *ws = &writes[id];

        // Clear checkpoint flags for this write.
        pthread_mutex_lock(&ws->lock);
        ws->c_bitmap_done = 0;
        ws->c_inode_done = 0;
        pthread_mutex_unlock(&ws->lock);

        // Issue final metadata checkpoint writes.
        issue_write_bitmap(id);
        issue_write_inode(id);

        // Wait until both checkpoint writes are complete.
        pthread_mutex_lock(&ws->lock);
        while (!stage3_done(ws)) {
            pthread_cond_wait(&ws->cv, &ws->lock);
        }

        //Entire journaling and checkpoint process is now done, so unlock
        pthread_mutex_unlock(&ws->lock);

        // later: issue_write_bitmap / write_inode and wait
        write_complete(id);
    }
    return NULL;
}

/* This function can be used to initialize the buffers and threads.
 */
void init_journal() {
    // Initialize the buffers
    buffer_init(&buffer1);
    buffer_init(&buffer2);
    buffer_init(&buffer3);

    // Intitalize the per-write state, which includes flags and syncs.
    for (int i = 0; i < MAX_WRITES; i++)
    {
        writes[i].data_done = 0;
        writes[i].txb_done = 0;
        writes[i].j_bitmap_done = 0;
        writes[i].j_inode_done = 0;
        writes[i].txe_done = 0;
        writes[i].c_bitmap_done = 0;
        writes[i].c_inode_done = 0;
        pthread_mutex_init(&writes[i].lock, NULL);
        pthread_cond_init(&writes[i].cv, NULL);
    }

    //Create the three worker threads
    pthread_t t1, t2, t3;
    pthread_create(&t1, NULL, metadata_thread, NULL);
    pthread_create(&t2, NULL, commit_thread, NULL);
    pthread_create(&t3, NULL, checkpoint_thread, NULL);

    // optional: detach so we don't care about joining them
    pthread_detach(t1);
    pthread_detach(t2);
    pthread_detach(t3);
}


/* This function is called by the file system to request writing data to
 * persistent storage.
*/

void request_write(int write_id) {
    buffer_put(&buffer1, write_id);
}

// This is called when the TXB is fully written to the journal
void journal_txb_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->txb_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

// This is called when the journal bitmap block is fully written
void journal_bitmap_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->j_bitmap_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

// Called when the journal inode block is fully written
void journal_inode_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->j_inode_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

// Called when the data write to its final location is complete.
void write_data_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->data_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

// Called when the TXE commit block is fully written to the journal.
void journal_txe_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->txe_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);

}

// This is called when the final bitmap checkpoint write is complete.
void write_bitmap_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->c_bitmap_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

// This function is called when the final inode checkpoint write is complete.
void write_inode_complete(int write_id) {
        write_state_t *ws = &writes[write_id];
        pthread_mutex_lock(&ws->lock);
        ws->c_inode_done = 1;
        pthread_cond_signal(&ws->cv);
        pthread_mutex_unlock(&ws->lock);
}

