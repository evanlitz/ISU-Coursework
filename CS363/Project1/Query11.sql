SELECT COUNT(DISTINCT students.sid) AS female_count
FROM students
LEFT JOIN major ON students.sid = major.sid
LEFT JOIN minor ON students.sid = minor.sid
WHERE (major.name = 'Software Engineering' OR minor.name = 'Software Engineering')
AND students.gender = 'F';