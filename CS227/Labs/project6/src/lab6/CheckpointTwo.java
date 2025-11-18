package lab6;
import java.awt.Point;
import java.util.ArrayList;
import java.util.Scanner;
import java.io.FileNotFoundException;
import java.io.File ; 
import plotter.Plotter;
import plotter.Polyline;

public class CheckpointTwo 
{
	public static void main(String[] args) throws FileNotFoundException
	{
		String filename = "hello.txt" ;
		readFile(filename) ;
	}
	
	
	
	
	
	public static Polyline parseOneLine(String line)
	{
		  	line.trim();
			int width = 1 ;
		    Scanner temp = new Scanner(line);  
		    if (temp.hasNext("#") != true && temp.hasNext(" ") != true)
		    {
		    	if (temp.hasNextInt())
		    	{
		    		width = temp.nextInt() ;
		    	}
		    String color = temp.next();
		    
		    while(temp.hasNextInt())
		    {
		    	int x = temp.nextInt();
		    	int y = temp.nextInt();
		    	
		    }
		 }
	}
	public static ArrayList<Polyline> readFile(String filename) throws FileNotFoundException 
	{
		Plotter plotter = new Plotter() ;
		File file = new File(filename) ;
		Scanner scan = new Scanner(file) ;
		ArrayList<Polyline> p3 = new ArrayList<Polyline>() ;
		String line = scan.nextLine();
		line = scan.nextLine();
		while(scan.hasNextLine())
		{
			line = scan.nextLine();
			p3.add(parseOneLine(line)) ;
			
		}
	}
	
}
