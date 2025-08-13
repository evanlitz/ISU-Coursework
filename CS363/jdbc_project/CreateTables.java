package coms363;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

public class CreateTables {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement()) {

             String[] sqlStatements = {
            				    "CREATE TABLE students (" +
            				    "ssn INTEGER PRIMARY KEY," +
            				    "sid INTEGER UNIQUE," +
            				    "name VARCHAR(20)," +
            				    "gender VARCHAR(1)," +
            				    "dob VARCHAR(10)," +
            				    "c_addr VARCHAR(20)," +
            				    "c_phone VARCHAR(20)," +
            				    "p_addr VARCHAR(20)," +
            				    "p_phone VARCHAR(20)" +
            				    ")",

            				    "CREATE TABLE departments (" +
            				    "dcode INTEGER PRIMARY KEY," +
            				    "dname VARCHAR(50) UNIQUE," +
            				    "phone VARCHAR(15)," +
            				    "college VARCHAR(20)" +
            				    ")",

            				    "CREATE TABLE degrees (" +
            				    "dgname VARCHAR(50)," +
            				    "level VARCHAR(20)," +
            				    "department_code INTEGER," +
            				    "PRIMARY KEY (dgname, level)," +
            				    "FOREIGN KEY (department_code) REFERENCES departments(dcode)" +
            				    ")",

            				    "CREATE TABLE courses (" +
            				    "cnumber INTEGER PRIMARY KEY," +
            				    "cname VARCHAR(50)," +
            				    "description VARCHAR(50)," +
            				    "credithours INTEGER," +
            				    "level VARCHAR(20)," +
            				    "department_code INTEGER," +
            				    "FOREIGN KEY (department_code) REFERENCES departments(dcode)" +
            				    ")",

            				    "CREATE TABLE register (" +
            				    "sid INTEGER," +
            				    "course_number INTEGER," +
            				    "regtime VARCHAR(20)," +
            				    "grade INTEGER," +
            				    "PRIMARY KEY (sid, course_number)," +
            				    "FOREIGN KEY (sid) REFERENCES students(sid)," +
            				    "FOREIGN KEY (course_number) REFERENCES courses(cnumber)" +
            				    ")",

            				    "CREATE TABLE major (" +
            				    "name VARCHAR(50)," +
            				    "level VARCHAR(20)," +
            				    "sid INTEGER," +
            				    "PRIMARY KEY (sid, name, level)," +
            				    "FOREIGN KEY (sid) REFERENCES students(sid)," +
            				    "FOREIGN KEY (name, level) REFERENCES degrees(dgname, level) ON DELETE CASCADE" +
            				    ")",

            				    "CREATE TABLE minor (" +
            				    "name VARCHAR(50)," +
            				    "level VARCHAR(20)," +
            				    "sid INTEGER," +
            				    "PRIMARY KEY (sid, name, level)," +
            				    "FOREIGN KEY (sid) REFERENCES students(sid)," +
            				    "FOREIGN KEY (name, level) REFERENCES degrees(dgname, level) ON DELETE CASCADE" +
            				    ")"
            };

            for (String sql : sqlStatements) {
                stmt.executeUpdate(sql);
                System.out.println("Executed: " + sql.split("\\(")[0].trim());
            }

        } catch (SQLException e) {
            System.out.println("Error executing SQL statement:");
            e.printStackTrace();
        }
    }
}
