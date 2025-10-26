-- Add new task for a specific user
INSERT INTO tasks (title, description, status_id, user_id) 
VALUES (
    'New task', 
    'Task description', 
    (SELECT id FROM status WHERE name = 'new'), 
    1
);

