-- Выполнение запроса на выборку последних записей для главной страницы
-- СУБД: SQLite (Django)

-- 1) Последние бронирования (3 шт.)
SELECT
  b.id,
  (c.last_name || ' ' || c.first_name || CASE WHEN c.middle_name <> '' THEN ' ' || c.middle_name ELSE '' END) AS client_fio,
  b.check_in,
  b.check_out,
  b.status,
  b.source,
  b.total_cost,
  b.created_at
FROM ui_booking AS b
JOIN ui_client  AS c ON c.id = b.client_id
ORDER BY b.created_at DESC, b.id DESC
LIMIT 3;

-- 2) Последние обращения (3 шт.)
SELECT
  t.id,
  t.subject,
  t.status,
  t.priority,
  (c.last_name || ' ' || c.first_name || CASE WHEN c.middle_name <> '' THEN ' ' || c.middle_name ELSE '' END) AS client_fio,
  t.booking_id,
  t.updated_at
FROM ui_ticket AS t
JOIN ui_client AS c ON c.id = t.client_id
ORDER BY t.updated_at DESC, t.id DESC
LIMIT 3;

