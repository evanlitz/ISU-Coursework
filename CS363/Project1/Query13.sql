SELECT degrees.dgname, degrees.level, COUNT(*) AS student_count
FROM (
    SELECT major.name, major.level FROM major
    UNION ALL
    SELECT minor.name, minor.level FROM minor
) AS all_degrees
JOIN degrees ON all_degrees.name = degrees.dgname AND all_degrees.level = degrees.level
GROUP BY degrees.dgname, degrees.level
ORDER BY student_count DESC, degrees.dgname
LIMIT 1;