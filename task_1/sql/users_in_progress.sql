-- Select users and their tasks with 'in progress' status
SELECT u.username, t.title, t.description, s.name AS status
FROM users u
INNER JOIN tasks t ON u.id = t.user_id
INNER JOIN status s ON t.status_id = s.id
WHERE s.name = 'in progress';

