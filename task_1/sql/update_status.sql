-- Update status of a specific task
UPDATE tasks 
SET status_id = (
    SELECT id 
    FROM status 
    WHERE name = 'in progress'
)
WHERE id = 1;

