# ClickUp Connector — Discovery & Feature Matrix

## 1. Classification of Capabilities

| Capability | Inbound (Imperal -> ClickUp) | Outbound (ClickUp -> Imperal) | Coverage |
| :--- | :---: | :---: | :---: |
| Workspaces & Hierarchy | - | Read (List Teams, Spaces, Folders, Lists) | Read-only |
| Tasks | Write (Create, Update, Delete) | Read (List, Get) | Both |
| Comments | Write (Create Comment) | Read (List Comments) | Both |
| Webhooks | Write (Create Webhook) | Receive (Events) | Both |
| Health Audit | Analytical (Inspect Spaces/Lists/Tasks) | - | Internal |

---

## 2. Feature Tiers

### Tier 1 — Core Essentials
- `connect_clickup`: Подключение по Personal API Token или OAuth 2.0.
- `list_teams`: Получение доступных рабочих пространств.
- `list_spaces`, `list_folders`, `list_lists`: Навигация по структуре проекта.
- `list_tasks`, `get_task`: Чтение задач.
- `create_task`, `update_task`, `delete_task`: Управление жизненным циклом задач.

### Tier 2 — Extended Ecosystem
- `list_comments`, `create_task_comment`: Командные обсуждения в контексте задачи.
- `create_webhook`: Подписка на вебхуки изменений статусов.
- `audit_clickup_health`: Комплексный аудит доступности пространств и незакрытых задач.
