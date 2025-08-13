SET GLOBAL local_infile = 1;

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\students.csv'
INTO TABLE students
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(sid, ssn, name, gender, dob, c_addr, c_phone, p_addr, p_phone);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\departments.csv'
INTO TABLE departments
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(dcode, dname, phone, college);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\degrees.csv'
INTO TABLE degrees
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(dgname, level, department_code);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\courses.csv'
INTO TABLE courses
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
(cnumber, cname, description, credithours, level, department_code);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\register.csv'
INTO TABLE register
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
(sid, course_number, regtime, grade);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\major.csv'
INTO TABLE major
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(sid,name,level);

LOAD DATA LOCAL INFILE 'C:\\Users\\evan\\OneDrive\\CODE\\CS363\\data\\project1\\minor.csv'
INTO TABLE minor
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(sid,name,level);