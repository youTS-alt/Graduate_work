-- Выполнение запроса на выборку списка обращений по актуальности и статусу
-- Параметры:
--   :status_1, :status_2 ... (опционально) -- статусы для фильтрации

SELECT
  t.id,
  t.subject,
  t.priority,
  t.status,
  t.booking_id,
  t.sla_due_at,
  t.updated_at,
  (c.last_name || ' ' || c.first_name || CASE WHEN c.middle_name <> '' THEN ' ' || c.middle_name ELSE '' END) AS client_fio
FROM ui_ticket AS t
JOIN ui_client AS c ON c.id = t.client_id
WHERE 1=1
  -- Пример фильтра по статусам:
  -- AND t.status IN (:status_1, :status_2)
ORDER BY t.updated_at DESC, t.id DESC;

