SELECT major.name, major.level 
FROM major
JOIN students ON major.sid = students.sid
WHERE students.name = 'Julie';