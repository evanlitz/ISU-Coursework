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
 * This class implements the mergesort algorithm.   
 *
 */

public class MergeSorter extends AbstractSorter
{	
	/** 
	 * Constructor takes an array of points.  It invokes the superclass constructor, and also 
	 * set the instance variables algorithm in the superclass.
	 *  
	 * @param pts   input array of integers
	 */
	public MergeSorter(Point[] pts) 
	{
		super(pts) ;
		algorithm = "Merge sort" ;
	}


	/**
	 * Performs mergesort on the array points[] of the parent class AbstractSorter. 
	 * 
	 * Only a call to mergeSortRec is needed here.
	 */
	@Override 
	public void sort()
	{
		mergeSortRec(points) ;
	}

	
	/**
	 * This is a recursive method that carries out mergesort on an array pts[] of points. One 
	 * way is to make copies of the two halves of pts[], recursively call mergeSort on them, 
	 * and merge the two sorted subarrays into pts[]. Carries out the division part of mergeSort
	 * as the elements are singled out before being sorted again later.
	 * 
	 * @param pts	point array 
	 */
	private void mergeSortRec(Point[] pts)
	{
		
		if (pts.length < 2) {
			return;
		}
		int mid = pts.length / 2;
		Point[] l = new Point[mid];
		Point[] r = new Point[pts.length - mid];

		for (int i = 0; i < mid; i++) {
			l[i] = pts[i];
		}
		for (int i = mid; i < pts.length; i++) {
			r[i - mid] = pts[i];
		}
		mergeSortRec(l);
		mergeSortRec(r);

		merge(pts, l, r, mid, pts.length - mid);

	}

	/*
	 * The merge method sorts and merges back together the points from the right and left arrays multiple times in recursion.
	 * Merge is called until array is sorted and has every element.
	 * 
	 * 
	 * 
	 */
	private void merge(Point[] pts, Point[] l, Point[] r, int left, int right)
	{
		if(Point.xORy == true)
		{
			super.setComparator(0);
		}
		else
		{
			super.setComparator(1);
		}
		int i = 0, j = 0, k = 0;
		while (i < left && j < right) {
			if (pointComparator.compare(l[i] , r[j]) < 0) {							// comparator
				pts[k++] = l[i++];
			} else {
				pts[k++] = r[j++];
			}
		}
		while (i < left) {
			pts[k++] = l[i++];
		}
		while (j < right) {
			pts[k++] = r[j++];
		}
	}

}
