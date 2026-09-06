# ClickUp Connector — Authentication & Credentials Standard

## 1. Supported Authentication Mechanisms
1. **Personal API Token**:
   - Токен вида `pk_...` передается в заголовке `Authorization: <token>`.
2. **OAuth 2.0 Web Flow**:
   - Authorization: `https://app.clickup.com/api?client_id={client_id}&redirect_uri={redirect_uri}`
   - Token Exchange: `POST https://api.clickup.com/api/v2/oauth/token`
3. **Client Credentials**:
   - Для автоматических сервисных аккаунтов через зарегистрированное ClickUp App.

## 2. Storage & Security
- Секреты сохраняются в `ctx.secrets` под ключом `clickup_connections`.
- В UI токены маскируются (`pk_***`).
