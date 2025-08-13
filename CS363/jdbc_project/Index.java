package coms363;

import java.sql.*;

public class Index {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        String querySQL = 
            "SELECT d.dgname, d.level " +
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

        try (Connection indexConnection = DriverManager.getConnection(url, user, password);
             Statement indexStatement = indexConnection.createStatement()) {

            long start = System.currentTimeMillis();
            ResultSet noIndexRS = indexStatement.executeQuery(querySQL);
            System.out.println("Degrees with more male students than female:");
            while (noIndexRS.next()) {
                System.out.println("Degree: " + noIndexRS.getString("dgname") +
                                   " (" + noIndexRS.getString("level") + ")");
            }
            long end = System.currentTimeMillis();
            System.out.println("Execution Time with No Index: " + (end - start) + " ms");

            try {
            	indexStatement.executeUpdate("CREATE INDEX idx_gender ON students(gender)");
            } catch (SQLException e) {
                System.out.println("Index already exists");
            }

            long indexStart = System.currentTimeMillis();
            ResultSet indexRS = indexStatement.executeQuery(querySQL);
            System.out.println("\nDegrees with more male students than female with indexing:");
            while (indexRS.next()) {
                System.out.println("Degree: " + indexRS.getString("dgname") +
                                   " (" + indexRS.getString("level") + ")");
            }
            long indexEnd = System.currentTimeMillis();
            System.out.println("Execution Time with Index: " + (indexEnd - indexStart) + " ms");

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
