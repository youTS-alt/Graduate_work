-- Выполнение запроса на формирование доски задач по статусам
-- Вариант 1: получить список задач для дальнейшей группировки на уровне приложения

SELECT
  tk.id,
  tk.type,
  tk.status,
  tk.description,
  tk.due,
  tk.created_at,
  d.name AS department_name,
  e.full_name AS assignee_name,
  tk.ticket_id,
  tk.booking_id
FROM ui_task AS tk
JOIN ui_department AS d ON d.id = tk.department_id
LEFT JOIN ui_employee AS e ON e.id = tk.assignee_id
ORDER BY tk.created_at DESC, tk.id DESC;

-- Вариант 2: агрегирование для счетчиков колонок (если требуется)
SELECT
  tk.status,
  COUNT(*) AS cnt
FROM ui_task AS tk
GROUP BY tk.status
ORDER BY cnt DESC;

