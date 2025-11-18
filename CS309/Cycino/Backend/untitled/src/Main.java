import java.nio.file.FileSystemNotFoundException;
import java.util.ArrayList;
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        //int[] a = {19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0};
<<<<<<< HEAD
        //int[] a = {4,3,2,1,0};
        //System.out.println(next_i(a,0,2,16));
        //System.out.println(next_j(a, 19,0,19));
        //quicksort(a, a.length);
        System.out.println(fill());
=======
        int[] a = {4,3,2,1,0};
        //System.out.println(next_i(a,0,2,16));
        //System.out.println(next_j(a, 19,0,19));
        quicksort(a, a.length);
>>>>>>> 33-blackjack-game-view
    }
    public static int next_i(int[] a, int i, int l, int p)
    {
        while ((i <= l) && (a[i] < p)) {
            i++;
            //System.out.println("i: " + i);
        }

        return i;
    }
<<<<<<< HEAD

    public enum SUIT{
        HEARTS,
        DIAMONDS,
        SPADES,
        CLUBS
    }

    public enum VALUE{
        JACK,
        QUEEN,
        KING,
        ACE

    }
    private static ArrayList<String> fill(){
        ArrayList<String> list = new ArrayList<>();
        for(int i = 0; i < 4; i++){
            for(int j = 2; j < 11; j++){
                String c = j + " of " + SUIT.values()[i];
                list.add(c);
            }
            for(int j = 0; j < 4; j++){
                String c = VALUE.values()[j] + " of " + SUIT.values()[i];
                list.add(c);
            }
        }
        return list;
    }
=======
>>>>>>> 33-blackjack-game-view
    public static int next_j(int[] a, int j, int f, int p)
    {
        System.out.println("inputs: " + j + ", " + f + ", " + p);
        while ((j > f) && (a[j] >= p)) {
            j--;
            //System.out.println("j: " + j);
        }

        return j;
    }

    public static int partition(int[] a, int f, int l)
    {
        //System.out.println("gay");
        int i, j, p, t;

        p = a[f];
        i = f + 1;
        j = l;

        while (i <= j) {
            i = next_i(a, i, l, p);
            System.out.println(i);
            j = next_j(a, j, f, p);
            System.out.println(j);

            if (i < j) {
                swap(a, i, j);
            }
        }

        if (j != f) {
            swap(a, j, f);
        }

        return j;
    }
    private static void swap(int[] a, int i, int j)
    {
        int tmp;

        tmp = a[i];
        a[i] = a[j];
        a[j] = tmp;
        System.out.println(Arrays.toString(a));
    }
    public static void quicksort_recurse(int[] a, int f, int l)
    {
        int p;

        if (f >= l) {
            return;
        }

        p = partition(a, f, l);
        System.out.println("p: " +p);

        quicksort_recurse(a, f, p - 1);
        quicksort_recurse(a, p + 1, l);
    }

    public static void quicksort(int[] a, int n)
    {
        quicksort_recurse(a, 0, n - 1);
    }
}