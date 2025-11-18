package lab7;

import java.io.File;

public class CheckpointTwo 
{

	public static void main(String[] args)
	  {
		File rootDirectory = new File(".");
		System.out.println(countFiles(rootDirectory));
		System.out.println(countPatterns(5));
		
		
		
	  }
	
	public static int countFiles(File f) 
	{
		if (f.isFile())
		{
			return 1 ;
		}
		else if (f.isDirectory())
		{
			int number = 0 ;
			File[] files = f.listFiles();
			for (File f1 : files)
			{
				number += countFiles(f1) ;
			}
			return number ;
		}
		else
		{
			return 0 ;
		}		
	}
	
	public static int countPatterns(int n)
	{
		if (n == 2)
		{
			return 2 ;
		}
		if (n < 0)
		{
			return 0 ;
		}
		else 
		{ 
	        return countPatterns(n-1) + countPatterns(n-3);
	    }
	}
}
