# DevSecOps: контейнеры, сканирование и SBOM

Этот проект использует простую, но практичную модель DevSecOps для учебного сервиса:
сначала приложение собирается в контейнер, затем образ проверяется на уязвимости,
после этого для него можно сформировать SBOM.

## Сканирование образа

Рекомендуемый инструмент: Trivy.

```bash
docker build -t ops-weather-platform:local .
./scripts/scan-image.sh ops-weather-platform:local
```

Скрипт завершится с ошибкой, если в образе найдены уязвимости уровня HIGH или CRITICAL.
В CI такой шаг можно вынести между `build` и `deploy`, чтобы не продвигать небезопасный образ.

## Генерация SBOM

Рекомендуемый инструмент: Syft.

```bash
docker build -t ops-weather-platform:local .
./scripts/generate-sbom.sh ops-weather-platform:local sbom.spdx.json
```

SBOM помогает показать состав образа: системные пакеты, Python-зависимости и метаданные.
Это полезно для аудита, поставки в enterprise-среду и расследований после CVE.

## Базовое укрепление контейнера

В `Dockerfile` и Compose-конфигурациях применены практики:

- slim-базовый образ Python 3.11;
- запуск приложения от non-root пользователя;
- `read_only: true` для файловой системы контейнера;
- `tmpfs` для временных файлов;
- `cap_drop: [ALL]`;
- `no-new-privileges`;
- healthcheck на `/health`;
- явное управление переменными окружения.

Файл `docker-compose.secure.yml` показывает более строгий вариант запуска с лимитами CPU,
памяти и процессов. Для production-среды секреты не должны храниться в Compose-файлах:
их нужно передавать через CI/CD variables, Vault, Kubernetes Secrets или другой секрет-хранилище.

