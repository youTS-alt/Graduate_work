-- Выполнение запроса на просмотр обращения с выборкой сообщений и связанных задач
-- Параметры:
--   :ticket_id -- идентификатор обращения (ui_ticket.id)

-- 1) Карточка обращения
SELECT
  t.id,
  t.subject,
  t.priority,
  t.status,
  t.sla_due_at,
  t.booking_id,
  t.created_at,
  t.updated_at,
  (c.last_name || ' ' || c.first_name || CASE WHEN c.middle_name <> '' THEN ' ' || c.middle_name ELSE '' END) AS client_fio
FROM ui_ticket AS t
JOIN ui_client AS c ON c.id = t.client_id
WHERE t.id = :ticket_id;

-- 2) Сообщения в обращении (хронологически)
SELECT
  m.id,
  m.channel,
  m.direction,
  m.text,
  m.attachments,
  m.created_at,
  m.contact_channel_id,
  m.template_id,
  m.campaign_id
FROM ui_message AS m
WHERE m.ticket_id = :ticket_id
ORDER BY m.created_at ASC, m.id ASC;

-- 3) Задачи, связанные с обращением
SELECT
  tk.id,
  tk.type,
  tk.status,
  tk.description,
  tk.due,
  tk.created_at,
  tk.updated_at,
  d.name AS department_name,
  e.full_name AS assignee_name
FROM ui_task AS tk
JOIN ui_department AS d ON d.id = tk.department_id
LEFT JOIN ui_employee AS e ON e.id = tk.assignee_id
WHERE tk.ticket_id = :ticket_id
ORDER BY tk.created_at DESC, tk.id DESC;

