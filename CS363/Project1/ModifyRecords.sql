UPDATE students
SET name = 'Frank'
WHERE ssn = 144673371;

DELETE FROM major 
WHERE sid = (SELECT sid FROM students WHERE ssn = 144673371);

INSERT INTO major (sid, name, level)
SELECT sid, 'Computer Science', 'MS' 
FROM students WHERE ssn = 144673371;

DELETE FROM register
WHERE regtime = 'Summer2024';