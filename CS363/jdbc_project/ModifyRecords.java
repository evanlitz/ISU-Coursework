package coms363;

import java.sql.*;

public class ModifyRecords {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        try (Connection MRconnection = DriverManager.getConnection(url, user, password)) {
            String updateNameStatement = "UPDATE students SET name = ? WHERE ssn = ?";
            try (PreparedStatement nameUpdate = MRconnection.prepareStatement(updateNameStatement)) {
                nameUpdate.setString(1, "Scott");
                nameUpdate.setInt(2, 144673371);
                int nameRowsChanged = nameUpdate.executeUpdate();  
                System.out.println("Updated the name to Scott for SSN 144673371." + nameRowsChanged + " rows changed.");
                System.out.println();
                
                ResultSet printChangedName = MRconnection.createStatement().executeQuery("SELECT * FROM students");
                while (printChangedName.next()) {
                    System.out.println("Student: SSN=" + printChangedName.getInt("ssn") +
                                       ", SID=" + printChangedName.getInt("sid") +
                                       ", Name=" + printChangedName.getString("name"));
                }
                System.out.println();
            }
            
            try (Statement majorStatement = MRconnection.createStatement()) {
                majorStatement.executeUpdate("INSERT IGNORE INTO degrees VALUES ('Computer Science', 'MS', 1)");
                majorStatement.executeUpdate("DELETE FROM major WHERE sid = 1001");
                majorStatement.executeUpdate("INSERT INTO major (name, level, sid) VALUES ('Computer Science', 'MS', 1001)");
                System.out.println("Major has been updated.");
                System.out.println();
                ResultSet majorResultSet = majorStatement.executeQuery("SELECT * FROM major");
                while (majorResultSet.next()) {
                    System.out.println("Major: SID=" + majorResultSet.getInt("sid") +
                                       ", Name=" + majorResultSet.getString("name") +
                                       ", Level=" + majorResultSet.getString("level"));
                }
                System.out.println();
                
                ResultSet registerResultSet = majorStatement.executeQuery("SELECT * FROM register");
                System.out.println("Register table after deletions:");
                System.out.println();
                while (registerResultSet.next()) {
                    System.out.println("Register: SID=" + registerResultSet.getInt("sid") +
                                       ", Course=" + registerResultSet.getInt("course_number") +
                                       ", Time=" + registerResultSet.getString("regtime") +
                                       ", Grade=" + registerResultSet.getInt("grade"));
                }
                System.out.println();
            }
            
            try (Statement summer2024DeleteStatement = MRconnection.createStatement()) {
                String deleteSummer2024SQL = "DELETE FROM register WHERE regtime = 'Summer2024'";
                int deletedRows = summer2024DeleteStatement.executeUpdate(deleteSummer2024SQL);
                System.out.println("Deleted " + deletedRows + " registration records from Summer2024");
                System.out.println();
                ResultSet summer2024DeletionResultSet = summer2024DeleteStatement.executeQuery("SELECT * FROM register");
                System.out.println("Register table after deleting Summer2024 Records:");
                System.out.println();
                while (summer2024DeletionResultSet.next()) {
                    System.out.println("Register: SID=" + summer2024DeletionResultSet.getInt("sid") +
                                       ", Course=" + summer2024DeletionResultSet.getInt("course_number") +
                                       ", Time=" + summer2024DeletionResultSet.getString("regtime") +
                                       ", Grade=" + summer2024DeletionResultSet.getInt("grade"));
                }
                System.out.println();
            }
            
            try (Statement minCourseNumberStatement = MRconnection.createStatement()) {
                String deleteFromRegisterTable =
                    "DELETE FROM register " +
                    "WHERE course_number NOT IN ( " +
                    "    SELECT * FROM ( " +
                    "        SELECT MIN(cnumber) " +
                    "        FROM courses " +
                    "        GROUP BY level, department_code " +
                    "    ) AS temp " +
                    ")";

                int numDeletedRegisters = minCourseNumberStatement.executeUpdate(deleteFromRegisterTable);
                System.out.println();
                System.out.println("Deleted " + numDeletedRegisters + " rows from the register table.");
                System.out.println();
                String deleteFromCoursesSQL =
                    "DELETE FROM courses " +
                    "WHERE (level, department_code, cnumber) NOT IN ( " +
                    "    SELECT * FROM ( " +
                    "        SELECT level, department_code, MIN(cnumber) " +
                    "        FROM courses " +
                    "        GROUP BY level, department_code " +
                    "    ) AS temp " +
                    ")";

                int numDeletedCourses = minCourseNumberStatement.executeUpdate(deleteFromCoursesSQL);
                System.out.println("Deleted " + numDeletedCourses + " duplicate courses");
                System.out.println();
                ResultSet coursesResultSet = minCourseNumberStatement.executeQuery("SELECT * FROM courses");
                System.out.println("Courses table after deletions:");
                System.out.println();
                while (coursesResultSet.next()) {
                    System.out.println("Course: CourseNumber=" + coursesResultSet.getInt("cnumber") +
                                       ", Name=" + coursesResultSet.getString("cname") +
                                       ", Department=" + coursesResultSet.getInt("department_code") +
                                       ", Level=" + coursesResultSet.getString("level"));
                }
            }   
        
        } catch (SQLException e) {
            System.out.println("Error modifying records:");
            e.printStackTrace();
        }
    }
}
