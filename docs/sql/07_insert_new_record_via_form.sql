-- Выполнение запроса на добавление новой записи через форму ввода
-- Пример: добавление нового гостя (ui_client)
-- Примечание: created_at/updated_at в Django обычно задаются автоматически,
-- но в SQL-скрипте их можно заполнить текущим временем.

INSERT INTO ui_client (
  created_at,
  updated_at,
  last_name,
  first_name,
  middle_name,
  birth_date,
  segment,
  preferences,
  notes
) VALUES (
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP,
  :last_name,
  :first_name,
  COALESCE(:middle_name, ''),
  :birth_date,
  COALESCE(:segment, ''),
  :preferences_json,
  COALESCE(:notes, '')
);

-- Получение идентификатора вставленной записи (SQLite)
SELECT last_insert_rowid() AS new_client_id;

