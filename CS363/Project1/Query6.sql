SELECT students.sid, students.name
FROM students
JOIN minor ON students.sid = minor.sid
ORDER BY students.sid;