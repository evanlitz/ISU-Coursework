-- CREATE DATABASE CollegeDB;
-- USE CollegeDB;

CREATE TABLE students (
	ssn INTEGER PRIMARY KEY,
    sid INTEGER UNIQUE,
    name VARCHAR(20),
    gender VARCHAR(1),
    dob VARCHAR(10),
    c_addr VARCHAR(20),
    c_phone VARCHAR(20),
    p_addr VARCHAR(20),
    p_phone VARCHAR(20)
);

CREATE TABLE departments (
	dcode INTEGER PRIMARY KEY,
    dname VARCHAR(50) UNIQUE,
    phone VARCHAR(10),
    college VARCHAR(20)
);    

CREATE TABLE degrees (
	dgname VARCHAR(50),
    level VARCHAR(5),
    department_code INTEGER,
    PRIMARY KEY (dgname, level),
    FOREIGN KEY	(department_code) REFERENCES departments(dcode)
);

CREATE TABLE courses (
	cnumber INTEGER PRIMARY KEY,
    cname VARCHAR(50),
    description VARCHAR(50),
    credithours INTEGER,
    level VARCHAR(20),
    department_code INTEGER,
    FOREIGN KEY (department_code) REFERENCES departments(dcode)
    );
    
CREATE TABLE register (
	sid INTEGER,
	course_number INTEGER,
	regtime VARCHAR(20),
	grade INTEGER,
	PRIMARY KEY (sid, course_number),
	FOREIGN KEY (sid) REFERENCES students(sid),
	FOREIGN KEY (course_number) REFERENCES courses(cnumber)
);	

-- CREATE TABLE offers (
-- 	course_number INTEGER,
--     department_code INTEGER,
--     PRIMARY KEY (course_number, department_code),
--     FOREIGN KEY (course_number) REFERENCES courses(cnumber) ON DELETE CASCADE,
--     FOREIGN KEY (department_code) REFERENCES departments(dcode) ON DELETE CASCADE
-- );
     
-- CREATE TABLE administer(
-- 	degree_name VARCHAR(50),
-- 	department_code INTEGER,
-- 	PRIMARY KEY (degree_name, department_code),
-- 	FOREIGN KEY (degree_name) REFERENCES degrees(dgname) ON DELETE CASCADE,
-- 	FOREIGN KEY (department_code) REFERENCES departments(dcode) ON DELETE CASCADE
-- );    

CREATE TABLE major (
	name VARCHAR(50),
    level VARCHAR(5),
    sid INTEGER,
    PRIMARY KEY (sid, name, level),
    FOREIGN KEY (sid) REFERENCES students(sid),
    FOREIGN KEY (name, level) REFERENCES degrees(dgname, level) ON DELETE CASCADE
);

CREATE TABLE minor (
    name VARCHAR(50),
    level VARCHAR(5),
	sid INTEGER,
    PRIMARY KEY (sid, name, level),
    FOREIGN KEY (sid) REFERENCES students(sid),
    FOREIGN KEY (name, level) REFERENCES degrees(dgname, level) ON DELETE CASCADE
);
