SELECT courses.cnumber, courses.cname, 
       COUNT(register.sid) AS student_count
FROM courses
LEFT JOIN register ON courses.cnumber = register.course_number
GROUP BY courses.cnumber, courses.cname
ORDER BY courses.cnumber;