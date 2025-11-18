package edu.iastate.cs228.hw2;

import java.io.FileNotFoundException;
import java.util.InputMismatchException;
import java.util.Random;
import java.util.Scanner;

/**
 *  
 * @author Evan Litzer
 *
 */

public class CompareSorters 
{
	/**
	 * Prompts user on which option to input for type of input array (or exit), before
	 * Repeatedly taking integer sequences either randomly generated or read from files. 
	 * Use them as coordinates to construct points.  Scan these points with respect to their 
	 * median coordinate point four times, each time using a different sorting algorithm. 
	 * Prints out results of time taken to sort using each algorithm.
	 *   
	 * 
	 * @param args
	 **/
	public static void main(String[] args) throws FileNotFoundException
	{		
		boolean done = true ;
		String fileName = "" ;
		Point[] points = null  ;
		int numPts = 0 ;
		int option = 0 ;
		int count = 1 ;
		System.out.println("Performances of Four Sorting Algorithms in Point Scanning");
		System.out.println();
		Scanner scanner = null ;
		while(done == true)
		{
			scanner = new Scanner(System.in) ;
			Random rand = new Random() ;
			System.out.println("keys: 1 (random integers) 2(file input) 3(exit)");
			System.out.print("Trial " + count + ": ");
			try 
			{
				option = scanner.nextInt() ;					//input mismatch
			}
			catch (InputMismatchException e)
			{
				System.out.println("ERROR: INVALID NUMBER ENTERED!") ;
			}
			if(option == 1)
			{
				System.out.print("Enter number of random points: ");
				try
				{
					numPts = scanner.nextInt() ;				// input mismatch + more than 1
				}
				catch (InputMismatchException e)
				{
					System.out.println("Enter a valid number.") ;
					break ;
				}
				if (numPts < 1)
				{
					scanner.close() ;
					System.out.println("Enter a number bigger than 1.") ;
					break ;
				}
				else
				{
					count++ ;
					points = generateRandomPoints(numPts, rand) ;
				}
			}
			else if(option == 2)
			{
				System.out.println("Points from a file");
				System.out.print("File name: ");
				fileName = scanner.next();
			}
			else if(option == 3)
			{
				System.out.println("Goodbye.");
				done = false ;
			}
			else
			{
				System.out.println("Enter one of the three valid numbers.");
			}


			PointScanner[] scanners = new PointScanner[4]; 

			if(option == 1)
			{
				scanners[0] = new PointScanner(points, Algorithm.MergeSort) ;
				scanners[0].scan() ;
				System.out.println("algorithm	size	time (ns)") ;
				System.out.println("----------------------------------") ;
				System.out.println(scanners[0].stats());
				scanners[1] = new PointScanner(points, Algorithm.SelectionSort) ;
				scanners[1].scan() ;
				System.out.println(scanners[1].stats());
				scanners[2] = new PointScanner(points, Algorithm.QuickSort) ;
				scanners[2].scan() ;
				System.out.println(scanners[2].stats());
				scanners[3] = new PointScanner(points, Algorithm.InsertionSort) ;
				scanners[3].scan() ;
				System.out.println(scanners[3].stats());
				System.out.println("----------------------------------") ;
			}
			else if(option == 2)
			{
				try
				{
					scanners[0] = new PointScanner(fileName, Algorithm.MergeSort) ;
					scanners[0].scan() ;
					System.out.println("algorithm	size	time (ns)") ;
					System.out.println("----------------------------------") ;
					System.out.println(scanners[0].stats());
					scanners[1] = new PointScanner(fileName, Algorithm.SelectionSort) ;
					scanners[1].scan() ;
					System.out.println(scanners[1].stats());
					scanners[2] = new PointScanner(fileName, Algorithm.QuickSort) ;
					scanners[2].scan() ;
					System.out.println(scanners[2].stats());
					scanners[3] = new PointScanner(fileName, Algorithm.InsertionSort) ;
					scanners[3].scan() ;
					System.out.println(scanners[3].stats());
					System.out.println("----------------------------------") ;
				}
				catch (FileNotFoundException e)
				{
					System.out.println("File not found. Please try again.") ;
				}
				count++ ;
			}

		}
		scanner.close() ;

	}


	/**
	 * This method generates a given number of random points.
	 * The coordinates of these points are pseudo-random numbers within the range 
	 * [-50,50] � [-50,50]. Used for randomly generating point coordinates for random arrays.
	 * 
	 * @param numPts  	number of points
	 * @param rand      Random object to allow seeding of the random number generator
	 * @throws IllegalArgumentException if numPts < 1
	 */
	private static Point[] generateRandomPoints(int numPts, Random rand) throws IllegalArgumentException
	{ 
		Point[] arrayPts = new Point[numPts] ;
		for(int x = 0 ; x < numPts; x++)
		{
			int randX = rand.nextInt(101) - 50 ;
			int randY = rand.nextInt(101) - 50 ;
			arrayPts[x] = new Point(randX, randY) ;
		}

		return arrayPts ; 
	}

}
