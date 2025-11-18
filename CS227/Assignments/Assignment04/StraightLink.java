package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PositionVector;
/**
 * 
 * @author Evan Litzer
 * 
 * Models a straight link, which links together three paths without a switch but with specific rules regarding where the trains go. 
 *
 */
public class StraightLink extends AbstractLink implements Crossable {
	
	private Point pointA ;
	private Point pointB ;
	private Point pointC ;
	
	// Creates a straight link object.
	public StraightLink(Point point1, Point point2, Point point3)
	{
		pointA = point1 ;
		pointB = point2 ;
		pointC = point3 ;
	}
	
	// Gets connected point to whatever point is passed in. Since Path A --> Path B, Path B --> Path A, Path C --> Path A, follows rule correctly in order
	// to allow for train to operate properly.
	@Override
	public Point getConnectedPoint(Point point) {
		// TODO Auto-generated method stub
		
		if(point == pointA)
		{
			return pointB ;
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

	// Returns the number of paths in the link. There are always three paths, so returns 3.
	@Override
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return 3 ;
	}

}
