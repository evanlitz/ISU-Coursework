package hw3;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

import api.Tile;

/**
 * Utility class with static methods for saving and loading game files.
 */
public class GameFileUtil {
	/**
	 * Saves the current game state to a file at the given file path.
	 * <p>
	 * The format of the file is one line of game data followed by multiple lines of
	 * game grid. The first line contains the: width, height, minimum tile level,
	 * maximum tile level, and score. The grid is represented by tile levels. The
	 * conversion to tile values is 2^level, for example, 1 is 2, 2 is 4, 3 is 8, 4
	 * is 16, etc. The following is an example:
	 * 
	 * <pre>
	 * 5 8 1 4 100
	 * 1 1 2 3 1
	 * 2 3 3 1 3
	 * 3 3 1 2 2
	 * 3 1 1 3 1
	 * 2 1 3 1 2
	 * 2 1 1 3 1
	 * 4 1 3 1 1
	 * 1 3 3 3 3
	 * </pre>
	 * 
	 * @param filePath the path of the file to save
	 * @param game     the game to save
	 */
	public static void save(String filePath, ConnectGame game) {
		try {
			FileWriter writing = new FileWriter(filePath) ;
			BufferedWriter w = new BufferedWriter(writing);
			// TODO: write to file, can use writer.write()
			w.write("" + game.getGrid().getWidth());
			w.write(" ");
			w.write("" + game.getGrid().getHeight());
			w.write(" ");
			w.write("" + game.getMinTileLevel());
			w.write(" ");
			w.write("" + game.getMaxTileLevel());
			int score = (int)game.getScore();
			w.write(" ") ;
			w.write("" + score);
			w.write("\n") ;
			
			for(int x = 0 ; x < game.getGrid().getHeight() ; x++)
			{
				for(int y = 0 ; y < game.getGrid().getWidth() ; y++)
				{
					w.write("" + game.getGrid().getTile(y, x).getLevel()) ;
					if(y != game.getGrid().getWidth() - 1) ;
					{
						w.write(" ") ;
					}
					
				}
				w.write("\n") ;
				
			}
			
			w.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * Loads the file at the given file path into the given game object. When the
	 * method returns the game object has been modified to represent the loaded
	 * game.
	 * <p>
	 * See the save() method for the specification of the file format.
	 * 
	 * @param filePath the path of the file to load
	 * @param game     the game to modify
	 */
	public static void load(String filePath, ConnectGame game) throws FileNotFoundException 
	{
		File f = new File(filePath) ; 
		Scanner scnr = new Scanner(f) ;
		int width = scnr.nextInt()  ;    //error here
		int height = scnr.nextInt();
		int min = scnr.nextInt();
		int max = scnr.nextInt();
		int score = scnr.nextInt();
		game.setGrid(new Grid(width, height)) ;
		game.setMinTileLevel(min) ;
		game.setMaxTileLevel(max) ;
		game.setScore(score) ;
		for(int x = 0 ; x < (int)game.getGrid().getHeight() ; x++)
		{
			//System.out.println("In for loop x " + x) ;
			for(int y = 0 ; y < (int)game.getGrid().getWidth(); y++)
			{
				//System.out.println("In for loop y " + y) ;
				int level = scnr.nextInt();
				Tile t1 = new Tile(level) ;
				game.getGrid().setTile(t1, y, x) ;
				game.getGrid().getTile(y, x).setLevel(level) ;
			}
		
		}
		//System.out.println(width + " " + height + " " + min + " " + max + " " + score) ;
		//System.out.println(game.getGrid()) ;
		scnr.close() ;
		
		
	}
}
