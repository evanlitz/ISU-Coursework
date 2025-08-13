SELECT major.name, major.level, COUNT(major.sid) AS student_count
FROM major
GROUP BY major.name, major.level
ORDER BY student_count DESC, major.name
LIMIT 1;