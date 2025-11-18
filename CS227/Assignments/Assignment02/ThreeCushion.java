package hw2;

import api.PlayerPosition;
import api.BallType;
import static api.PlayerPosition.*;
import static api.BallType.*;

/**
 * Class that models the game of three-cushion billiards.
 * 
 * @author Evan Litzer
 */


public class ThreeCushion {
	/**
	 * Player A's score.
	 */
	private int playerAScore ;
	/**
	 * Player B's score.
	 */
	private int playerBScore ;
	/**
	 * Inning number.
	 */
	private int inning ;
	/**
	 * Keeps track of whether the shot is still valid or not.
	 */
	private boolean isShotValid ;
	/**
	 * Keeps track of whether the current shot is the break shot.
	 */
	private boolean breakShot ;
	/**
	 * Keeps track of whether the current inning has started or not.
	 */
	private boolean inningStarted ;
	/**
	 * Keeps track of whether the current shot has started.
	 */
	private boolean shotStarted ;
	/**
	 * Keeps track of whether the current shot has met the requirements of a bank shot. 
	 */
	private boolean bankShot ;
	/**
	 * Keeps track of the status of the game being over or not.
	 */
	private boolean gameOver ;
	/**
	 * Placeholder for the amount of points needed to win the game.
	 */
	private int pointsToWin ;
	/**
	 * Player that is currently taking the shots.
	 */
	private PlayerPosition currentPlayer ;
	/**
	 * Cueball of the current player that is shooting.
	 */
	private BallType currentCueBall ;
	/**
	 * Cueball of Player A.
	 */
	private BallType PAcueBall ;
	/**
	 * Cueball of Player B.
	 */
	private BallType PBcueBall ;
	/**
	 * Tracks whether a lagWinner has been chosen or not, signifying start of the game.
	 */
	private boolean SGupdate ;
	/**
	 * Tracks amount of times the cueball has hit a cushion.
	 */
	private int cushion ;
	/**
	 * Placeholder for the first ball that was hit by the cueball.
	 */
	private BallType ball1 ;
	/**
	 * Placeholder for the second ball that was hit by the cueball
	 */
	private BallType ball2 ;
	/**
	 * Tracks the condition of a bankshot regarding three cushions being hit in a shot.
	 */
	private boolean threeCushion ;
	/**
	 * Tracks the condition of a bankshot regarding two different balls being hit.
	 */
	private boolean twoBall ;
	/**
	 * The lagWinner who chooses who takes the break shot and what color cue ball they desire.
	 */
	private PlayerPosition lagWinner ;
	/**
	 * Tracks whether if Player A has committed a foul before shot has been reset. 
	 * Comes in handy when other player takes a shot when previous shot hasn't ended.
	 */
	private boolean PAerror ;
	/**
	 * Tracks whether if Player B has committed a foul before shot has been reset. 
	 * Comes in handy when other player takes a shot when previous shot hasn't ended.
	 */
	private boolean PBerror ;
	
	/**
	 * @param lagWin
	 * @param points
	 * 
	 * Constructs a new three cushion billiards game with preset lagwinner and amount of points needed to win. 
	 * Inning is set to 1, gameOver is set to false to signify a new game, most inital updates are set to false.
	 * Break shot is set to true as it is first shot of a game.
	 * Scores are reset to 0, along with cushion variable.
	 * All objects are set to null besides the lagWinner.
	 * 
	 * 
	 * 
	 */
	public ThreeCushion(PlayerPosition lagWin, int points) 
	{
		pointsToWin = points ;
		lagWinner = lagWin ;
		inning = 1 ;
		gameOver = false ;
		SGupdate = false ;
		isShotValid = false ;
		breakShot = true ;
		cushion = 0 ;
		playerAScore = 0 ;
		playerBScore = 0 ;
		bankShot = false ;
		ball1 = null ;
		ball2 = null ;
		shotStarted = false ;
		PAcueBall = null ;
		PBcueBall = null ;
		threeCushion = false ;
		twoBall = false ;
		inningStarted = false ;
		PAerror = false ;
		PBerror = false ;
		
	}
	
	/**
	 * Mutator method that simulates the cueball hitting a cushion. 
	 * If it is the break shot first hit, it is a foul.
	 * Cushion variable keeps track of amount of times hit.
	 */
	public void cueBallImpactCushion()
	{
		if(isShotValid == true && gameOver == false)
			{
				if(breakShot == false)
				{
					cushion += 1 ;	
				}
				else
				{
					foul() ;
				}
				if(cushion >= 3 && ball1 == null)
				{
					threeCushion = true ;
				}
			}
		
		
	}
	
	/**
	 * @param ball
	 * 
	 * Mutator method that simulates the cueball striking another ball.
	 * If it is the break shot, the ball hit must be red.
	 * Objects ball1 and ball2 keep track of previous balls hit.
	 * 
	 * 
	 */
	public void cueBallStrike(BallType ball)
	{
		if(isShotValid == true && gameOver == false && SGupdate == true)
		{
			if(breakShot == true)
			{
				if(ball != RED)
				{
					foul() ;
				}
				breakShot = false ;
			}
			if(ball1 == null && ball2 == null)
			{
				ball1 = ball ;
			}
			else if(ball2 == null && cushion >= 3)
			{
				if(ball1 != ball)
				{
					ball2 = ball ;
					twoBall = true ;
				}
			}

			 
		}
		
		
		
		
		
		
		
	}
	
	/**
	 * @param ball
	 * 
	 * Mutator method that simulates the cue stick striking the cue ball. 
	 * If the cue ball is not the ball struck, then it is a foul.
	 * Game must be going on and started, while all other shots must be ended.
	 * inningStarted is set to true if shot is valid.
	 * 
	 * 
	 * 
	 */
	public void cueStickStrike(BallType ball)
	{
		bankShot = false ;
		if(SGupdate == true && gameOver == false)
		{
			if(shotStarted == false)
			{
				inningStarted = true ;
				if(currentCueBall == ball)
				{
					shotStarted = true ;
					isShotValid = true ;
				}
				else 
				{
					foul() ;
				}
				
			}
			else 
			{
				foul() ;
			}
		}
		else
		{
			inningStarted = false ;
		}
			
		
	}
	
	/**
	 * Mutator method that simulates the end of a shot.
	 * If conditions of a bank shot have been met, then bankShot is set to true.
	 * breakShot and shotStarted are set to false while other variables are reset for other shots.
	 * Suffices if a point is scored if conditions are met, otherwise other player is up and inning increments.
	 * 
	 */
	public void endShot()
	{
		if(twoBall == true && threeCushion == true)
		{
			bankShot = true ;
		}
		
		breakShot = false ;
		shotStarted = false ;
		if(isShotValid == true)
		{
			if(cushion >= 3 && ball1 != null && ball2 != null)
			{
				if(currentPlayer == PLAYER_A)
				{
					playerAScore += 1 ;
					if(playerAScore == pointsToWin)
					{
						gameOver = true ;
					}
				}
				else if(currentPlayer == PLAYER_B)
				{
					playerBScore += 1 ;
					if(playerBScore == pointsToWin)
					{
						gameOver = true ;
					}
				}
			}
			else
			{
				inning += 1 ;
				inningStarted = false ;
				if(currentPlayer == PLAYER_A)
				{
					currentPlayer = PLAYER_B ;
					currentCueBall = PBcueBall ;
				}
				else if(currentPlayer == PLAYER_B)
				{
					currentPlayer = PLAYER_A ;
					currentCueBall = PAcueBall ;
				
				}
			}

		}
		ball1 = null ;
		ball2 = null ;
		cushion = 0 ;
		twoBall = false ;
		threeCushion = false ;
		PBerror = false ;
		PAerror = false ;
	}
		
		
	
	
	/**
	 * Mutator method that simulates a foul occuring during a shot.
	 * Increments inning and swtiches players/cue-balls as inning is over.
	 * PAerror and PBerror track if player took shot during another shot, resulting in foul.
	 * isShotValid makes sure that only one foul is called for each turn.
	 * 
	 * 
	 * 
	 */
	public void foul()
	{
		if(isShotValid == true && gameOver == false && SGupdate == true)
		{
			inningStarted = false ;
			isShotValid = false ;
			inning += 1 ;
			if(currentPlayer == PLAYER_A)
			{
				currentPlayer = PLAYER_B ;
				currentCueBall = PBcueBall ;
				PAerror = true ;
			}
			else if(currentPlayer == PLAYER_B)
			{
				currentPlayer = PLAYER_A ;
				currentCueBall = PAcueBall ;
				PBerror = true ;
			
			}
		}
		else if(shotStarted == false && gameOver == false && SGupdate == true)
		{
			inningStarted = false ;
			inning += 1 ;
			if(currentPlayer == PLAYER_A)
			{
				currentPlayer = PLAYER_B ;
				currentCueBall = PBcueBall ;
			}
			else if(currentPlayer == PLAYER_B)
			{
				currentPlayer = PLAYER_A ;
				currentCueBall = PAcueBall ;
			}
		}
		else if(isShotValid == false && gameOver == false && SGupdate == true)
		{
			if(currentPlayer == PLAYER_A)
			{
				if(PBerror == true)
				{
					currentPlayer = PLAYER_B ;
					currentCueBall = PBcueBall ;
					inning += 1 ;
					inningStarted = false ;
				}
			}
			else if(currentPlayer == PLAYER_B)
			{
				if(PAerror == true)
				{
					currentPlayer = PLAYER_A ;
					currentCueBall = PAcueBall ;
					inning += 1 ;
					inningStarted = false ;
				}
			}
		}
		
	}
	
	/**
	 * @return
	 * 
	 * Accessor method that returns which cue ball is being used by the current player.
	 * 
	 * 
	 */
	public BallType getCueBall()
	{
		return currentCueBall ;
	}
	
	/**
	 * @return
	 * 
	 * Accessor method that returns the current inning that the game is in.
	 * 
	 */
	public int getInning()
	{
		return inning ;
	}
	
	/**
	 * @return
	 * Accessor method that returns the current player of the inning who is taking shots.
	 * 
	 */
	public PlayerPosition getInningPlayer()
	{
		return currentPlayer ;
	}
	
	/**
	 * @return
	 * 
	 * Accessor method that returns the current score of Player A.
	 * 
	 */
	public int getPlayerAScore()
	{
		return playerAScore ;
	}
	
	/**
	 * @return
	 * Accessor method that returns the current score of Player B.
	 * 
	 */
	public int getPlayerBScore()
	{
		return playerBScore ;
	}
	
	/**
	 * @return
	 * Accessor method that returns whether the current shot is a bank shot.
	 * 
	 */
	public boolean isBankShot()
	{
		return bankShot ;
	}
	
	/**
	 * @return
	 * Accessor method that returns whether the current shot is the break shot.
	 * 
	 */
	public boolean isBreakShot()
	{
		return breakShot ;
	}
	
	/**
	 * @return
	 * Accessor method that returns whether the game is over or not.
	 */
	public boolean isGameOver()
	{
		return gameOver ;
	}
	
	/**
	 * @return
	 * Accessor method that returns whether the inning has started or not.
	 */
	public boolean isInningStarted()
	{
		return inningStarted ;
	}
	
	/**
	 * @return
	 * Accessor method that returns whether the shot has started or not.
	 */
	public boolean isShotStarted()
	{
		return shotStarted ;
	}
	

	
	/**
	 * @param selfBreak
	 * @param cueBall
	 * 
	 * Mutator method that simulates the decisions made by lagWinner. 
	 * The lagWinner can choose whether to take the break themselves with selfBreak and what cueball they want with cueBall.
	 * Depending on what the lagWinner chooses, the other player is left with the other cue ball color and whether they break or not.
	 * SGupdate updates to true to signify that the game has started.
	 * 
	 * 
	 */
	public void lagWinnerChooses(boolean selfBreak, BallType cueBall)
	{
		if (SGupdate == false)
		{
			if (selfBreak == true)
			{
				if (lagWinner == PLAYER_A)
				{
					currentPlayer = lagWinner ;
					PAcueBall = cueBall ;
					currentCueBall = cueBall;
					if(PAcueBall == WHITE)
						{
							PBcueBall = YELLOW ;
						}
					else 
						{
							PBcueBall = WHITE ;
						}
				}
				else
				{
					currentPlayer = lagWinner ;
					PBcueBall = cueBall ;
					currentCueBall = cueBall ;
					if(PBcueBall == WHITE)
					{
						PAcueBall = YELLOW ;
					}
					else
					{
						PAcueBall = WHITE ;
					}
				}
			}
			else 
			{
				if(lagWinner == PLAYER_A)
				{
					currentPlayer = PLAYER_B ;
					PAcueBall = cueBall ;
					if(PAcueBall == WHITE)
					{
						PBcueBall = YELLOW ;
						currentCueBall = PBcueBall ;
						
					}
					else
					{
						PBcueBall = WHITE ;
						currentCueBall = PBcueBall ;
					}
				}
				else
				{
					PBcueBall = cueBall ;
					currentPlayer = PLAYER_A ;
					if(PBcueBall == WHITE)
					{
						PAcueBall = YELLOW ;
						currentCueBall = PAcueBall ;
					}
					else
					{
						PBcueBall = WHITE ;
						currentCueBall = PAcueBall ;
					}
				}
			}
		}
		SGupdate = true ;
	}
	/**
	 * Returns a one-line string representation of the current game state. The
	 * format is:
	 * <p>
	 * <tt>Player A*: X Player B: Y, Inning: Z</tt>
	 * <p>
	 * The asterisks next to the player's name indicates which player is at the
	 * table this inning. The number after the player's name is their score. Z is
	 * the inning number. Other messages will appear at the end of the string.
	 * 
	 * @return one-line string representation of the game state
	 */
	public String toString() {
		String fmt = "Player A%s: %d, Player B%s: %d, Inning: %d %s%s";
		String playerATurn = "";
		String playerBTurn = "";
		String inningStatus = "";
		String gameStatus = "";
		if (getInningPlayer() == PLAYER_A) {
			playerATurn = "*";
		} else if (getInningPlayer() == PLAYER_B) {
			playerBTurn = "*";
		}
		if (isInningStarted()) {
			inningStatus = "started";
		} else {
			inningStatus = "not started";
		}
		if (isGameOver()) {
			gameStatus = ", game result final";
		}
		return String.format(fmt, playerATurn, getPlayerAScore(), playerBTurn, getPlayerBScore(), getInning(),
				inningStatus, gameStatus);
	}
}
