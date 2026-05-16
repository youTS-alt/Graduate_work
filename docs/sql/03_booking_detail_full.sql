-- Выполнение запроса на просмотр детализации бронирования с выборкой связанных сущностей
-- Параметры:
--   :booking_id -- идентификатор бронирования (ui_booking.id)

-- 1) Заголовок/параметры бронирования
SELECT
  b.id,
  b.check_in,
  b.check_out,
  b.status,
  b.source,
  b.total_cost,
  b.created_at,
  b.updated_at,
  (c.last_name || ' ' || c.first_name || CASE WHEN c.middle_name <> '' THEN ' ' || c.middle_name ELSE '' END) AS client_fio,
  rc.name AS category_name,
  rt.name AS rate_name,
  r.room_number
FROM ui_booking AS b
JOIN ui_client AS c ON c.id = b.client_id
JOIN ui_roomcategory AS rc ON rc.id = b.category_id
JOIN ui_rate AS rt ON rt.id = b.rate_id
LEFT JOIN ui_room AS r ON r.id = b.room_id
WHERE b.id = :booking_id;

-- 2) Гости в бронировании
SELECT
  bg.id,
  bg.full_name,
  bg.role,
  bg.document,
  bg.created_at
FROM ui_bookingguest AS bg
WHERE bg.booking_id = :booking_id
ORDER BY bg.id ASC;

-- 3) Состав (услуги/пакеты/сборы)
SELECT
  bi.id,
  bi.item_type,
  bi.quantity,
  bi.amount,
  bi.comment,
  bi.created_at,
  s.name AS service_name,
  o.name AS offer_name
FROM ui_bookingitem AS bi
LEFT JOIN ui_service AS s ON s.id = bi.service_id
LEFT JOIN ui_offer AS o ON o.id = bi.offer_id
WHERE bi.booking_id = :booking_id
ORDER BY bi.id ASC;

-- 4) Платежи
SELECT
  p.id,
  p.method,
  p.status,
  p.amount,
  p.provider_ref,
  p.created_at,
  p.updated_at
FROM ui_payment AS p
WHERE p.booking_id = :booking_id
ORDER BY p.created_at DESC, p.id DESC;

-- 5) История изменений (аудит по бронированию)
SELECT
  a.id,
  a.action,
  a.risk,
  a.details,
  a.created_at,
  a.actor_employee_id,
  a.actor_agent_id
FROM ui_auditlog AS a
WHERE a.entity = 'Booking' AND a.entity_id = :booking_id
ORDER BY a.created_at DESC, a.id DESC
LIMIT 50;

