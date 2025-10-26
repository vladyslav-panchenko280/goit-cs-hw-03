-- Get all tasks that are not completed yet
SELECT * 
FROM tasks 
WHERE status_id != (
    SELECT id 
    FROM status 
    WHERE name = 'completed'
);

