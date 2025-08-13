SELECT courses.cnumber, courses.cname
FROM courses
JOIN departments ON courses.department_code = departments.dcode
WHERE departments.dname = 'Computer Science'
ORDER BY courses.cnumber;