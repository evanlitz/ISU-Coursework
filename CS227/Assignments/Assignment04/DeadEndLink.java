package hw4;

import api.Crossable;
import api.Point;
import api.PositionVector;
/**
 * 
 * @author Evan Litzer
 * 
 * Models a dead end link, which links a path to nothing.
 *
 */
public class DeadEndLink extends AbstractLink implements Crossable 
{

	// @Override Doesn't do anything as there is nowhere to shift the points to. 
	public void shiftPoints(PositionVector positionVector) {
		// TODO Auto-generated method stub
		// does nothing
	}

	// @Override Doesn't do anything as there is no connected point for a dead end. Returns null always.
	public Point getConnectedPoint(Point point) {
		// TODO Auto-generated method stub
		// doesn't connect to anything
		return null ;
	}

	// @Override Returns one path as there is always only one path in a dead end link.
	public int getNumPaths() {
		// TODO Auto-generated method stub
		return 1 ;
	}
	
}
