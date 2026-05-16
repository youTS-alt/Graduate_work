-- Выполнение запроса на редактирование данных существующей записи
-- Пример: изменение статуса и приоритета обращения (ui_ticket)
-- Параметры:
--   :ticket_id
--   :new_status
--   :new_priority

UPDATE ui_ticket
SET
  status = :new_status,
  priority = :new_priority,
  updated_at = CURRENT_TIMESTAMP
WHERE id = :ticket_id;

-- Контроль результата
SELECT id, subject, priority, status, updated_at
FROM ui_ticket
WHERE id = :ticket_id;

