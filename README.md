# API Gateway

FastAPI-сервис, который является единой публичной точкой входа для frontend API requests.

## Назначение

- Проксирует auth requests в `auth-service`.
- Проксирует deployment requests в `deployments-service`.
- Отдает project API через gRPC-вызовы в `projects-service`.
- Отдает внутренние routes для service-to-service flows, включая webhook deployment triggers.
- Проверяет пользовательские и сервисные JWT.

## HTTP API

- `GET /healthz` - проверка состояния сервиса.
- Публичный API расположен под `/api/v1`.
- Внутренний API расположен под `/internal`.

Upstream-сервисы:

- `auth-service` через HTTP.
- `deployments-service` через HTTP.
- `projects-service` через gRPC.

## Конфигурация

Настройки читаются из переменных окружения с префиксом `GATEWAY_`. Для вложенных полей используется разделитель `__`.

Основные переменные:

- `GATEWAY_SERVER__PORT`
- `GATEWAY_SERVER__FRONTEND_URL`
- `GATEWAY_GRPC__PROJECTS_SERVICE_ADDR`
- `GATEWAY_UPSTREAM__AUTH_SERVICE_URL`
- `GATEWAY_UPSTREAM__DEPLOYMENTS_SERVICE_URL`
- `GATEWAY_AUTH__JWT_SECRET`

## Деплой

Helm chart находится в `charts/api-gateway`. GitHub Actions workflow собирает image и деплоит сервис через Helm.

Фронтенд должен обращаться к gateway через:

```text
https://api.xn--d1acmhpe.tech
```
