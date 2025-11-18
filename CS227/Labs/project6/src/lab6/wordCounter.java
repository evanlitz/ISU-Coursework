package lab6;

import java.util.Scanner;
import java.io.FileNotFoundException;
import java.io.File ;

public class wordCounter {
	public static void main(String[] args) throws FileNotFoundException
	{
		printAllLines("story.txt") ;
	}
	
	
	private static void oneLine(String line, int number) throws FileNotFoundException
	{
		int count = 0 ;
		Scanner temp = new Scanner(line) ;
		while (temp.hasNext()) 
		{
			count  += 1 ;
			temp.next();
		}
		System.out.println(number + " line: " + count + " words. ") ;
	}
	
	private static void printAllLines(String filename) throws FileNotFoundException
	{
	    int number = 0 ;
		File file = new File(filename);    
	    Scanner scanner = new Scanner(file);
	    while (scanner.hasNextLine())
	    {
	    	String line = scanner.nextLine() ;
	    	number+= 1 ;
	    	oneLine(line, number) ;
	    }
	    scanner.close() ;
	}
}
