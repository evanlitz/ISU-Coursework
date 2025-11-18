package hw4;

import api.Crossable;
import api.Path;
import api.Point;
import api.PointPair;
import api.PositionVector;
/**
 * 
 * @author Evan Litzer
 * 
 * 
 * Models a multi switch link, which can link up to three different sets of paths. Has a switch that determines which pair of paths train is running on.
 *
 */
public class MultiSwitchLink extends AbstractMultiLink implements Crossable {
	
	// Tracks whether cross is in progress or not, preventing change in switching connection.
	private boolean inProgress ;
	// Creates a multi switch link object, passing in the array of pairs and initalizing inProgress to false. 
	public MultiSwitchLink(PointPair[] pairs)
	{
		super(pairs) ;
		inProgress = false ;
	}

	// States whether the train has entered the crossing, making the switch true and not allowing any switching of connection.
	@Override
	public void trainEnteredCrossing() {
		// TODO Auto-generated method stub
		inProgress = true ;
	}
	// States that train has exited crossing, allowing switch to be used again.
	@Override
	public void trainExitedCrossing() {
		// TODO Auto-generated method stub
		inProgress = false ;
	}
	// Switches the connection of paths in the link, choosing a new pointpair. 
	public void switchConnection(PointPair pair, int index)
	{
		if(inProgress == false)
		{
			getPairs()[index] = pair ;
		}
	}

}
