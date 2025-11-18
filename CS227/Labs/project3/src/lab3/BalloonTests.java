package lab3;
import static org.junit.Assert.assertEquals;

import org.junit.Test;

import balloon3.Balloon; 

public class BalloonTests {
    // margin of error for floating-point comparisons
    private static final double EPSILON = 10e-07;
	
    @Test
    public void testInitialRadius()
    {
      String msg = "A newly constructed balloon should have the radius of 0";
      Balloon b = new Balloon(5);
      assertEquals(msg, 0.0, b.getRadius(), EPSILON);
    }
    @Test
	public void testPoppedStatus() 
    {
	      String msg = "A popped balloon should be popped";
	      Balloon b = new Balloon(5);
	      b.pop() ;
	      assertEquals(msg, true, b.isPopped());
    }
    
    @Test
	public void testBlow() 
    {
	      String msg = "A newly constructed balloon with maximum radius 5 blown up by 3 units should have a radius of 3";
	      Balloon b = new Balloon(5);
	      b.blow(3) ;
	      assertEquals(msg, 3, b.getRadius(), EPSILON);
    }
	@Test
	public void testDeflate() 
    {
	      String msg = "A balloon blown up with 3 units of air and then deflated should return a radius of 0";
	      Balloon b = new Balloon(5);
	      b.blow(3) ;
	      b.deflate() ;
	      assertEquals(msg, 0, b.getRadius(), EPSILON);
    }
	
	@Test
	public void testTooMuchAir() 
    {
	      String msg = "A balloon with a maximum radius of 5 blown up by 6 units of air should pop";
	      Balloon b = new Balloon(5);
	      b.blow(60) ;
	      assertEquals(msg, true, b.isPopped());
    }
	
	@Test
	public void testInitialPop() 
    {
	      String msg = "A newly constructed balloon should not be popped";
	      Balloon b = new Balloon(5);
	      assertEquals(msg, false, b.isPopped());
    }
	
	@Test
	public void testBlowPop() 
    {
	      String msg = "A popped balloon can not be blown up anymore.";
	      Balloon b = new Balloon(5);
	      b.pop() ;
	      b.blow(3);
	      assertEquals(msg, 0, b.getRadius());
    }
	
	@Test
	public void testNegativeBlow() 
    {
	      String msg = "A newly constructed balloon should maintain a radius of 0 if the amount of air advised is negative";
	      Balloon b = new Balloon(5);
	      b.blow(-3);
	      assertEquals(msg, 0, b.getRadius());
    }
	
    @Test
	public void testPoppedStatusRadius() 
    {
	      String msg = "A popped balloon should have a radius of 0";
	      Balloon b = new Balloon(5);
	      b.blow(4) ;
	      b.pop() ;
	      assertEquals(msg, 0.0, b.getRadius(), EPSILON);
    }
    
	@Test
	public void testDeflatePop() 
    {
	      String msg = "A balloon blown up with 3 units of air and then deflated should not be popped";
	      Balloon b = new Balloon(5);
	      b.blow(3) ;
	      b.deflate() ;
	      assertEquals(msg, false, b.isPopped());
    }
    
	@Test
	public void testBlownUp() 
    {
	      String msg = "A balloon blown up with maximum units of air should not be popped";
	      Balloon b = new Balloon(5);
	      b.blow(5) ;
	      assertEquals(msg, false, b.isPopped());
    }
	
	@Test
	public void testMultiple() 
    {
	      String msg = "Multiple inflations/deflations";
	      Balloon b = new Balloon(5);
	      b.blow(3) ;
	      b.blow(2);
	      assertEquals(msg, 5.0, b.getRadius(), EPSILON);
    }
	
	@Test
	public void testConstructor() 
    {
	      String msg = "Balloons initalized with a radius of 0 should not be popped";
	      Balloon b = new Balloon(0);
	      assertEquals(msg, false, b.isPopped());
    }
	
	@Test
	public void testConstructorAgain() 
    {
	      String msg = "Balloons initalized with a negative radius should have a radious of 0";
	      Balloon b = new Balloon(-5);
	      assertEquals(msg, 0.0, b.getRadius(), EPSILON);
    }
	
	
}
