package lab8;

public class IntListTest {

	public static void main(String args[])
	{
		IntListSorted b = new IntListSorted() ;
		b.add(4) ;
		b.add(9);
		b.add(3);
		b.add(5);
		System.out.println(b.getMedian()) ;
	}
}
