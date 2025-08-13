package coms363;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

public class DropTables {

    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/collegedb";
        String user = "coms363";
        String password = "password";

        String[] dropSQL = {
            "DROP TABLE IF EXISTS minor",
            "DROP TABLE IF EXISTS major",
            "DROP TABLE IF EXISTS register",
            "DROP TABLE IF EXISTS courses",
            "DROP TABLE IF EXISTS degrees",
            "DROP TABLE IF EXISTS departments",
            "DROP TABLE IF EXISTS students"
        };

        try (Connection connect = DriverManager.getConnection(url, user, password);
             Statement stmt = connect.createStatement()) {

            for (String sql : dropSQL) {
                stmt.executeUpdate(sql);
                System.out.println("Dropped Table: " + sql);
            }

        } catch (SQLException e) {
            System.out.println("Error dropping tables:");
            e.printStackTrace();
        }
    }
}
