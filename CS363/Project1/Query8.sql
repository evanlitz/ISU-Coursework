SELECT name, sid, ssn
FROM students
WHERE name LIKE '%n%' OR name LIKE '%N%'
ORDER BY sid;
