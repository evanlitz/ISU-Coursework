package edu.iastate.cs228.hw2;

import java.io.FileNotFoundException;
import java.lang.NumberFormatException; 
import java.lang.IllegalArgumentException; 
import java.util.InputMismatchException;


/**
 *  
 * @author Evan Litzer
 *
 */

/**
 * 
 * This class implements the version of the quicksort algorithm presented in the lecture, except it sorts the array of points based on x or y.  
 *
 */

public class QuickSorter extends AbstractSorter
{
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *   
	 * @param pts   input array of integers
	 */
	public QuickSorter(Point[] pts)
	{
		super(pts) ;
		algorithm = "Quick sorter" ;
		
	}
		

	/**
	 * Carry out quicksort on the array points[] of the AbstractSorter class.  
	 * 
	 */
	@Override 
	public void sort()
	{
		quickSortRec(0, points.length - 1) ;
	}
	
	
	/**
	 * Operates on the subarray of points[] with indices between first and last. Checks if sorting is over and returns/iniates recursive second part and 
	 * recursively calls itself with updated pivot and first/last values to carry out quickSort.
	 * 
	 * @param first  starting index of the subarray
	 * @param last   ending index of the subarray
	 */
	private void quickSortRec(int first, int last)
	{
		if(first >= last)
		{
			return ;
		}
		int pivot = partition(first, last) ;
		quickSortRec(first, pivot) ;
		quickSortRec(pivot + 1, last) ;
	}
	
	
	/**
	 * Operates on the subarray of points[] with indices between first and last. Carries out swapping and pivot parts
	 * of QuickSort sorting algorithm.
	 * 
	 * @param first
	 * @param last
	 * @return
	 */
	private int partition(int first, int last)
	{
		int midpoint = first + (last-first) / 2 ;
		Point pivot = points[midpoint] ;
		Point temp ;
		if(Point.xORy == true)
		{
			super.setComparator(0);
		}
		else
		{
			super.setComparator(1);
		}
		boolean done = false ;
		while (done == false)
		{
			while(pointComparator.compare(points[first], pivot) < 0)
			{
				first += 1 ;
			}
			while(pointComparator.compare(pivot, points[last]) < 0)
			{
				last -= 1 ;
			}
			if(first >= last)
			{
				done = true ;
			}
			else
			{
				temp = points[first] ;
				points[first] = points[last] ;
				points[last] = temp ;
				first += 1 ;
				last -= 1 ;
			}
		}
		
		return last ;
	}	
}
