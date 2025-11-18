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
 * This class implements the insertion sort algorithm.
 *
 */

public class InsertionSorter extends AbstractSorter 
{
	/**
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 * 
	 * @param pts  
	 */
	public InsertionSorter(Point[] pts) 
	{
		super(pts) ;
		algorithm = "insertion sort" ;
	}	


	/** 
	 * Perform insertion sort on the array points[] of the parent class AbstractSorter.  
	 */
	@Override 
	public void sort()
	{
		if(Point.xORy == true)
		{
			super.setComparator(0);
		}
		else
		{
			super.setComparator(1);
		}

		Point temp ;
		for(int x = 0 ; x < points.length ; x++)
		{
			for(int y = x ; y > 0 ; y--)
			{
				if(pointComparator.compare(points[y], points[y-1]) < 0)
				{
					temp = points[y-1] ;
					points[y-1] = points[y] ;
					points[y] = temp ;
				}
			}
		}
	}
}
