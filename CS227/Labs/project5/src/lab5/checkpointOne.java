package lab5;

public class checkpointOne {

	public static void main(String[] args) {
		
		System.out.println(initial("Evan Smith jones Jackson Von Ludwig")) ;
		System.out.println(vowelIndex("bbbbbbb")) ;


	}

	public static String initial(String name)
	{
		String j = "" ;
		for(int x = 0 ; x < name.length(); x++)
		{
			if(x == 0)
			{
				j += name.charAt(x) ;
			}
			if(name.charAt(x) == ' ' && x != name.length() - 1)
			{
				j+= name.charAt(x+1) ;
			}
		}
		
		
		return j ;
	}
	
	
	
	public static int vowelIndex(String word)
	{
		int index = -1 ;
		String vowels = "aeiouAEIOU" ;
		for(int x = 0 ; x < word.length(); x++)
		{
			if(vowels.indexOf(word.charAt(x)) >= 0)
			{
				return x ;
			}
		}
		return index ;
		
	}

	
	
}
