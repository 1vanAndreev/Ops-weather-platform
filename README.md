# ops-weather-platform

`ops-weather-platform` — портфолио-проект для практики полного DevOps-пути:
от маленького HTTP-сервиса до контейнеризации, DevSecOps, CI/CD, Ansible и подготовки Kubernetes-кластера.

Проект сделан как учебная, но правдоподобная эволюция одного сервиса. Его можно загрузить на GitHub
и использовать как демонстрацию навыков для junior DevOps, infrastructure, CI/CD, service delivery
или NMS-adjacent стажировок.

## Зачем существует проект

Многие учебные репозитории показывают только один слой: приложение, Dockerfile или пару манифестов.
Здесь цель другая: показать, как один сервис постепенно становится эксплуатационно зрелым.
Каждый этап добавляет новую практику и оставляет понятный след в структуре репозитория.

## Архитектура

```text
Client -> FastAPI service -> Provider abstraction -> Mock weather/rates providers
                 |
                 +-> Docker image
                 +-> GitLab CI/CD
                 +-> Ansible host preparation
                 +-> Kubernetes manifests
```

Сервис написан на Python 3.11 и FastAPI. Внешние API заменены чистой provider-абстракцией
с deterministic mock-данными, поэтому приложение запускается без API-ключей и нестабильных сетевых зависимостей.

## API

- `GET /health` — healthcheck сервиса.
- `GET /weather?date=YYYY-MM-DD&city=Moscow` — погодные данные за дату.
- `GET /rates?date=YYYY-MM-DD&base=USD&target=RUB` — курс валютной пары за дату.

Пример:

```bash
curl "http://127.0.0.1:8000/weather?date=2026-04-23&city=Moscow"
curl "http://127.0.0.1:8000/rates?date=2026-04-23&base=USD&target=RUB"
```

## Локальный запуск

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Проверка качества:

```bash
ruff check app tests
pytest -q
```

## Docker

```bash
docker compose up --build
```

Контейнер использует slim-образ, non-root пользователя, healthcheck, read-only filesystem,
отключение Linux capabilities и `no-new-privileges`.

## DevSecOps

Документ: `docs/devsecops.md`.

Основные практики:

- сканирование образа через Trivy;
- генерация SBOM через Syft;
- отдельный пример `docker-compose.secure.yml`;
- базовое hardening-поведение для контейнера.

```bash
docker build -t ops-weather-platform:local .
./scripts/scan-image.sh ops-weather-platform:local
./scripts/generate-sbom.sh ops-weather-platform:local sbom.spdx.json
```

## GitLab CI/CD

Основная CI/CD-реализация находится в `.gitlab-ci.yml`.

Pipeline:

- `lint` — проверка Ruff;
- `test` — pytest;
- `build` — сборка и push Docker-образа;
- `deploy` — ручной деплой только из `main` или `master`.

Pipeline поддерживает staging и production через отдельные manual jobs:

- `deploy_staging`;
- `deploy_production`.

Переменная `DEPLOY_TARGET` показывает параметризованный deploy-сценарий.
В реальной инфраструктуре вместо `echo` использовались бы `kubectl`, Helm или Ansible с protected variables.

## Jenkins как альтернатива

`Jenkinsfile` добавлен как альтернативный пример для команд, где Jenkins остается основным orchestrator.
Он повторяет те же этапы: lint, test, build и manual deploy для `main/master`.
GitLab CI в этом репозитории считается основной реализацией.

## Ansible

Каталог `ansible/` готовит Linux-хосты под Kubernetes:

- `roles/k8s_prereqs` — swap, kernel modules, sysctl, базовые пакеты;
- `roles/crio` — установка CRI-O 1.28+;
- `roles/k8s_packages` — установка kubeadm, kubelet, kubectl;
- `playbooks/prepare-k8s.yml` — общий playbook подготовки.

Пример:

```bash
cd ansible
ansible-playbook playbooks/prepare-k8s.yml
```

## Kubernetes

Документ: `docs/k8s-cluster-setup.md`.

В `k8s/` лежат манифесты:

- namespace;
- configmap;
- deployment;
- service;
- ingress.

Кластерный путь описывает kubeadm, kubectl, CRI-O и Calico.
Проверки включают `kubectl get nodes`, `kubectl get pods -A` и сетевой тест через busybox.

## Что практиковалось

- FastAPI backend и health endpoint.
- Конфигурация через environment variables.
- Логирование и обработка ошибок.
- Dockerfile best practices.
- Docker Compose и secure Compose.
- DevSecOps: image scanning и SBOM.
- GitLab CI/CD с production-style разделением окружений.
- Jenkins pipeline как альтернативный пример.
- Ansible role-based automation.
- Kubernetes deployment manifests.
- Документация уровня портфолио.

## Будущие улучшения

- Подключить реальные weather/rates providers с API keys через secret storage.
- Добавить Helm chart.
- Добавить GitLab security scanning jobs.
- Добавить OpenTelemetry traces и Prometheus metrics.
- Развернуть staging в managed Kubernetes и production-like namespace.
- Добавить Renovate или Dependabot для зависимостей.
