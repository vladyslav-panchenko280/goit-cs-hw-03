-- Get list of tasks without description
SELECT * 
FROM tasks 
WHERE description IS NULL OR description = '';

