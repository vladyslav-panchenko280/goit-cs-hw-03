-- Get tasks for users with specific email domain
SELECT t.* 
FROM tasks t
INNER JOIN users u ON t.user_id = u.id
WHERE u.email LIKE '%@example.com';

