package coms363;

import java.sql.*;

public class Query {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        try (Connection queryConnection = DriverManager.getConnection(url, user, password);
             Statement queryStatement = queryConnection.createStatement()) {

        	String query1SQL = "SELECT c.cnumber, c.cname, AVG(r.grade) AS avg_grade " +
                    "FROM courses c " +
                    "JOIN register r ON c.cnumber = r.course_number " +
                    "GROUP BY c.cnumber, c.cname";

            ResultSet query1ResultSet = queryStatement.executeQuery(query1SQL);
            while (query1ResultSet.next()) {
                int courseNum = query1ResultSet.getInt("cnumber");
                String courseName = query1ResultSet.getString("cname");
                double avgGrade = query1ResultSet.getDouble("avg_grade");

                System.out.println("Course #" + courseNum + ": " + courseName + " | Average Grade: " + avgGrade);
            }
            
            System.out.println();
            
            String query2SQL = "SELECT COUNT(DISTINCT s.sid) AS female_count " +
                    "FROM students s " +
                    "JOIN major m ON s.sid = m.sid " +
                    "JOIN degrees d ON m.name = d.dgname AND m.level = d.level " +
                    "JOIN departments dept ON d.department_code = dept.dcode " +
                    "WHERE s.gender = 'F' AND dept.college = 'LAS' " +
                    "UNION " +
                    "SELECT COUNT(DISTINCT s.sid) " +
                    "FROM students s " +
                    "JOIN minor m ON s.sid = m.sid " +
                    "JOIN degrees d ON m.name = d.dgname AND m.level = d.level " +
                    "JOIN departments dept ON d.department_code = dept.dcode " +
                    "WHERE s.gender = 'F' AND dept.college = 'LAS'";

      ResultSet query2ResultSet = queryStatement.executeQuery(query2SQL);
      int totalFemaleCount = 0 ;
      while (query2ResultSet.next()) {
    	    totalFemaleCount += query2ResultSet.getInt(1);
    	}
    	System.out.println("Total female students majoring or minoring in LAS degrees: " + totalFemaleCount + " females.");
      
      System.out.println();
      
      String query3SQL = "SELECT d.dgname, d.level " +
                    "FROM degrees d " +
                    "JOIN major m ON d.dgname = m.name AND d.level = m.level " +
                    "JOIN students s ON m.sid = s.sid " +
                    "GROUP BY d.dgname, d.level " +
                    "HAVING SUM(s.gender = 'M') > SUM(s.gender = 'F') " +
                    "UNION " +
                    "SELECT d.dgname, d.level " +
                    "FROM degrees d " +
                    "JOIN minor m ON d.dgname = m.name AND d.level = m.level " +
                    "JOIN students s ON m.sid = s.sid " +
                    "GROUP BY d.dgname, d.level " +
                    "HAVING SUM(s.gender = 'M') > SUM(s.gender = 'F')";

      ResultSet query3ResultSet = queryStatement.executeQuery(query3SQL);
      while (query3ResultSet.next()) {
          String name = query3ResultSet.getString("dgname");
          String level = query3ResultSet.getString("level");
          System.out.println("Degree: " + name + " (" + level + ")");
      }


        } catch (SQLException e) {
            System.out.println("Query execution failed:");
            e.printStackTrace();
        }
    }
}
