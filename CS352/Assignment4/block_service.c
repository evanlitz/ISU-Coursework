#include <stdio.h>
#include "journal.h"
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>

typedef struct {
	int write_id;
} txe_arg_t;

static void *txe_delay_thread(void *arg)
{
	txe_arg_t *a = (txe_arg_t *)arg;
	sleep(1);
	journal_txe_complete(a->write_id);
	free(a);
	return NULL;
}

void issue_journal_txb(int write_id) {
	printf("issue journal txb %d\n", write_id);
	journal_txb_complete(write_id);
}

void issue_journal_bitmap(int write_id) {
	printf("issue journal bitmap %d\n", write_id);
	journal_bitmap_complete(write_id);
}

void issue_journal_inode(int write_id) {
	printf("issue journal inode %d\n", write_id);
	journal_inode_complete(write_id);
}

void issue_write_data(int write_id) {
	printf("issue write data %d\n", write_id);
	write_data_complete(write_id);
}

void issue_journal_txe(int write_id) {
	printf("issue journal txe %d\n", write_id);

	static int first = 1;
	if (first) {
		first = 0;

		pthread_t t;
		txe_arg_t *a = malloc(sizeof(txe_arg_t));
		a->write_id = write_id;
		pthread_create(&t, NULL, txe_delay_thread, a);
		pthread_detach(t);
	} else {
		journal_txe_complete(write_id);
	}
}

void issue_write_bitmap(int write_id) {
	printf("issue write bitmap %d\n", write_id);
	write_bitmap_complete(write_id);
}

void issue_write_inode(int write_id) {
	printf("issue write inode %d\n", write_id);
	write_inode_complete(write_id);
}
