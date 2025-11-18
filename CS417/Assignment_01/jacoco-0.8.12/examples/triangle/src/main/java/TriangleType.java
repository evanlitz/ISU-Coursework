//Introduction to Software Testing
//Authors: Paul Ammann & Jeff Offutt
//modified by M.Cohen for class exercise
//Chapter 6;
// See TriangleTypeTest for Junit tests




public class TriangleType
{
     /**
     * @param s1, s2, s3:  sides of the putative triangle
     * @return enum describing type of triangle
     */
   public static Triangle triangle (int s1, int s2, int s3)
   {
      // Reject non-positive sides
      if (s1 <= 0 || s2 <= 0 || s3 <= 0)
         return (Triangle.INVALID);

      // Check triangle inequality
      if (s1+s2 <= s3 || s2+s3 <= s1 || s1+s3 <= s2)
         return (Triangle.INVALID);

      // Identify equilateral triangles
      if ((s1 == s2) && (s2 == s3))
         return Triangle.EQUILATERAL;

      // Identify isosceles triangles
      // original program line is below (correct version) 
      // if ((s1 == s2) || (s2 == s3) || (s1 == s3))

      //fault introduced below by M.Cohen
       if ((s1 == s3) || (s2 == s3) || (s1 == s3))
         return Triangle.ISOSCELES;

      return (Triangle.SCALENE);
   } 
}
