package edu.iastate.cs228.hw3;

import java.util.AbstractSequentialList;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Iterator;
import java.util.ListIterator;
import java.util.NoSuchElementException;

/**
 * Implementation of the list interface based on linked nodes
 * that store multiple items per node.  Rules for adding and removing
 * elements ensure that each node (except possibly the last one)
 * is at least half full.
 * 
 * @author Evan Litzer
 * 
 * Represents a stoutlist object that contains connected nodes with node-individual lists of E elements stored in a data array. Also contains other classes,
 * including the node and nodeinfo classes representing the nodes and their information, the comparator class which compares different E elements in the 
 * nodes for sorting, and the listIterator class which iterates through the list. 
 * 
 * StoutList is a list of linked nodes with elements inside the nodes. 
 * 
 */
public class StoutList<E extends Comparable<? super E>> extends AbstractSequentialList<E>
{
	/**
	 * Default number of elements that may be stored in each node.
	 */
	private static final int DEFAULT_NODESIZE = 4;

	/**
	 * Number of elements that can be stored in each node.
	 */
	private final int nodeSize;

	/**
	 * Dummy node for head. I set it back to private! 
	 */
	private Node head;

	/**
	 * Dummy node for tail.
	 */
	private Node tail;

	/**
	 * Number of elements in the list.
	 */
	private int size;

	/**
	 * Constructs an empty list with the default node size.
	 */
	public StoutList()
	{
		this(DEFAULT_NODESIZE);
	}

	/**
	 * Constructs an empty list with the given node size. Only has dummy nodes that are connected.
	 * @param nodeSize number of elements that may be stored in each node, must be 
	 *   an even number
	 */
	public StoutList(int nodeSize)
	{
		// Check to see if nodeSize is even and positive.
		if (nodeSize <= 0 || nodeSize % 2 != 0) 
		{
			// Switched for testing.
			throw new IllegalArgumentException("nodeSize must be even and positive.");
		}

		// Setting up the dummy nodes and their links.
		head = new Node();
		tail = new Node();
		head.next = tail;
		tail.previous = head;
		this.nodeSize = nodeSize;
	}

	/**
	 * Constructor for grading only.  Fully implemented. 
	 * @param head
	 * @param tail
	 * @param nodeSize
	 * @param size
	 */
	public StoutList(Node head, Node tail, int nodeSize, int size)
	{
		// Set head, tail, nodeSize, and size to the preferred parameters in the constructor.
		this.head = head; 
		this.tail = tail; 
		this.nodeSize = nodeSize; 
		this.size = size; 
	}
	/*
	 * Returns the size of the list, or total number of elements in all the nodes.
	 */
	@Override
	public int size()
	{
		return size ;
	}

	/*
	 * Adds an item to the end of the list and after the last element. Cannot be added to tail obviously. Takes in item to add.
	 * Returns boolean true.
	 * @param item
	 */
	@Override
	public boolean add(E item)
	{
		NodeInfo NI = new NodeInfo();
		NI.add(item);
		return true;
	}



	/*
	 * Finds and returns the node based on the passed in position. Calls find(pos).
	 */
	public Node getNode(int pos)
	{
		NodeInfo NI = new NodeInfo();
		NI.find(pos);
		return NI.node;
	}
	/*
	 * Finds and returns the offset based on the passed in position. Calls find(pos) after creating a NodeInfo object.
	 */
	public int getOffset(int pos)
	{
		NodeInfo NI = new NodeInfo();
		NI.find(pos);
		return NI.offset;
	}
	/*
	 * Adds an item to the list based on passed in position and item. Creates new NodeInfo object to find correct node, then adds the item
	 * to the said node in the node add method.
	 */
	@Override
	public void add(int pos, E item)
	{
		NodeInfo NI = new NodeInfo();
		NI.add(pos,item);
	}

	/*
	 * Removes an item from a list based on the passed in postition. Creates new NodeInfo object and calls nodeinfo remove method with position
	 * Returns the removed item.
	 */
	@Override
	public E remove(int pos)
	{

		NodeInfo NI = new NodeInfo();
		NI.remove( pos);
		E x = head.next.data[0];
		return x;


	}

	/**
	 * 
	 * 
	 * Sorts all elements in stout list in a non-decreasing order using insertionSort(). First creates an array of comparables with list size casted as an array of
	 * generics before traversing through the list and all the nodes and adding the elements to the array. Head and tail are connected back to eachother before
	 * insertion sort is called with the array and the created comparator. After size is downgraded back to 0, traverses through array and adds back all the values
	 * to the nodes in the sorted order.
	 * 
	 */
	public void sort()
	{
		E[] arr = (E[]) new Comparable[size] ;

		int j = 0 ;
		Node node = head ;
		while(node.next != tail)
		{
			node = node.next ;
			for(int x = 0 ; x < node.count ; x++)
			{
				arr[j] = node.data[x] ;
				j++ ;
			}
		}
		head.next = tail ;
		tail.previous = head ;

		insertionSort(arr, new MyComparator()) ;
		size = 0 ;
		for(int x = 0 ; x < arr.length ; x++)
		{
			add(arr[x]) ;
		}

	}

	/**
	 * 
	 * Sorts all elements in the list in a non-increasing order using bubbleSort. First creates an array of comparables with list size casted as an array of
	 * generics before traversing through the list and all the nodes and adding the elements to the array. Then, head and tail are reconnected and size is downgraded
	 * back to 0. BubbleSort is performed on the array, before the elements are added back to the list in an opposite fashion as to what they were sorted to,
	 * 
	 * 
	 * 
	 */
	public void sortReverse() 
	{
		E[] arr = (E[]) new Comparable[size] ;
		Node node = head ;
		int j = 0 ;
		while(node.next != tail)
		{
			node = node.next ;
			for(int x = 0 ; x < node.count ; x++)
			{
				arr[j] = node.data[x] ;
				j++ ;
			}
		}
		head.next = tail ;
		tail.previous = head ;
		bubbleSort(arr) ;
		size = 0 ;
		for(int y = arr.length - 1 ; y >= 0 ; y--)
		{
			add(arr[y]) ;
		}

	}
	/*
	 * Returns a stoutListIterator object.
	 */
	@Override
	public Iterator<E> iterator()
	{
		return new StoutListIterator() ;
	}
	/*
	 * Returns a StoutListIterator object.
	 */
	@Override
	public ListIterator<E> listIterator()
	{
		return new StoutListIterator() ;
	}
	/*
	 * Returns a new stoutlistiterator object that takes in index value.
	 * @param index
	 */
	@Override
	public ListIterator<E> listIterator(int index)
	{
		return new StoutListIterator(index) ;
	}

	/**
	 * Returns a string representation of this list showing
	 * the internal structure of the nodes.
	 */
	public String toStringInternal()
	{
		return toStringInternal(null);
	}

	/**
	 * Returns a string representation of this list showing the internal
	 * structure of the nodes and the position of the iterator.
	 *
	 * @param iter
	 *            an iterator for this list
	 */
	public String toStringInternal(ListIterator<E> iter) 
	{
		
		int count = 0;
		int position = -1;
		if (iter != null) {
			position = iter.nextIndex();
		}

		StringBuilder sb = new StringBuilder();
		sb.append('[');
		Node current = head.next;
		while (current != tail) {
			sb.append('(');
			E data = current.data[0];
			if (data == null) {
				sb.append("-");
			} else {
				if (position == count) {
					sb.append("| ");
					position = -1;
				} 


				sb.append(data.toString());
				++count;
			}

			for (int i = 1; i < nodeSize; ++i) {
				sb.append(", ");
				data = current.data[i];
				if (data == null) {
					sb.append("-");
				} else {
					if (position == count) {
						sb.append("| ");
						position = -1;
					}
					sb.append(data.toString());
					++count;

					// iterator at end
					if (position == size && count == size) {
						sb.append(" |");
						position = -1;
					}
				}
			}
			sb.append(')');
			current = current.next;
			if (current != tail)
				sb.append(", ");
		}
		sb.append("]");
		return sb.toString();
	}

	/**
	 * NodeInfo helper class, giving extended access to node information.
	 * @author Evan Litzer
	 */
	private class NodeInfo
	{
		// Initializes node and offset values.
		public Node node;
		public int offset;
		// Empty constructor for nodeInfo.
		public NodeInfo()
		{
			this.node = null;
			this.offset = 0;
		}
		// Creates nodeInfo object with passed in node and offset parameters.
		public NodeInfo(Node node, int offset)
		{
			this.node = node;
			this.offset = offset;
		}
		/*
		 * Finds the node that contains the passed in position parameter value.
		 * 
		 */
		public void find(int pos)
		{
			Node current = head.next ;

			int sum = 0;

			int nextOffset = pos;
			// Finds the correct node by traversing through ones that don't contain the position.
			while(current != tail && sum + current.count <= pos) {

				sum += current.count;

				nextOffset -= current.count;

				current = current.next;

			}
			this.node = current;
			this.offset = nextOffset;
		}
		/*
		 * Removes an element from a node based on the passed in postion value.
		 * 
		 * Adheres to all of the rules laid out in the instructions.
		 */
		public void remove(int pos)
		{
			E deleted = null ;
			int offset = getOffset( pos) ;
			Node current = getNode(pos);

			// If on the last node
			if(current.next == tail)
			{
				
				if(current.count <= 1)
				{
					deleted = current.data[offset] ;
					current.removeItem(offset);
					current.previous.next = tail ;
					tail.previous = current.previous ;
				}
				else
				{
					deleted = current.data[offset] ;
					current.removeItem(offset) ;
				}
			}
			// If the current
			else if(current.count > nodeSize / 2)
			{
				deleted = current.data[offset - 1] ;
				current.removeItem(offset - 1) ;
			}
			else
			{
				if(current.next.count > nodeSize / 2)
				{
					deleted = current.data[offset] ;
					current.removeItem(offset) ;
					current.addItem(current.next.data[0]) ;
					current.next.removeItem(0) ;
				}
				else if(current.next.count <= nodeSize / 2)
				{
					deleted = current.data[offset] ;
					current.removeItem(offset) ;
					for(int i = 0; i < current.next.count ; i++) 
					{
						current.addItem(current.next.data[i]);
						current.next.removeItem(i);
					}
					current.next.previous = current ;
					current.next = current.next.next ;
				}
			}
		}


		/*
		 * Adds an item to a node. Since there is no index parameter, checks for an open node and adds it to the end of it.
		 * If there is no empty node, creates a new one.
		 */
		public boolean add(E item) {
			Node current = head ;
			// Check if item is null.
			if(item == null)
			{
				throw new NullPointerException("Item that you are trying to add is null.") ;
			}
			// Check if it is an empty list. If it is, then creates a new node.
			else if(head.next == tail)
			{
				Node newNode = new Node() ;
				newNode.addItem(0, item) ;
				newNode.previous = current ;
				newNode.next = tail ;
				tail.previous = newNode ;
				current.next = newNode ;
				size++ ;
				return true ;
			}
			else
			{
				while(current.next != tail)
				{
					current = current.next ;
				}
				if(current.count < nodeSize)
				{
					current.addItem(item); 
				}
				else 
				{
					Node newNode = new Node() ;
					newNode.addItem(item) ;
					newNode.previous = current ;
					newNode.next = tail ;
					tail.previous = newNode ;
					current.next = newNode ;
				}
				size++ ;
				return true ;
			}
		}
		
		/*
		 * Adds an item to a node based on the postion passed in. Adheres to specfic rules laid out 
		 * in the instructions.
		 */
		public void add(int pos, E item) {

			int offset ;
			// If empty, call add(item).
			if(head == tail)
			{
				add(item) ;
			}
			// Check if postion is valid.
			else 
			{
				if (pos < 0 || pos > size) {
					throw new IndexOutOfBoundsException();
				}
			// If the postion is equal to 0, then it is a special case. All elements are shifted,
			// and item is added to the front of the list. Split must occur if too many elements, if not
			// then it is just added.	
				if (pos == 0 ) {				
					Node current = head.next;
					if(current.count >= nodeSize  ) {
						Node newNode = new Node();

						int itemsToMove = current.count / 2;
						for(int i = 0; i < itemsToMove; i++) {
							newNode.addItem(current.data[current.count - itemsToMove + i]);
							current.removeItem(current.count - itemsToMove + i);

						}
						current.addItem(0, item);

						newNode.next = current.next;
						newNode.previous = current;
						current.next.previous =  newNode;
						current.next = newNode;
					} else {
						head.next.addItem(0,item);
					}
				} else {
					//Find the position pos -1
					Node current ;
					current = getNode(pos-1);
					offset = getOffset(pos-1) + 1;

					//  Add a data element to offset + 1
					//if (offset+1 == nodeSize) {need to add it to the next node}


					// If offset equals 0, then rules of instructions are followed.
					if(offset == 0)
					{
						if(current.previous != head && current.previous != null && current.previous.count < nodeSize)
						{
							current.previous.addItem(item);
						}
						else if(current == tail && current.previous.count == nodeSize)
						{
							add(item);
						}
					}

					Boolean countTest = true;
					if ( current.count < nodeSize) {
						countTest = false;
						current.addItem(offset, item);
					} 


					if(current.count > nodeSize || countTest ) {
						Node newNode = new Node();

						int itemsToMove = current.count / 2;
						for(int i = 0; i < itemsToMove; i++) {
							newNode.addItem(current.data[current.count - itemsToMove + i]);
							current.removeItem(current.count - itemsToMove + i);

						}
						current.addItem(offset, item);

						newNode.next = current.next;
						newNode.previous = current;
						current.next.previous =  newNode;
						current.next = newNode;
					}
				}
				size++;
			}
		}

	}


	/**
	 * Node type for this list.  Each node holds a maximum
	 * of nodeSize elements in an array.  Empty slots
	 * are null.
	 * 
	 * @author Evan Litzer
	 * 
	 * 
	 * Class represents a node contained in a stoutlist. Each node has an array of generic elements
	 * named data. Every node has an offset, a previous/next (besides head/tail), and a count representing
	 * how many elements there are.
	 */
	public class Node
	{
		// Empty node constructor.
		public Node()
		{
			this.next = null ;
			this.previous = null ;
			this.count = 0 ;
		}

		/**
		 * Array of actual data elements.
		 */
		// Unchecked warning unavoidable.
		public E[] data = (E[]) new Comparable[nodeSize];

		/**
		 * Link to next node.
		 */
		public Node next;

		/**
		 * Link to previous node;
		 */
		public Node previous;

		/**
		 * Index of the next available offset in this node, also 
		 * equal to the number of elements in this node.
		 */
		public int count;

		/**
		 * Adds an item to this node at the first available offset.
		 * Precondition: count < nodeSize
		 * @param item element to be added
		 */
		void addItem(E item)
		{
			if (count >= nodeSize)
			{
				return;
			}
			data[count++] = item;
			//useful for debugging
			//      System.out.println("Added " + item.toString() + " at index " + count + " to node "  + Arrays.toString(data));
		}

		/**
		 * Adds an item to this node at the indicated offset, shifting
		 * elements to the right as necessary.
		 * 
		 * Precondition: count < nodeSize
		 * @param offset array index at which to put the new element
		 * @param item element to be added
		 */
		void addItem(int offset, E item)
		{
			if (count >= nodeSize)
			{
				return;
			}
			for (int i = count - 1; i >= offset; --i)
			{
				data[i + 1] = data[i];
			}
			++count;
			data[offset] = item;
			//useful for debugging 
			//      System.out.println("Added " + item.toString() + " at index " + offset + " to node: "  + Arrays.toString(data));
		}

		/**
		 * Deletes an element from this node at the indicated offset, 
		 * shifting elements left as necessary. Adjusts count too.
		 * Precondition: 0 <= offset < count
		 * @param offset
		 */
		void removeItem(int offset)
		{
			E item = data[offset];
			for (int i = offset + 1; i < nodeSize; ++i)
			{
				data[i - 1] = data[i];
			}
			data[count - 1] = null;
			--count;
		}    
	}
	/*
	 * @author Evan Litzer
	 * 
	 * Represents an iterator of the stoutlist, used for iterating through the list in order to access different
	 * nodes and elements of the nodes.
	 */
	private class StoutListIterator implements ListIterator<E>
	{
		// Class values.  

		private Node current ;
		private int index ;
		private int offset ;
		private int lastIndex;

		/**
		 * Default constructor 
		 */
		public StoutListIterator()
		{
			this.offset = 0 ;
			this.index = 0 ;
			this.lastIndex = 0;
			this.current = head ;
		}

		/**
		 * Constructor finds node at a given position.
		 * @param pos = the position of the element/item.
		 */
		public StoutListIterator(int pos)
		{
			current = getNode(pos) ;
			offset = getOffset(pos) ;
		}
		// Returns the next index.
		public int nextIndex() 
		{
			return index;
		}
		// Returns the previous index.
		public int previousIndex()
		{
			return index ; // - 1; 
		}
		// Returns true or false based on if there is a previous node.
		public boolean hasPrevious()
		{
			return (offset > 0 || (current.previous != null && current.previous != head)) ;
		}
		// Returns the previous item based on the index/cursor.
		public E previous()
		{
			if(hasPrevious() == false)
			{
				throw new NoSuchElementException() ;
			}
			// if there is negative offset, change to previous node.
			if(offset <= 0)
			{
				current = current.previous ;
				offset = current.count ;
			}
			offset-- ;
			E item = current.data[offset] ;
			index-- ;
			lastIndex = index;
			return item ;

		}
		// Returns true if there is a node in the next position.
		@Override
		public boolean hasNext()
		{
			return (offset < current.count || (current.next != null && current.next != tail)) ;
		}
		/*
		 * Returns the next item/element in the list/node.
		 */
		@Override
		public E next()
		{
			// If there is no next item, throw exception.
			if(hasNext() == false)
			{
				throw new NoSuchElementException() ;
			}
			// Goes to next node if offset is too big.
			if(offset >= current.count)
			{
				current = current.next ;
				offset = 0 ;
			}
			
			E item = current.data[offset++] ;
			lastIndex = index;
			index++ ;
			return item ;
		}
		/*
		 * Removes an element from the listIterator.
		 */
		@Override
		public void remove()
		{
			Node removal = current ;
			NodeInfo NI = new NodeInfo();
			NI.remove(index);
		}


		/*
		 * Sets a specific item to e.
		 */
		@Override
		public void set(E e) {
//			System.out.println("Index is " + index);
//			System.out.println("Offset is " + offset);
//			System.out.println("lastIndex is " + lastIndex);
			Node toSet = current;
			// If on the first of the entire list
			if(lastIndex == 0) {		
				toSet.data[offset] = e;
			} else {
				if (lastIndex < index) {   // next was last used
					if(offset == 0) {
						toSet = current.previous;
					}
					toSet.data[offset - 1] = e;
				} else {  // previous was last used
					if(offset == nodeSize) {
						toSet = current.next;

					}
				}

			}
		}
		/*
		 * Adds an item to the list based on the index of the cursor.
		 */
		@Override
		public void add(E item) {	
			NodeInfo NI = new NodeInfo();
			NI.add(index,item);
			this.index++ ;
		}
	}


	/**
	 * Sort an array arr[] using the insertion sort algorithm in the NON-DECREASING order. 
	 * Follows the insertion sort algorithm, using the comparator to compare the generic items properly from the array.
	 * @param arr   array storing elements from the list 
	 * @param comp  comparator used in sorting 
	 */
	private void insertionSort(E[] arr, Comparator<? super E> comp)
	{
		for(int x = 1 ; x < arr.length ; x++)
		{
			E cur = arr[x] ;
			int b = x - 1 ;

			while(comp.compare(arr[b], cur) > 0 && b >= 0)
			{
				arr[b + 1] = arr[b] ;
				b -= 1 ;
			}
			arr[b + 1] = cur ;



		}
	}





	/**
	 * Sort arr[] using the bubble sort algorithm in the NON-INCREASING order. 
	 * Follows the bubble sort algorithm in order to sort the items of the array into the non-increasing order.
	 * @param arr  array holding elements from the list
	 */
	private void bubbleSort(E[] arr)
	{
		boolean isDone ;
		for(int x = 0 ; x < arr.length - 1 ; x++)
		{
			isDone = true ;
			for(int y = 0 ; y < arr.length - x - 1 ; y++)
			{
				if(arr[y].compareTo(arr[y + 1]) > 0)
				{
					E temp = arr[y] ;
					arr[y] = arr[y+1] ;
					arr[y+1] = temp ;
					isDone = false ;
				}
			}

			if(isDone == true)
			{
				break ;
			}

		}

	}

	/*
	 * @author Evan Litzer
	 * 
	 * Comparator class used to compare generic items of the list.
	 */
	class MyComparator<E extends Comparable<E>> implements Comparator<E> {
		@Override
		public int compare(E arg0, E arg1) {
			return arg0.compareTo(arg1);
		}
	}

	// Unit tests from here on out!
	
	
	
	
	
//	private void testEverything1( StoutList theList )
//	{
//		System.out.println("Test everything 2");
//
//		theList.add("A") ;
//		theList.add("B") ;
//		theList.add("X") ;
//		theList.add("X") ;
//		theList.add("C") ;
//		theList.add("D") ;
//		theList.add("E") ;
//
//		//remove a couple entries
//		theList.head.next.data[2] = null;
//		theList.head.next.data[3] = null;
//		theList.head.next.count = 2;
//
//		StoutListIterator iter = new StoutListIterator();
//
//		System.out.println("FIRST TIME USING ITERATOR REMOVES");
//		System.out.println("After Add(V) in figure 4");
//		theList.add("V") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(W) in figure 5");
//		theList.add("W") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(2,X) in figure 6");
//		theList.add(2,"X") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.exit(1);
//
//
//		System.out.println("After Add(2,Y) in figure 7");
//		theList.add(2,"Y") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(2,Z) in figure 8");
//		theList.add(2,"Z") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		iter.next();
//		iter.next();iter.next();
//		iter.next();
//		iter.next();
//		iter.next();iter.next();
//		iter.next();
//		iter.next();
//		iter.next();
//		//System.out.println(toStringInternal(iter)) ;
//
//		System.out.println("After Remove(9) in figure 10");
//		//theList.remove(10) ;
//		iter.remove();
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Remove(3) in figure 11") ;
//		theList.remove(3) ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Remove(3) in figure 12") ;
//		theList.remove(3) ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Remove(5) in figure 13") ;
//		theList.remove(5) ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Remove(3) in figure 14") ;
//		theList.remove(3) ;
//		System.out.println(theList.toStringInternal()) ;
//
//
//		System.exit(1);
//
//
//	}
//
//
//
//
//	private void testEverything2( StoutList theList )
//	{
//		System.out.println("\n\n\nTest everything 2");
//
//		// Create a list like in the example
//		theList.add("A") ;
//		theList.add("B") ;
//		theList.add("X") ;
//		theList.add("X") ;
//		theList.add("C") ;
//		theList.add("D") ;
//		theList.add("E") ;
//
//		//remove a couple entries
//		theList.head.next.data[2] = null;
//		theList.head.next.data[3] = null;
//		theList.head.next.count = 2;
//
//		StoutListIterator iter = new StoutListIterator();
//
//		NodeInfo NI = new NodeInfo();
//		//System.out.println("FIND lastIndex is "+ iter.lastIndex +" and value is " + (String)NI.find(iter.lastIndex));
//		System.out.println(toStringInternal(iter)) ;
//
//		Node x;
//		int off;
//		for(int q=0 ; q<=4 ; q++) {
//			x = getNode(q);
//			off = getOffset(q);
//			System.out.println("Position = " +q+ " Node = " + x.data[off] + " " + off);
//		}
//
//
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(V) in figure 4");
//		theList.add("V") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(W) in figure 5");
//		theList.add("W") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(2,X) in figure 6");
//		theList.add(2,"X") ;
//		System.out.println(theList.toStringInternal()) ;
//
//
//		System.out.println("After Add(0,Y) in figure 7");
//		theList.add(0,"Y") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(0,Z) in figure 8");
//		theList.add(0,"Z") ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Add(0,Z) in figure 8");
//		theList.add(4,"O") ;
//		System.out.println(theList.toStringInternal()) ;
//
//
//
//
//		System.out.println("After Remove(9) in figure 10");
//		theList.remove(9) ;
//		System.out.println(theList.toStringInternal()) ;
//
//		System.out.println("After Remove(5) in figure 13") ;
//		theList.remove(5) ;
//		System.out.println(theList.toStringInternal()) ;
//
//
//	}
//
//
//	private void testEverything3( StoutList theList )
//	{
//		System.out.println("Test everything 2");
//
//		//Test Iterater add and remove
//		theList.add("A") ;
//		theList.add("R") ;
//		theList.add("C") ;
//		theList.add("H") ;
//		theList.add("E") ;
//		theList.add("F") ;
//		theList.add("G") ;
//		theList.add("L") ;
//		theList.add("I") ;
//		theList.add("Z") ;
//		theList.add("K") ;
//
//		StoutListIterator iter = new StoutListIterator();
//
//		iter.next();iter.next();
//
//		iter.add((E) "j");
//
//		//		ArrayList<E> arr = new ArrayList<>() ;
//
//		System.out.println(theList.toStringInternal()) ;
//
//		theList.sortReverse() ;
//
//		System.out.println(theList.toStringInternal()) ;
//
//		//System.out.println(toStringInternal(iter)) ;
//	}
//
//
//
//
//	public static void main(String args[]) 
//	{
//		//		StoutList listerine = new StoutList(StoutList.DEFAULT_NODESIZE) ;
//		//		StoutList<String> list = new StoutList<>(4) ;
//		//		list.testEverything1(list);
//
//		StoutList<String> list2 = new StoutList<>(4) ;
//		list2.testEverything2(list2);
//		//		StoutList<String> list3 = new StoutList<>(4) ;
//		//		list.testEverything3(list);
//
//
//	}
}