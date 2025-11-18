import org.junit.Test;
import static org.junit.Assert.*;
import java.util.*;

public class PrimeNumberFinderTest {

  @Test(timeout = 4000)
  public void test00() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer((-2479));
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals((-2479), int0);
  }

  @Test(timeout = 4000)
  public void test01() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer((-2479));
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals((-2479), int0);
  }

  @Test(timeout = 4000)
  public void test02() throws Throwable {
      int int0 = PrimeNumberFinder.computeSumOfPrimes((List<Integer>) null);
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test03() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer(0);
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test04() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer(3);
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals(3, int0);
  }

  @Test(timeout = 4000)
  public void test05() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer(6);
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals(6, int0);
  }

  @Test(timeout = 4000)
  public void test06() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer((-5));
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals((-5), int0);
  }

  @Test(timeout = 4000)
  public void test07() throws Throwable {
      LinkedList<Integer> linkedList0 = new LinkedList<Integer>();
      Integer integer0 = new Integer(1);
      linkedList0.add(integer0);
      int int0 = PrimeNumberFinder.computeSumOfPrimes(linkedList0);
      assertEquals(1, int0);
  }

  @Test(timeout = 4000, expected = ArrayIndexOutOfBoundsException.class)
  public void test08() throws Throwable {
      List<Integer> list0 = List.of();
      PrimeNumberFinder.computeSumOfPrimes(list0);
  }

  @Test(timeout = 4000)
  public void test09() throws Throwable {
      boolean boolean0 = PrimeNumberFinder.isPrime(3);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test10() throws Throwable {
      boolean boolean0 = PrimeNumberFinder.isPrime(2);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test11() throws Throwable {
      boolean boolean0 = PrimeNumberFinder.isPrime(1);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test12() throws Throwable {
      boolean boolean0 = PrimeNumberFinder.isPrime((-1));
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test13() throws Throwable {
      boolean boolean0 = PrimeNumberFinder.isPrime(0);
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test14() throws Throwable {
      List<Integer> list0 = PrimeNumberFinder.findPrimes((-1), (-1));
      assertTrue(list0.isEmpty());
  }

  @Test(timeout = 4000)
  public void test15() throws Throwable {
      List<Integer> list0 = PrimeNumberFinder.findPrimes(2, 2);
      assertTrue(list0.contains(2));
  }

  @Test(timeout = 4000)
  public void test16() throws Throwable {
      List<Integer> list0 = PrimeNumberFinder.findPrimes(1, 3);
      assertEquals(3, (int) list0.get(1));
      assertEquals(2, (int) list0.get(0));
  }

  @Test(timeout = 4000)
  public void test17() throws Throwable {
      List<Integer> list0 = PrimeNumberFinder.findPrimes((-3), 0);
      assertTrue(list0.isEmpty());
  }

  @Test(timeout = 4000, expected = ArrayIndexOutOfBoundsException.class)
  public void test18() throws Throwable {
      List<Integer> list0 = List.of();
      PrimeNumberFinder.computeSumOfPrimes(list0);
  }
}
