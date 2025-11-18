package edu.iastate.cs228.hw2;

/**
 *  
 * @author Evan Litzer
 *
 */

import java.util.Comparator;
import java.io.FileNotFoundException;
import java.lang.IllegalArgumentException; 
import java.util.InputMismatchException;

/**
 * 
 * This abstract class is extended by SelectionSort, InsertionSort, MergeSort, and QuickSort.
 * It stores the input (later the sorted) sequence. Includes one constructor and many
 * methods that will lated be implemented by all of the sorting classes. 
 *
 */
public abstract class AbstractSorter
{
	
	protected Point[] points;    // array of points operated on by a sorting algorithm. 
	                             // stores ordered points after a call to sort(). 
	
	protected String algorithm = null; // "selection sort", "insertion sort", "mergesort", or
	                                   // "quicksort". Initialized by a subclass constructor.
		 
	protected Comparator<Point> pointComparator = null;  // The point comparator is used to compare two points
														// based on boolean xORy. 
	
	
	/**
	 * This constructor accepts an array of points as input. Copy the points into the array points[]. 
	 * 
	 * @param  pts  input array of points 
	 * @throws IllegalArgumentException if pts == null or pts.length == 0.
	 */
	protected AbstractSorter(Point[] pts) throws IllegalArgumentException
	{
		if(pts == null || pts.length == 0)
		{
			throw new IllegalArgumentException("Array is empty or null") ;
		}
		
		this.points = new Point[pts.length] ;
		for(int x = 0 ; x < pts.length ; x++)
		{
			this.points[x] = pts[x] ;
		}
		
		
	}
	
	/**
	 * Generates a comparator on the fly that compares by x-coordinate if order == 0, by y-coordinate
	 * if order == 1. Assign the 
     * comparator to the variable pointComparator. 
     *  
	 * 
	 * @param order  0   by x-coordinate 
	 * 				 1   by y-coordinate
	 * 			    
	 * 
	 * @throws IllegalArgumentException if order is less than 0 or greater than 1
	 *        
	 */
	public void setComparator(int order) throws IllegalArgumentException 
	{
		if(order < 0 || order > 1)
		{
			throw new IllegalArgumentException("Order is not 0 or 1.") ;
		}
		
		

		pointComparator = new Comparator<Point>() {

			@Override
			public int compare(Point p1, Point p2) {
				if(order == 0)
				{
					return Integer.compare(p1.getX(), p2.getX());
				}
				else
				{
					return Integer.compare(p1.getY(), p2.getY());
				}
			}
		
		
		} ;
	}

	

	/**
	 * Use the created pointComparator to conduct sorting.  
	 * 
	 * Should be protected. Made public for testing. 
	 */
	public abstract void sort(); 
	
	
	/**
	 * Obtain the point in the array points[] that has median index 
	 * 
	 * @return	median point 
	 */
	public Point getMedian()
	{
		return points[points.length/2]; 
	}
	
	
	/**
	 * Copys the array points[] onto the array pts[]. 
	 * 
	 * @param pts
	 */
	public void getPoints(Point[] pts)
	{	
		for(int x = 0 ; x < points.length ; x++) // Maybe flipped?
		{
			points[x] = pts[x] ;
		}
	}
	

	/**
	 * Swaps the two elements indexed at i and j respectively in the array points[]. 
	 * Forgot about this method, so really just unimplemented.
	 * 
	 * @param i
	 * @param j
	 */
	protected void swap(int i, int j)
	{
		Point temp ;
		temp = points[j] ;
		points[j] = points[i] ;
		points[i] = temp ;
	}	
}
