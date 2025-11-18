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
 * Models a multi fixed link, where there can be up to 3 different linked paths based on a path array. All code is inherited.
 *
 */
public class MultiFixedLink extends AbstractMultiLink implements Crossable {
	//Creates a multi fixed link object.
	public MultiFixedLink(PointPair[] pairs)
	{
		super(pairs) ;
		
	}

}


