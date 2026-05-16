-- Выполнение запроса на просмотр карточки гостя с подгрузкой связанных данных
-- Параметры:
--   :client_id  -- идентификатор гостя (ui_client.id)

-- 1) Основная карточка гостя
SELECT
  c.id,
  c.last_name,
  c.first_name,
  c.middle_name,
  c.birth_date,
  c.segment,
  c.preferences,
  c.notes,
  c.created_at,
  c.updated_at
FROM ui_client AS c
WHERE c.id = :client_id;

-- 2) Контактные каналы
SELECT
  cc.id,
  cc.type,
  cc.value,
  cc.is_primary,
  cc.verified_at,
  cc.priority,
  cc.created_at,
  cc.updated_at
FROM ui_contactchannel AS cc
WHERE cc.client_id = :client_id
ORDER BY cc.is_primary DESC, cc.priority ASC, cc.id ASC;

-- 3) Согласия
SELECT
  cs.id,
  cs.type,
  cs.status,
  cs.source,
  cs.obtained_at,
  cs.revoked_at,
  cs.created_at
FROM ui_consent AS cs
WHERE cs.client_id = :client_id
ORDER BY cs.obtained_at DESC, cs.id DESC;

-- 4) Лояльность (если есть)
SELECT
  l.id,
  l.level,
  l.points,
  l.updated_at
FROM ui_loyalty AS l
WHERE l.client_id = :client_id;

-- 5) Связанные бронирования (последние 20)
SELECT
  b.id,
  b.check_in,
  b.check_out,
  b.status,
  b.source,
  b.total_cost,
  rc.name AS category_name,
  r.room_number
FROM ui_booking AS b
JOIN ui_roomcategory AS rc ON rc.id = b.category_id
LEFT JOIN ui_room AS r ON r.id = b.room_id
WHERE b.client_id = :client_id
ORDER BY b.created_at DESC, b.id DESC
LIMIT 20;

-- 6) Связанные обращения (последние 20)
SELECT
  t.id,
  t.subject,
  t.priority,
  t.status,
  t.booking_id,
  t.updated_at
FROM ui_ticket AS t
WHERE t.client_id = :client_id
ORDER BY t.updated_at DESC, t.id DESC
LIMIT 20;

