package lab7;

public class CheckpointOne {

	 public static void main(String[] args)
	  {
	    int[] test = {3, 4, 5, 1, 2, 3, 2}; // sum should be 20
	    int result = arrayMax(test);
	    System.out.println(result);
		 
		 System.out.println(getPyramidCount(3)) ;
	  }
	
	
	
	
	
	 public static int arrayMax(int[] arr)
	 {
		 return arrayMaxRec(arr, 0, arr.length - 1) ;
	 }
	 
	 private static int arrayMaxRec(int[] arr, int start, int end)
	 { 
	 
		 if (start == end)
		 {
			 return arr[start];
		 }
		 else
		 {
			 int mid = (start + end) / 2 ;
			 int leftMax = arrayMaxRec(arr, start, mid) ;
			 int rightMax = arrayMaxRec(arr, mid + 1, end) ;
			 return Math.max(leftMax, rightMax) ;
		 }
		 
	 }
	 
	 
	 
	 private static int getPyramidCount(int level) 
	 {
		 if (level == 0)
		 {
			 return 0 ;
		 }
		 else
		 {
			int low = level * level ;
			int high = getPyramidCount(level - 1) ;
			return low + high ;
		 }
	 }
	 
	 
	 
	 
	 
	 
}
