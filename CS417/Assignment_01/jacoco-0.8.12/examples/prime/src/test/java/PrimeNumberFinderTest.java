import org.junit.Test;
import static org.junit.Assert.*;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays; 

/*sample tests for homework. you will need to add to these */

public class PrimeNumberFinderTest{

    //Instantiate class - this will cover the constructor of the class
    @Test
    public void instantiateClass(){
      PrimeNumberFinder myPrime=new PrimeNumberFinder();
    }

    
    //Tests for the findPrimes method (you can add to these)
    @Test
    public void testFindPrimes1() {
       List<Integer> primes = PrimeNumberFinder.findPrimes(2,8);
       List<Integer> expected = Arrays.asList(2,3,5,7);
       assertArrayEquals(expected.toArray(),primes.toArray());
    }

    //test for isPrime
   @Test
    public void testIsPrime1() {
        assertTrue(PrimeNumberFinder.isPrime(23));
    }

    //test for a non-prime number
    @Test
    public void testIsPrime2() {
        assertFalse(PrimeNumberFinder.isPrime(10));
    }
    
    //tests for the sumofP method - note the list provided is the list of primes
    // to be summed - not the lower and upper bound

    @Test
    public void sumofP1() {
	List<Integer> input = Arrays.asList(5,7);
	assertEquals(12,PrimeNumberFinder.computeSumOfPrimes(input));
    }

    @Test
    public void negNumbers() {
        assertFalse(PrimeNumberFinder.isPrime(-17));
        assertFalse(PrimeNumberFinder.isPrime(-1));
        assertFalse(PrimeNumberFinder.isPrime(0));
        assertFalse(PrimeNumberFinder.isPrime(1));
    }

    @Test
    public void divideByTwoIsNotPrime()
    {
        assertFalse(PrimeNumberFinder.isPrime(4));
        assertFalse(PrimeNumberFinder.isPrime(6));
        assertFalse(PrimeNumberFinder.isPrime(100));
    }

    @Test
    public void divideByThreeIsNotPrime()
    {
        assertFalse(PrimeNumberFinder.isPrime(9));
        assertFalse(PrimeNumberFinder.isPrime(27));
        assertFalse(PrimeNumberFinder.isPrime(99));
    }


    @Test
    public void compositeCaughtByLoop_iBranch() { 
        assertFalse(PrimeNumberFinder.isPrime(25)); 
        assertFalse(PrimeNumberFinder.isPrime(121)); 
    }

    @Test 
    public void compositeCaughtByLoop_iPlus2Branch() { 
        assertFalse(PrimeNumberFinder.isPrime(49));  
        assertFalse(PrimeNumberFinder.isPrime(77));  
    }

    @Test 
    public void smallPrimesTrue() { 
        assertTrue(PrimeNumberFinder.isPrime(2));
        assertTrue(PrimeNumberFinder.isPrime(3));
        assertTrue(PrimeNumberFinder.isPrime(5));
        assertTrue(PrimeNumberFinder.isPrime(7));
    }

    @Test 
    public void noLoopEntryStillPrime() { 
        assertTrue(PrimeNumberFinder.isPrime(23)); 
    }

    @Test
    public void loopRunsButRemainsPrime_singleIter() { 
        assertTrue(PrimeNumberFinder.isPrime(29)); 
    }

    @Test
    public void loopRunsMultipleIters_prime() { 
        assertTrue(PrimeNumberFinder.isPrime(97));   
        assertTrue(PrimeNumberFinder.isPrime(9973)); 
    }

    @Test
    public void sumprimes_true_getFirstElement() {
        int sum = PrimeNumberFinder.computeSumOfPrimes(Arrays.asList(2, 3));
        assertEquals(5, sum);
    }

    @Test
    public void sumsingleprime_falseBranch() {
        int sum = PrimeNumberFinder.computeSumOfPrimes(Arrays.asList(2));
        assertEquals(2, sum);
    }

    @Test
    public void sumprimes_emptyList_falsereturnzero() {
        List<Integer> empty = new ArrayList<>(); 
        int sum = PrimeNumberFinder.computeSumOfPrimes(empty);
        assertEquals(0, sum);
    }

    @Test
    public void sumMultiplePrimes_true_multipleAdds() {
        int sum = PrimeNumberFinder.computeSumOfPrimes(Arrays.asList(2, 3, 5, 7));
        assertEquals(17, sum);
    }

}