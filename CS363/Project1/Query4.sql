SELECT DISTINCT students.name
FROM students
JOIN register ON students.sid = register.sid
WHERE register.regtime LIKE '%Fall2022%';
