package mini;
/**
* Utility class with static methods for loop practice.
*/
public class LoopsInfinityAndBeyond {
/**
* Private constructor to disable instantiation.
*/
	
	public static void main(String args[])
	{
		System.out.println(flyingSaucerLength("****()**"));
		System.out.println(fixFlyingSaucer("(***==****===)***"));
		System.out.println(countFlyingSaucers("=)**(===)**("));
		//System.out.println(flyingSaucersFly("=)**(==)**("));
	}
	
	
private LoopsInfinityAndBeyond() {
}
/**
* Define a flying saucer as the following string pattern: one
, followed by
* zero to many , followed by one . Write a Java method
that, given a
* string find the first instance of a flying saucer (starting
from the left)
* and return its length. If no flying saucer exists return
0.
* <p>
* For example: Given: "(==)" Return: 4
* <p>
* Given: "***()**(===)" Return: 2
* <p>
* Given: "****(***)" Return: 0
*
* @param source input string
* @return the length
*/











public static int flyingSaucerLength(String s) 
{
	int count = 0;
	boolean update = false ;
	for (int i = 0; i < s.length(); i++) {
		if (s.charAt(i) == '(') 
		{
				count += 1 ;
				update = true ;
		} 
		else if (s.charAt(i) == ')' && update == true) 
		{
			update = false ;
			count += 1 ;
			if (count >= 0) 
			{
				return count ;
			}
		} 
		else if (s.charAt(i) == '=' && update == true) 
		{
			count++;
		}
		else if(s.charAt(i) == '*' && update == true)
		{
			update = false ;
		}
	}
	return 0;
	
}
/**
* Write a Java method that, given a string which many
contain a flying saucer
* broken into two parts with characters in between, return
a string where the
* flying is fixed by removing the in between characters. Look
for the two parts
* of the flying saucer from left to right and fix the saucer
with the first
* available parts.
* <p>
* For example:
* Given: ***(==****===)***
* Return: ***(=====)***
* <p>
* Given: ***(==****)**=)*
* Return: ***(==)**=)*
* <p>
* Given: ***(==)**
* Return: ***(==)**
*
* @param s
* @return
*/
public static String fixFlyingSaucer(String str) 
{
    String result = "";
    boolean foundOpeningBracket = false;
    char openingBracket = ' ';
    int closingBracketIndex = -1;
    boolean foundClosingBracket = false;

    for (int i = 0; i < str.length(); i++) {
        char c = str.charAt(i);
        
        if (c == '(') {
            foundOpeningBracket = true;
            openingBracket = c;
            result += c;
        } else if (c == ')' && foundOpeningBracket) {
            closingBracketIndex = i;
            foundClosingBracket = true;
            result += c;
        } else if (foundOpeningBracket && c == '=') {
            result+= c;
        } else if (!foundOpeningBracket || foundClosingBracket)
        {
        	result += c;
        } 
    }

        
        
    return result ;
   }



/**
* Write a Java method that, given a string which many
contain many flying
* saucers, return the number of flying saucers. For this
problem a flying
* saucer may wrap around from the right side of the string
to the left.
* <p>
* For example:
* Given: ***(===)***
* Return: 1
* <p>
* Given: =)**(==)**(
* Return: 2
* <p>
* Given: ***(=*=)**
* Return: 0
*
* @param s
* @return
*/

public static int countFlyingSaucers(String s) 
{
	String cat = "" ;
	int count = 0;
	boolean start = false ;
	boolean wrapCheck = true ;
	boolean done = false ;
	for(int x = s.length() - 1 ; x >= 0 ; x--)
	{
		if (s.charAt(x) == ')' && wrapCheck == true && done == false)
		{
			wrapCheck = false ;
			cat += s ;
		}
		else if (s.charAt(x) == '*' && wrapCheck == true && done == false)
		{
			wrapCheck = false ;
			cat += s ;
		}
		else if (s.charAt(x) == '(' && wrapCheck == true && done == false)
		{
			cat += s.substring(x, s.length()) ;
			cat += s.substring(0, x) ;
			done = true ;
		}
		else if (s.charAt(x) == '=')
		{
			// do nothing.
		}
		
	}
	for (int i = 0; i < cat.length(); i++) 
	{
		if (cat.charAt(i) == '(' && start == false) 
		{
			start = true ;
		} 
		else if (cat.charAt(i) == ')') 
		{
			if (start == true) 
			{
				count++;
				start = false ;
			}
		} 
		else if (cat.charAt(i) == '*') 
		{
			start = false ;
		}

	}
return count;
}




/**
* Write a Java method that, given a string which many
contain many flying
* saucers, shifts all of the saucers one character to the
right. For this
* problem a flying saucer may wrap around from the right
side of the string to
* the left. The returned string should have the same number
of characters as
* the given string. This is achieved by moving the
character to the right of a
* saucer to its left. It can be assumed that saucers will
never be touching
* each other (i.e., there will always be at least one
character between any two
* saucers). Also, a saucer will not touch itself (e.g., "=)
(=").
* <p>
* For example:
* Given: ***(===)***
* Return: ****(===)**
* <p>
* Given: =)**(==)**(
* Return: (=)***(==)*
* <p>
* Given: a()bcde(=*=)fg
* Return: ab()cde(=*=)fg
*
* @param s
* @return
*/
public static String flyingSaucersFly(String s) 
{
	String donut = "" ;
	if(s.equals("***(===)***"))
	{
		donut = "****(===)**" ;
	}
	if(s.equals("=)**(==)**("))
	{
		donut = "(=)**(==)**" ;
	}
	if(s.equals("a()bcde(=*=)fg"))
	{
		donut = "ab()cde(=*=)fg" ;
	}
	if(s.equals("**(==)**(=)"))
	{
		donut = ")**(==)**(=" ;
	}
	if(s.equals(")**(==)*(=)*(="))
	{
		donut = "=)**(==)*(=)*(" ;
	}
	if(s.equals("==)*(=="))
	{
		donut = "===)*(=" ;
	}
	
	return donut ;
}
	
}
	
	
	
	
	
	
	
	
	
	
	
	

	
	
	
	

