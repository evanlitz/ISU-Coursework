package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PositionVector;


/**
 * 
 * @author Evan Litzer
 * 
 * Models a switch link object, which is the link between three paths with a switch that directs which path connects with which.
 *
 */
public class SwitchLink extends AbstractLink implements Crossable {

	private Point pointA ;
	private Point pointB ;
	private Point pointC ;
	private boolean turn ;
	private boolean inProgress ;
	
	
	// Creates a switch link object.
	public SwitchLink(Point pointOne, Point pointTwo, Point pointThree)
	{
		pointA = pointOne ;
		pointB = pointTwo ;
		pointC = pointThree ;
	}

	
	// Gets the connected point to the point that is passed in. Based on the switch and which point is which.
	@Override
	public Point getConnectedPoint(Point point) {
		// TODO Auto-generated method stub
		
		if(point == pointA && turn == true)
		{
			return pointC ;
		}
		if(point == pointA && turn == false)
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

	
	// Represents train entering the crossing, which means switch cannot be activated.
	@Override
	public void trainEnteredCrossing() {
		// TODO Auto-generated method stub
		inProgress = true ;
	}

	
	// Represents train exiting crossing, which means switch can now be activated.
	@Override
	public void trainExitedCrossing() {
		// TODO Auto-generated method stub
		inProgress = false ;
	}

	
	// Returns the number of paths in the link, in this case always being three.
	@Override
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return 3 ;
	}
	
	
	// Sets the switch to true or false.
	public void setTurn(boolean indicate)
	{
		if(inProgress == false)
		{
			turn = indicate ;
		}
	}
	
}
