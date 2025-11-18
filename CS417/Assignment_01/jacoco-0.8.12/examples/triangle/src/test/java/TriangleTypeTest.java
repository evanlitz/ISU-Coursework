// Introduction to Software Testing
// Authors: Paul Ammann & Jeff Offutt
// Chapter 6; page ??
// JUnit for TriangleType.java

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameters;
import static org.junit.Assert.*;
import java.util.*;

@RunWith(Parameterized.class)
public class TriangleTypeTest {
    public int x;
    public int y;
    public int z;
    public Triangle t;

    public TriangleTypeTest (int x, int y, int z, Triangle t) {
       this.x = x; this.y = y; this.z = z; this.t = t;
    }

   @Parameters public static Collection<Object[]> parameters() {
        List<Object[]> list = new ArrayList<Object[]>();
        list.add(new Object[] {0, 1, 2, Triangle.INVALID});
        list.add(new Object[] {4, 2, 2, Triangle.INVALID});
        list.add(new Object[] {2, 2, 2, Triangle.EQUILATERAL});
        return list;
    }

   @Test public void triangleTest() { 
      assertEquals(t,TriangleType.triangle(x, y, z)); 
   }
}


