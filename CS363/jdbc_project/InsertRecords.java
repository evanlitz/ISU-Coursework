package coms363;
import java.io.*;
import java.sql.*;

public class InsertRecords {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        String line;
        Connection insertRecordsConnection = null;

        try {
            insertRecordsConnection = DriverManager.getConnection(url, user, password);
            String studentFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\students.csv"; 
            String insertStudentsSQL = "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
            try (PreparedStatement studentPS = insertRecordsConnection.prepareStatement(insertStudentsSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(studentFilePath))) {
                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    studentPS.setInt(1, Integer.parseInt(data[1].trim())); 
                    studentPS.setInt(2, Integer.parseInt(data[0].trim())); 
                    studentPS.setString(3, data[2].trim());                
                    studentPS.setString(4, data[3].trim());                
                    studentPS.setString(5, data[4].trim());                
                    studentPS.setString(6, data[5].trim());               
                    studentPS.setString(7, data[6].trim());                
                    studentPS.setString(8, data[7].trim());                
                    studentPS.setString(9, data[8].trim());                
                    studentPS.executeUpdate();
                }
            }

            String deptFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\departments.csv";
            String deptInsertSQL = "INSERT INTO departments VALUES (?, ?, ?, ?)";
            try (PreparedStatement deptPS = insertRecordsConnection.prepareStatement(deptInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(deptFilePath))) {
                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    deptPS.setInt(1, Integer.parseInt(data[0].trim()));
                    deptPS.setString(2, data[1].trim());
                    deptPS.setString(3, data[2].trim());
                    deptPS.setString(4, data[3].trim());
                    deptPS.executeUpdate();
                }
            }
            
            String degreesFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\degrees.csv";
            String degreesInsertSQL = "INSERT INTO degrees VALUES (?, ?, ?)";

            try (PreparedStatement degreePS = insertRecordsConnection.prepareStatement(degreesInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(degreesFilePath))) {

                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    degreePS.setString(1, data[0].trim());                 
                    degreePS.setString(2, data[1].trim());                 
                    degreePS.setInt(3, Integer.parseInt(data[2].trim()));  
                    degreePS.executeUpdate();
                }
            }
            
            String coursesFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\courses.csv";
            String coursesInsertSQL = "INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)";

            try (PreparedStatement coursePS = insertRecordsConnection.prepareStatement(coursesInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(coursesFilePath))) {

                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    coursePS.setInt(1, Integer.parseInt(data[0].trim()));     
                    coursePS.setString(2, data[1].trim());                    
                    coursePS.setString(3, data[2].trim());                    
                    coursePS.setInt(4, Integer.parseInt(data[3].trim()));     
                    coursePS.setString(5, data[4].trim());                    
                    coursePS.setInt(6, Integer.parseInt(data[5].trim()));     
                    coursePS.executeUpdate();
                }
            }
            
            
            String majorFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\major.csv";
            String majorInsertSQL = "INSERT INTO major (sid, name, level) VALUES (?, ?, ?)";

            try (PreparedStatement majorPS = insertRecordsConnection.prepareStatement(majorInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(majorFilePath))) {

                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    majorPS.setInt(1, Integer.parseInt(data[0].trim()));  
                    majorPS.setString(2, data[1].trim());                 
                    majorPS.setString(3, data[2].trim());                 
                    majorPS.executeUpdate();
                }
            }
            
            String minorFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\minor.csv";
            String minorInsertSQL = "INSERT INTO minor (sid, name, level) VALUES (?, ?, ?)";

            try (PreparedStatement minorPS = insertRecordsConnection.prepareStatement(minorInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(minorFilePath))) {

                reader.readLine(); // Skip header
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    minorPS.setInt(1, Integer.parseInt(data[0].trim()));  
                    minorPS.setString(2, data[1].trim());                 
                    minorPS.setString(3, data[2].trim());                 
                    minorPS.executeUpdate();
                }
            }
            
            String registerFilePath = "C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\register.csv";
            String registerInsertSQL = "INSERT INTO register VALUES (?, ?, ?, ?)";

            try (PreparedStatement registerPS = insertRecordsConnection.prepareStatement(registerInsertSQL);
                 BufferedReader reader = new BufferedReader(new FileReader(registerFilePath))) {

                reader.readLine(); 
                while ((line = reader.readLine()) != null) {
                    String[] data = line.split(",", -1);
                    registerPS.setInt(1, Integer.parseInt(data[0].trim()));  
                    registerPS.setInt(2, Integer.parseInt(data[1].trim()));  
                    registerPS.setString(3, data[2].trim());                
                    registerPS.setInt(4, Integer.parseInt(data[3].trim()));  
                    registerPS.executeUpdate();
                }
            }
            
            System.out.println("Inserted all records!");

        } catch (Exception e) {
            System.out.println("Error inserting records:");
            e.printStackTrace();
        }
    }
}
