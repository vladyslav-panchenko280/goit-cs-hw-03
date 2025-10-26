-- Get list of users who have no tasks
SELECT * 
FROM users 
WHERE id NOT IN (
    SELECT DISTINCT user_id 
    FROM tasks
);

