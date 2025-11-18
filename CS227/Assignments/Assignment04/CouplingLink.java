package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PositionVector;

/**
 * 
 * @author Evan Litzer
 * 
 * Models a coupling link, which links two paths together. 
 *
 */
public class CouplingLink extends AbstractLink implements Crossable {

	
	// Points signifying high and low points.
	private Point pointA ;
	private Point pointB ;

	// Creates a new couplingLink object.
	public CouplingLink(Point point1, Point point2)
	{
		pointA = point1 ;
		pointB = point2 ;

	}
	
	/**
	 * Gets the connected point of the point passed in.
	 */
	@Override
	public Point getConnectedPoint(Point point) {
		// TODO Auto-generated method stub
		if(point == pointB)
		{
			return pointA ;
		}
		if(point == pointA)
		{
			return pointB ;
		}

		return null ;
	}

	
	/**
	 * Returns the number of paths in a coupling link, always being two.
	 */
	@Override
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return 2 ;
	}











}
