package library;

import java.util.Date;

public abstract class LibraryItem implements Item {
	protected String title ;
	protected Date dueDate ;
	protected Patron person ;
	
	protected LibraryItem()
	{
		super() ;
	}
	
	  public abstract void checkOut(Patron person, Date dueDate) ;

	  public abstract void checkIn() ;
	  
	  public abstract void renew(Date dat) ;
	  
	  public abstract double getFine(Date dat) ;
	  
	  public abstract boolean isOverdue(Date now) ;
	  
	  public abstract int compareTo(Item other) ;
	  
	  public abstract boolean isCheckedOut() ;
	  
	  public abstract Date getDueDate() ;
	  
	  public abstract String getTitle() ;
	  
	  public abstract Patron getPatron() ;
	  
	  

}
