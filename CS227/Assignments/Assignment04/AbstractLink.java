package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PositionVector;

/*
 * @author Evan Litzer
 * 
 * Models an AbstractLink, representing the parent class of every link class/object.
 */

public abstract class AbstractLink implements Crossable {

	/**
	 * Shifts the points of a link based on positionVector points to simulate the train moving from one
	 * path to another.
	 */
	public void shiftPoints(PositionVector positionVector) 
	{
		Point pointTwo = positionVector.getPointB();

		Point newPoint = getConnectedPoint(pointTwo) ;

		Path otherPath = newPoint.getPath() ;

		
		// checks which way the train moves before setting the points.
		if(newPoint.getPointIndex() == 0)
		{
			positionVector.setPointA(otherPath.getLowpoint());
			positionVector.setPointB(otherPath.getPointByIndex(1));
		}
		else
		{
			positionVector.setPointA(otherPath.getHighpoint());
			positionVector.setPointB(otherPath.getPointByIndex(otherPath.getNumPoints() - 2));
		}
	}
// Gets the connected point in the link based on the passed in point.
	public abstract Point getConnectedPoint(Point point) ; 
	
// Signifies train entering crossing. Does nothing a lot for links.
	public void trainEnteredCrossing() 
	{
		
	}
// Signifies train leaves crossing. Does nothing for a lot of links.
	public void trainExitedCrossing() 
	{
		
	}
// Gets the number of paths 
	public abstract int getNumPaths() ;




}
