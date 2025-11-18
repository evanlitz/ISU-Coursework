/* To compile this program:
 *   gcc cs321_f2024_pa1_quicksort.c -o cs321_f2024_pa1_quicksort
 * Change N and recompile to run on arrays of different sizes.
 *
 * For this assignment, you'll be implementing quicksort in the LEG
 * subset of the ARMv8 ISA.  Quicksort is an n-squared comparison
 * sort, with expected O(n log(n)) behavior, which you should all be
 * familiar with from your data structures course.
 *
 * Regardless of how comfortable you may be with quicksort, or with how
 * well you may comprehend this C implementation, we want to stress here that
 * you do not have to understand this algorithm!  You don't even have to try
 * to understand it.  All that you have to do is, essentially, be the
 * compiler and translate this C code into LEGv8.  This is not to discourage
 * understanding.  Understanding is a good and useful thing.  We are simply
 * pointing out that you don't need to understand the algorithm in order to
 * implement your solution.  It's not rare that a route of expedience is
 * optimal.
 *
 * See the comments and code below for details on exactly what you must 
 * implement.
 *
 * Note that this C implementation uses 32-bit ints, but your ARM solution
 * will use 64-bit ints.  In your code, all variables will be 64-bit ints or
 * pointers to 64-bit ints.  This will not be stated elsewhere.
 */

#include <stdio.h>

#define N 512

/* Here is a single-function version of partition, the workhorse
 * function of quicksort.  This, or something very similar, is
 * probably what you would write if you were doing this in a
 * higher-level language.
 *
 * Below, we break this into a number of smaller functions.  We do this for
 * two reasons:
 *
 *   1) The bigger a procedure is, the more difficult it (usually) is to 
 *      implement it in assembly (in particular, the refactor eliminates
 *      nested loops); and
 *   2) We want to force you to implement multiple procedures, use the stack,
 *      and adhere to ARMv8 calling conventions.
 *
 * You will NOT be implementing this function.  You'll be implementing the
 * broken-down version of it below.  This version is only here for reference.
 */
int partition_reference_do_not_implement(int *a, int f, int l)
{
  int i, j, p, t;

  for (p = a[f], i = f + 1, j = l; i <= j;) {
    while ((i <= l) && (a[i] < p)) {
      i++;
    }
    while ((j > f) && (a[j] >= p)) {
      j--;
    }
    if (i < j) {
      t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
  }
  if (j != f) {
    t = a[f];
    a[f] = a[j];
    a[j] = t;
  }

  return j;
}

/* Searches array a between the current i and the last index in the partition
 * l looking for the next element less than the partition value p, returning
 * its index or l + 1.
 */
int next_i(int *a, int i, int l, int p)
{
  while ((i <= l) && (a[i] < p)) {
    i++;
  }

  return i;
}

/* Searches array a in reverse order between the current j and the
 * first index in the partition f looking for the next earlier element
 * greater than or equal to the partition value p, returning its index
 * or f.
 */
int next_j(int *a, int j, int f, int p)
{
  while ((j > f) && (a[j] >= p)) {
    j--;
  }

  return j;
}

/* Swaps the value in a at index i with the value at index j. */
void swap(int *a, int i, int j)
{
  int tmp;

  tmp = a[i];
  a[i] = a[j];
  a[j] = tmp;
}

/* Partitions the elements of array a between indices f and l around
   the partition value a[f].
 */
int partition(int *a, int f, int l)
{
  int i, j, p, t;

  p = a[f];
  i = f + 1;
  j = l;
  
  while (i <= j) {
    i = next_i(a, i, l, p);
    j = next_j(a, j, f, p);

    if (i < j) {
      swap(a, i, j);
    }
  }
  
  if (j != f) {
    swap(a, j, f);
  }

  return j;
}

/* Calls partition to break the array a between f and l into two subarrays
 * and recursively calls quicksort_recurse on those.  Recursion bottoms out
 * on arrays of 0 or 1 element, which are trivially sorted.
 */
void quicksort_recurse(int *a, int f, int l)
{
  int p;

  if (f >= l) {
    return;
  }

  p = partition(a, f, l);
  quicksort_recurse(a, f, p - 1);
  quicksort_recurse(a, p + 1, l);
}

/* Helper to call quicksort_recurse correctly without presenting a strange
 * interface to users.
 */
void quicksort(int *a, int n)
{
  quicksort_recurse(a, 0, n - 1);
}

/* fill fills the array a (of n elements) with decreasing values from *
 * n - 1 to zero (reverse sorted order).                              */
void fill(int *a, int n) {
  int i;
  
  for (i = 0; i < n; i++) {
    a[i] = n - i - 1;
  }
}

/* Your main function should allocate space for an array, call fill to   *
 * fill it with decreasing numbers, and then call quicksort to sort      *
 * it.  Use the HALT emulator instruction to see the memory contents and *
 * confirm that your functions work.  You may choose any array size you  *
 * like (up to the default limit of memory, 4096 bytes or 512 8-byte     *
 * integers).                                                            *
 *                                                                       * 
 * After completing all of the above, HALT the emulator to force a core  *
 * dump so that you (and the TAs) can examine the contents of memory.    *
 *                                                                       *
 * You must implement all functions described above except for the       *
 * reference implementation of partition.  You are acting as the         *
 * compiler here; you are not granted creative freedom to refactor these *
 * functions to your liking.  You must adhere to ARMv8 calling           *
 * conventions; in particular, you must correctly use the stack when     *
 * calling and implementing procedures, and a procedure may not "know"   *
 * anything that it was not explicitly informed of by way of its         *
 * parameters!  For example: Even though you--the programmer--know that  *
 * no other procedure uses X22, you still must save it before you use it *
 * and restore it when you are finished with it.  Imagine that, instead  *
 * of you writing all of these procedures, each of them is written by a  *
 * different person, but none of you are permitted to communicate with   *
 * each other in any way.  The only thing each of you has is this        *
 * specification.  When we put all of your procedures together, your     *
 * program should work, but the only way that will be possible is if you *
 * fully adhere to convention.                                           *
 *                                                                       *
 * You may work alone or with a single partner on this assignment.       */
int main(int argc, char *argv[])
{
  /* In your LEGv8 program, main will not be a procedure.  Control will *
   * begin at the top of the file, so you should think of that as main. *
   * If control reaches the end of the file, the program will exit,     *
   * which you may think of as leaving main.                            */

  int a[N];

  fill(a, N);

  /*
  int i;
  for (i = 0; i < N; i++) {
    printf("%d\t", a[i]);
  }
  printf("\n");
  */
  
  quicksort(a, N);

  /*
  for (i = 0; i < N; i++) {
    printf("%d\t", a[i]);
  }
  printf("\n");
  */
  
  return 0;
}
