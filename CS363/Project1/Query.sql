SELECT c_addr 
FROM students 
WHERE name = 'Gail';

SELECT major.name, major.level 
FROM major
JOIN students ON major.sid = students.sid
WHERE students.name = 'Julie';

SELECT courses.cnumber, courses.cname
FROM courses
JOIN departments ON courses.department_code = departments.dcode
WHERE departments.dname = 'Computer Science'
ORDER BY courses.cnumber;

SELECT students.sid, students.name
FROM students
JOIN register ON students.sid = register.sid
WHERE register.regtime LIKE '%Fall2022%';

SELECT degrees.dgname, degrees.level
FROM degrees
JOIN departments ON degrees.department_code = departments.dcode
WHERE departments.dname = 'Computer Science'
ORDER BY degrees.level;

SELECT students.sid, students.name
FROM students
JOIN minor ON students.sid = minor.sid
ORDER BY students.sid;

SELECT students.name, students.sid
FROM students
JOIN major ON students.sid = major.sid
JOIN register ON students.sid = register.sid
JOIN courses ON register.course_number = courses.cnumber
WHERE LOWER(courses.cname) = 'database'
AND major.level IN ('MS', 'PhD')
ORDER BY students.sid;

SELECT name, sid, ssn
FROM students
WHERE name LIKE '%n%' OR name LIKE '%N%'
ORDER BY sid;

SELECT name, sid, ssn
FROM students
WHERE name BETWEEN 'Amy' AND 'Gail'
ORDER BY name;

SELECT courses.cnumber, courses.cname, 
       COUNT(register.sid) AS student_count
FROM courses
LEFT JOIN register ON courses.cnumber = register.course_number
GROUP BY courses.cnumber, courses.cname
ORDER BY courses.cnumber;

SELECT COUNT(DISTINCT students.sid) AS female_count
FROM students
LEFT JOIN major ON students.sid = major.sid
LEFT JOIN minor ON students.sid = minor.sid
WHERE (major.name = 'Software Engineering' OR minor.name = 'Software Engineering')
AND students.gender = 'F';

SELECT major.name, major.level, COUNT(major.sid) AS student_count
FROM major
GROUP BY major.name, major.level
ORDER BY student_count DESC, major.name
LIMIT 1;

SELECT degrees.dgname, degrees.level, COUNT(*) AS student_count
FROM (
    SELECT major.name, major.level FROM major
    UNION ALL
    SELECT minor.name, minor.level FROM minor
) AS all_degrees
JOIN degrees ON all_degrees.name = degrees.dgname AND all_degrees.level = degrees.level
GROUP BY degrees.dgname, degrees.level
ORDER BY student_count DESC, degrees.dgname
LIMIT 1;