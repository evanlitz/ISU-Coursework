SELECT degrees.dgname, degrees.level
FROM degrees
JOIN departments ON degrees.department_code = departments.dcode
WHERE departments.dname = 'Computer Science'
ORDER BY degrees.level;
