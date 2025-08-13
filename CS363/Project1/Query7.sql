SELECT students.name, students.sid
FROM students
JOIN major ON students.sid = major.sid
JOIN register ON students.sid = register.sid
JOIN courses ON register.course_number = courses.cnumber
WHERE LOWER(courses.cname) = 'database'
AND major.level IN ('MS', 'PhD')
ORDER BY students.sid;