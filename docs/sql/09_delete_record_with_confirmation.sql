-- Выполнение запроса на удаление записи с подтверждением операции
-- Пример: удаление обращения (ui_ticket)
-- В реальной системе чаще используется "мягкое" удаление (статус), однако ниже приведён пример физического удаления.
-- Параметры:
--   :ticket_id

-- 1) Просмотр удаляемой записи (этап подтверждения)
SELECT id, subject, priority, status, updated_at
FROM ui_ticket
WHERE id = :ticket_id;

-- 2) Удаление связанных сообщений (если не настроено каскадирование на уровне БД)
DELETE FROM ui_message
WHERE ticket_id = :ticket_id;

-- 3) Удаление задач, связанных с обращением (если требуется)
DELETE FROM ui_task
WHERE ticket_id = :ticket_id;

-- 4) Удаление обращения
DELETE FROM ui_ticket
WHERE id = :ticket_id;

