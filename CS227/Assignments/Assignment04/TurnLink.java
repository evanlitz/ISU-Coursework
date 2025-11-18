package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PositionVector;

/**
 * 
 * @author Evan Litzer
 *
 * Models a turnLink, a link between three paths that follows the rules of point A from path A traveling
 * to point C of path C, point B of path B to path A of path A, and point C of path C to point A of path A.
 * 
 *
 *
 *
 */
public class TurnLink extends AbstractLink implements Crossable {
	// Point A on path A
	private Point pointA ;
	// Point B on path B
	private Point pointB ;
	// Point C on path C
	private Point pointC ;
	
	// Assigns points, creates a new TurnLink object.
	public TurnLink(Point point1, Point point2, Point point3)
	{
		pointA = point1 ;
		pointB = point2 ;
		pointC = point3 ;
	}

	@Override
	/*
	 * Gets the point connected to the passed in point in the turnlink.
	 */
	public Point getConnectedPoint(Point point) {
		// TODO Auto-generated method stub
		if(point == pointA)
		{
			return pointC ;
		}
		if(point == pointB)
		{
			return pointA ;
		}
		if(point == pointC)
		{
			return pointA ;
		}
		
		return null ;
	}


	@Override
	/*
	 * Gets the number of paths in the link, returning 3 every time.
	 */
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return 3 ;
	}

}
