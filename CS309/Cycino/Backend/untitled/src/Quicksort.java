import java.util.Scanner;

public class Quicksort {
    static int[] array = new int[5];
    static int X0, X1, X2, X9, X10, X11, X15, X16, X17, X18, X19, X20;

    public static void main(String[] args) {
        X20 = 69;
        X19 = 0;
        X0 = 0;
        X1 = 5;
        fill();
        print();
        quicksort();
        print();
    }

    public static void fill() {
        X9 = 0;
        while (X1 > X9) {
            X10 = X1 - X9 - 1;
            X11 = X9 * 8;
            array[X11 / 8] = X10;
            X9++;
        }
    }

    public static void print() {
        X9 = 0;
        while (X1 > X9) {
            X10 = array[X9];
            System.out.print(X10 + " ");
            X9++;
        }
        System.out.println();
    }

    public static void quicksort() {
        X2 = X1 - 1;
        X1 = 0;
        quicksort_recurse();
    }

    public static void quicksort_recurse() {
        if (X1 >= X2) return;

        int p = partition();

        X9 = p;
        X2 = p - 1;
        quicksort_recurse();

        X1 = p + 1;
        X2 = array.length - 1;
        quicksort_recurse();
    }

    public static int partition() {
        X9 = X1 + 1;
        X10 = X2;
        int p = array[X1];

        while (X9 <= X10) {
            while (X9 <= X2 && array[X9] <= p) X9++;
            while (array[X10] > p) X10--;
            if (X9 < X10) swap(X9, X10);
        }
        swap(X1, X10);
        return X10;
    }

    public static void swap(int i, int j) {
        int temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}