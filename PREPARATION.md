# ClickUp Connector — Preparation & Architecture

**Service**: ClickUp  
**Target API**: ClickUp REST API v2  
**Endpoint**: `https://api.clickup.com/api/v2`  
**Auth Endpoint**: `https://app.clickup.com/api` (OAuth 2.0 Web Flow & Personal API Token)  
**Official Docs**: `https://clickup.com/api`

---

## 1. Executive Summary & Market Position
ClickUp — одна из самых быстрорастущих и многофункциональных платформ управления проектами и командной работы (~12% мирового рынка). Коннектор Imperal Cloud предоставляет:
- Подключение по Personal API Token (pk_...) и OAuth 2.0;
- Полную навигацию по 4-уровневой иерархии: Workspace (Team) -> Space -> Folder -> List -> Task;
- Полный CRUD задач (Task ID, статус, приоритет, исполнители);
- Работу с комментариями к задачам;
- Регистрацию вебхуков на события (taskCreated, taskUpdated);
- Value-add аудит здоровья структуры рабочего пространства.

---

## 2. Ключевые архитектурные особенности API
1. **Иерархическая адресация**: Создание задач требует `list_id`, списков — `folder_id` или `space_id`.
2. **Токены**: Личный токен имеет префикс `pk_` и передается в заголовке `Authorization: pk_...` (без префикса Bearer) либо `Bearer` для OAuth.
3. **Пагинация**: Стандартная страничная пагинация (`page=0, 1...`).
4. **Rate Limits**: 100 запросов в минуту на токен.
