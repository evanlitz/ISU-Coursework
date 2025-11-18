
package edu.iastate.cs228.hw2;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * 
 * @author 
 *
 */

import java.io.FileNotFoundException;
import java.util.InputMismatchException;
import java.util.Scanner;


/**
 * 
 * 
 * @author Evan Litzer
 * 
 * This class sorts all the points in an array of 2D points to determine a reference point whose x and y 
 * coordinates are respectively the medians of the x and y coordinates of the original points. 
 * 
 * It records the employed sorting algorithm as well as the sorting time for comparison. 
 *
 */
public class PointScanner  
{
	private Point[] points; 

	private Point medianCoordinatePoint;  // point whose x and y coordinates are respectively the medians of 
	// the x coordinates and y coordinates of those points in the array points[].
	private Algorithm sortingAlgorithm;    


	protected long scanTime; 	       // execution time in nanoseconds. 

	/**
	 * This constructor accepts an array of points and one of the four sorting algorithms as input. Copy 
	 * the points into the array points[].
	 * 
	 * @param  pts  input array of points 
	 * @throws IllegalArgumentException if pts == null or pts.length == 0.
	 */
	public PointScanner(Point[] pts, Algorithm algo) throws IllegalArgumentException
	{
		if(pts == null|| pts.length == 0 )
		{
			throw new IllegalArgumentException ("point array is null or is empty") ;
		}
		points = pts ;
		sortingAlgorithm = algo ;
	}


	/**
	 * This constructor reads points from a file. It also checks if the file exists, if it is valid, what the sorting algorith is and sets it, and reads/sets the 
	 * values in the file to the values in the point array through the point constructor.
	 * 
	 * @param  inputFileName
	 * @throws FileNotFoundException 
	 * @throws InputMismatchException   if the input file contains an odd number of integers
	 */
	protected PointScanner(String inputFileName, Algorithm algo) throws FileNotFoundException, InputMismatchException
	{
		int xcord, ycord ;
		sortingAlgorithm = algo ;
		File file = new File(inputFileName) ;
		Scanner scanner = new Scanner(file) ;
		int count = 0 ;
		while(scanner.hasNextInt())
		{
			scanner.nextInt() ;
			count++ ;
		}										
		scanner.close() ;
		if(count % 2 != 0)
		{
			throw new InputMismatchException("Odd amount of ints") ;
		}
		scanner = new Scanner(file) ;
		points = new Point[count/2] ;
		for(int x = 0 ; x < points.length ; x++)
		{
			xcord = scanner.nextInt() ;
			ycord = scanner.nextInt() ;
			points[x] = new Point(xcord, ycord) ;
		}

		scanner.close();
	}



	/**   
	 *  
	 * Based on the value of sortingAlgorithm, creates an object of SelectionSorter, InsertionSorter, MergeSorter,
	 * or QuickSorter to carry out sorting. Carries out two rounds of sorting using the designated algorithm to find median x and y coordinates before
	 * creating a medianCoordinatePoint using the point constructor and the two coordinate values. Also calculates scanTime, the amount of time taken to sort the array.     
	 * @param algo
	 * @return
	 */
	public void scan()
	{

		AbstractSorter aSorter; 

		if(sortingAlgorithm == Algorithm.SelectionSort)
		{
			aSorter = new SelectionSorter(points) ;
		}
		else if(sortingAlgorithm == Algorithm.InsertionSort)
		{
			aSorter = new InsertionSorter(points) ;
		}
		else if(sortingAlgorithm == Algorithm.QuickSort)
		{
			aSorter = new QuickSorter(points) ;
		}
		else if(sortingAlgorithm == Algorithm.MergeSort)
		{
			aSorter = new MergeSorter(points) ;
		}
		else
		{
			aSorter = null ;
		}

		aSorter.setComparator(0) ;
		long start = System.nanoTime();
		aSorter.sort() ;
		long end = System.nanoTime() ;
		scanTime += (end - start) ;
		int medianX = points[points.length / 2].getX() ;

		aSorter.setComparator(1) ;
		start = System.nanoTime();
		aSorter.sort() ;
		end = System.nanoTime() ;
		scanTime += (end - start) ;
		int medianY = points[points.length / 2].getY() ;

		medianCoordinatePoint = new Point(medianX, medianY) ;

	}


	/**
	 * Outputs performance statistics in the format: 
	 * <sorting algorithm> <size>  <time>
	 * For instance, selection sort   1000	  9200867
	 */
	public String stats()
	{
		return sortingAlgorithm + "		" + points.length + "	" + scanTime ;  
	}


	/**
	 * Displays/prints the coordinates of the median coordinate point calculated through sorting.
	 */
	@Override
	public String toString()
	{
		return "MCP: (" + medianCoordinatePoint.getX() + ", " + medianCoordinatePoint.getY() + ")" ;
	}


	/**
	 *  
	 * This method, called after scanning, writes point data into a file by outputFileName. The format 
	 * of data in the file is the same as printed out from toString().  The file can help you verify 
	 * the full correctness of a sorting result and debug the underlying algorithm. 
	 * 
	 * @throws FileNotFoundException
	 */
	public void writeMCPToFile() throws FileNotFoundException
	{
		FileWriter writer ;
		String outputFilename = "" ;
		Scanner scanner = new Scanner(System.in) ;
		System.out.println("Enter the output file name: ");					
		try {
				outputFilename = scanner.next() ;
		}
		catch (InputMismatchException e)
		{
			System.out.println("Enter a valid file name.");
		}
		

		try
		{
			writer = new FileWriter(outputFilename) ;
			String data = toString();
			writer.write(data) ;
			writer.flush() ;
			writer.close() ;
		}
		catch (IOException e)
		{
			System.out.println("ERROR");
		}
		scanner.close() ;
	}	




}
