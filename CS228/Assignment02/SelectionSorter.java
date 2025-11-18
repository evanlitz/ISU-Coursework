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
 * This class implements the selection sort algorithm. 
 *
 */

public class SelectionSorter extends AbstractSorter
{
	/**
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts  
	 */
	public SelectionSorter(Point[] pts)  
	{
		super(pts) ;
		algorithm = "selection sort";
	}	


	/** 
	 * Apply selection sort on the array points[] of the parent class AbstractSorter.  
	 * 
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
		int jmin ;
		Point temp ;
		for(int x = 0 ; x < points.length - 1 ; x++)
			{
				jmin = x ;
				for(int y = jmin ; y < points.length ; y++)
				{
					if(pointComparator.compare(points[y], points[jmin]) < 1)
					{
						jmin = y ;
					}
				}
				temp = points[x] ;
				points[x] = points[jmin] ;
				points[jmin] = temp ;
			}

		}

}	
