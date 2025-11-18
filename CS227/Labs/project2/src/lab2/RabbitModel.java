package lab2;
import java.util.Random;
/**
 * A RabbitModel is used to simulate the growth
 * of a population of rabbits. 
 */
public class RabbitModel
{
  // TODO - add instance variables as needed
  
	private int population ;

	
	
  /**
   * Constructs a new RabbitModel.
   */
  public RabbitModel()
  {
	population = 0 ;
  }  
 
  /**
   * Returns the current number of rabbits.
   * @return
   *   current rabbit population
   */
  public int getPopulation()
  {
    // TODO - returns a dummy value so code will compile
    return population;
  }
  
  /**
   * Updates the population to simulate the
   * passing of one year.
   */
  public void simulateYear()
  {
	Random rand = new Random() ;
	int temp = rand.nextInt(10) ;
	population += temp ;
	temp = 0 ;
	}
	
  
  
  /**
   * Sets or resets the state of the model to the 
   * initial conditions.
   */
  public void reset()
  {
    population = 0 ;
   
  }
}