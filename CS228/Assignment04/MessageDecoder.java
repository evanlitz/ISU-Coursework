package edu.iastate.cs228.hw4;

import java.util.Scanner;
import java.io.File;
import java.io.FileNotFoundException;
/*
 * MessageDecoder Class.
 * @author Evan Litzer
 * Class that decodes and decrypts a message that is formed from a combination of a binary tree of characters and binary code of 1's and 0's.
 * This information is read in from a user-prompted file and assigned to its class variables. 
 * Firstly, the class builds the tree by using the characters in the first line of the file. 
 * Then using the 1s and 0s, the class is able to decrypt the string by using the numbers to traverse through the preset binary tree of chars.
 * 1s point right, 0s point left as characters are accessed.
 * 
 */
public class MessageDecoder {
	// Represents the index of the characters used to build the tree. Incremented when every character is used once.
	private static int staticCharIdx = 0;
	// Array of characters that are used to build the tree. First line of read in file is assigned to this array.
	private static char[] encodingChars;
	// Encoding scheme that represents binary tree.
	private static String encodingString;
	// The root of the MsgTree representing either the topmost beginning node or the current node a traversal is currently on during recursion.
	private static MsgTree root;
	// Amount of characters in decoded message. Used for stats.
	private static int characters ;
	// Amount of bits in decoded message. Used for stats.
	private static double bits ;
/*
 * MsgTree class.
 * Essential in decoding, as characters are assigned and organized in these binary trees almost as a blueprint in order to decode
 * the string. Binary trees where null nodes represent the inner nodes (or branches) and nodes with characters are the outer nodes (children/leaves).
 *  
 */
	private static class MsgTree {
		// Character that each nodes in the tree possesses if it is a leaf. If not, then assigned to null.
		char payloadChar;
		// Left and right children/branches of a node, traverses further into the tree using the parent node.
		MsgTree left, right;
		// Constructor for an inner node with character assigned to null.
		MsgTree() {
			this(Character.MIN_VALUE);
		}
		// Constructor for an outer node with character assigned to whatever is passed in based on file being read in.
		// Left and right are assigned to null because outer nodes have no children.
		MsgTree(char payloadChar) {
			this.payloadChar = payloadChar;
			left = null;
			right = null;
		}
		// Constructor for building the actual binary tree of characters.
		// Passed in string is assigned to class encodingString and encodingChars array of characters use characters from string.
		// Root is then assigned to and calls buildTree().
		MsgTree(String es) {
			MessageDecoder.encodingString = es;
			MessageDecoder.encodingChars = es.toCharArray();
			MessageDecoder.root = buildTree();
		}
		
	}

/*
 * Constructs the character tree based on a preorder traversal of the characters in MessageDecoder's encodingChars array. 
 */
	private static MsgTree buildTree() {

		// Get the first payloadChar of the payloadChar array
		MsgTree thisMsgTree = new MsgTree();
		char encodeChar = getNextChar();
		if (encodeChar == Character.MIN_VALUE) {
			thisMsgTree.payloadChar = encodeChar;
			return thisMsgTree;
		}

		if (encodeChar == '^') {
			// This is a node that must have 2 children
			thisMsgTree.left = buildTree();
			thisMsgTree.right = buildTree();
		} else {
			thisMsgTree.payloadChar = encodeChar;
			return thisMsgTree;
		}
		return thisMsgTree;
	}

	private static char getNextChar() {
		if (MessageDecoder.encodingChars.length > MessageDecoder.staticCharIdx) {
			return MessageDecoder.encodingChars[MessageDecoder.staticCharIdx++];
		} else
			return Character.MIN_VALUE;
	}
/*
 * Prints the binary codes compared to each character that it represents. 
 * Does this by traversing through the tree and outputting 1s and 0s based on if the node has a valid character or not.
 * Recursively occurs as the left and right trees of a node are checked and traversed through.
 */
	private static void printCodes(MsgTree node, String code) {
		if (code == "") {
			System.out.println("Character   code");
			System.out.println("---------------------");
		}
		if (node.payloadChar != Character.MIN_VALUE) {
			System.out.println("   " + node.payloadChar + "        " + code);
		} else {
			printCodes(node.left, code + "0");
			printCodes(node.right, code + "1");
		}
	}
/*
 * Responsible for the actual output and decoding of the message. 
 * For loop makes sure that every character in the encodedMessage is accessed, and determines accordingly where the current MsgTree should be assigned based on if 
 * the bit is a 0 (left) or a 1 (right). If there are no right or lefts to access in a node, then the character of the leaf node is added to the string and 
 * MsgTree is reassigned to the root until there are no more characters left to traverse through.
 */
	private static String decodeMessage(String encodedMessage, MsgTree root) {
		StringBuilder decoded = new StringBuilder();
		MsgTree current = root;

		for (char bit : encodedMessage.toCharArray()) {
			if (bit == '0') {
				current = current.left;
			} else {
				current = current.right;
			}
			if (current.left == null && current.right == null) {
				decoded.append(current.payloadChar);
				MessageDecoder.characters ++ ;
				current = root;
			}
		}
		return decoded.toString();
	}
	/*
	 * Prints out the statistics of decoding the message.
	 */
	private static void printStatistics()
	{
		System.out.println("STATISTICS:");
		System.out.println("Average bits/char: " + MessageDecoder.bits / MessageDecoder.characters) ;
		System.out.println("Total characters: " + MessageDecoder.characters) ;
		System.out.println("Space savings: " + (1 - (MessageDecoder.bits / MessageDecoder.characters)/16) * 100 + "%") ;
		
	}
/*
 * Prints the entire tree and its connections. Used for testing purposes.
 */
	static public void printTree(MsgTree root) {
		System.out.print(traverseTree(root));
	}
/*
 * Prints the characters and the connections of the tree. Used for testing purposes.
 */
	static public String traverseTree(MsgTree root) {

		if (root == null) {
			return "";
		}

		StringBuilder sb = new StringBuilder();
		sb.append(root.payloadChar);

		String pointerRight = "└──";
		String pointerLeft = (root.right != null) ? "├──" : "└──";

		traverseTheNodes(sb, "", pointerLeft, root.left, root.right != null);
		traverseTheNodes(sb, "", pointerRight, root.right, false);

		return sb.toString();
	}
/*
 * Used in printing the tree. Used for testing purposes.
 */
	static public void traverseTheNodes(StringBuilder sb, String padding, String pointer, MsgTree node,
			boolean hasRightSibling) {
		if (node != null) {
			sb.append("\n");
			sb.append(padding);
			sb.append(pointer);
			sb.append(node.payloadChar);

			StringBuilder thePaddingBuilder = new StringBuilder(padding);
			if (hasRightSibling) {
				thePaddingBuilder.append("│  ");
			} else {
				thePaddingBuilder.append("   ");
			}

			String thePaddingForBoth = thePaddingBuilder.toString();
			String pointerRight = "└──";
			String pointerLeft = (node.right != null) ? "├──" : "└──";

			traverseTheNodes(sb, thePaddingForBoth, pointerLeft, node.left, node.right != null);
			traverseTheNodes(sb, thePaddingForBoth, pointerRight, node.right, false);
		}
	}
	/*
	 * Main method that takes in user input for reading in a file and decodes whatever message is encrypted in the files.
	 * Reads in the strings and information from the files and assigns them to MessageDecoder class variables in order to use
	 * messageDecoder methods correctly.
	 * Then decodes the string from the file and outputs the string along with the characters matched with their binary code.
	 */
	public static void main(String[] args) {
		
		Scanner scanner = new Scanner(System.in);
		System.out.print("Please enter filename to decode: ");
		String filename = scanner.nextLine();

		try {
			// Read the file and build the binary tree
			Scanner fileScanner = new Scanner(new File(filename));
			int lineCounter = 0;
			String[] fileLines = new String[3];
			while (fileScanner.hasNext())
				fileLines[lineCounter++] = fileScanner.nextLine();
			String encodingScheme = fileLines[0];
			String encodedMessage = fileLines[lineCounter - 1];
			bits = encodedMessage.length() ;
			if (lineCounter == 3)
				encodingScheme = fileLines[0] + "\n" + fileLines[1];
			fileScanner.close();

			// Build the decoder Tree
			MessageDecoder.MsgTree theTree = new MessageDecoder.MsgTree(encodingScheme);

			//Print out the codes for each character
			printCodes(MessageDecoder.root, "");

			// Decode the message
			System.out.println("MESSAGE:");
			System.out.println(decodeMessage(encodedMessage, MessageDecoder.root));

			// Statistics.
			printStatistics() ;

//			// Print out the deocder tree in a graphical way for debugging purposes.    
//			System.out.println(" \n\nGraphical representation of the tree");
//			printTree(MessageDecoder.root);

		} catch (FileNotFoundException e) {
			System.err.println("File not found: " + e.getMessage());
		}
		scanner.close();

	}
	
	
}