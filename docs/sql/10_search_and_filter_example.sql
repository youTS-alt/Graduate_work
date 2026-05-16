-- Выполнение запроса на поиск и фильтрацию информации в функциональном разделе системы
-- Пример: поиск гостей по ФИО и фильтр по сегменту, с пагинацией.
-- Параметры:
--   :q         -- строка поиска (например, 'Иван')
--   :segment   -- сегмент (может быть NULL/пустым, если фильтр не нужен)
--   :limit     -- размер страницы
--   :offset    -- смещение

SELECT
  c.id,
  c.last_name,
  c.first_name,
  c.middle_name,
  c.segment,
  c.updated_at
FROM ui_client AS c
WHERE 1=1
  AND (
    c.last_name   LIKE '%' || :q || '%'
    OR c.first_name  LIKE '%' || :q || '%'
    OR c.middle_name LIKE '%' || :q || '%'
  )
  AND (
    :segment IS NULL
    OR :segment = ''
    OR c.segment = :segment
  )
ORDER BY c.updated_at DESC, c.id DESC
LIMIT :limit OFFSET :offset;

