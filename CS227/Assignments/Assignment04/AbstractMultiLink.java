package hw4;

import api.Crossable;
import api.Point;
import api.PointPair;
/**
 * 
 * @author Evan Litzer
 * 
 * Models an abstract multi link object, which basically is when there are up to six different paths at a link and you must use pointpair. 
 * 
 * Parent class to MultiFixedLink and MultiSwitchLink.
 *
 */
public abstract class AbstractMultiLink extends AbstractLink implements Crossable {
	
	protected PointPair[] paths ;
	// Creates an abstract multi link object with the array of pairs passed in.
	protected AbstractMultiLink(PointPair[] pairs)
	{
		paths = pairs ;
	}
	
	
	
	// Gets the connected point to whatever point is passed in. Finds index of array first before taking both points out and figuring out which is which.
	@Override
	public Point getConnectedPoint(Point point) 
		// TODO Auto-generated method stub
		{
			// TODO Auto-generated method stub
			int location = 0 ;
			for(int x = 0 ; x < paths.length ; x++)
			{
				if(paths[x].getPointA() == point || paths[x].getPointB() == point)
				{
					location = x ;
				}
			}

			if(paths[location].getPointA() == point)
			{
				return paths[location].getPointB() ;
			}
			if(paths[location].getPointB() == point)
			{
				return paths[location].getPointA() ;
			}

			return null;
		}

	
	// Returns the number of paths.
	@Override
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return paths.length ;
	}
	// gets the array of point pairs so child classes can access.
	protected PointPair[] getPairs()
	{
		return paths ;
	}

}
