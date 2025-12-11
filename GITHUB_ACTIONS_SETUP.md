# GitHub Actions Setup Guide

## Проблема

Workflow'ы помечены красным (❌ FAILED) потому что отсутствуют необходимые GitHub Actions secrets для подключения к Kubernetes кластеру.

## Решение

### Шаг 1: Сгенерируйте kubeconfig в base64

```bash
# Если у вас есть kubeconfig файл
cat ~/.kube/config | base64 -w 0

# Скопируйте весь output (включая символы переноса)
```

### Шаг 2: Добавьте secrets в GitHub

1. Перейдите в: `Settings` → `Secrets and variables` → `Actions`
2. Нажмите `New repository secret`
3. Добавьте следующие secrets:

#### Обязательные секреты для deployment:

| Secret Name | Значение | Описание |
|-------------|----------|----------|
| `KUBECONFIG_PROD` | (base64 encoded kubeconfig) | Kubernetes конфигурация (base64 encoded) |
| `DO_API_TOKEN_PROD` | (DigitalOcean API token) | DigitalOcean API token для управления ресурсами |
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | URL вашего Supabase проекта |
| `SUPABASE_ANON_KEY` | (ваш ключ) | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | (ваш ключ) | Supabase service role key |
| `TELEGRAM_BOT_TOKEN` | (ваш token) | Токен вашего Telegram бота |
| `DO_REGISTRY_USERNAME` | (username) | DigitalOcean Container Registry username |
| `DO_REGISTRY_TOKEN` | (token) | DigitalOcean Container Registry token |

### Шаг 3: Проверьте установку

После добавления всех секретов:

1. Перейдите на страницу workflow: 
   ```
   https://github.com/vik9541/super-brain-digital-twin/actions/workflows/deploy-with-secrets.yml
   ```

2. Нажмите кнопку `Run workflow` → `Run workflow` (используется `workflow_dispatch`)

3. Проверьте логи deployment

## Альтернатива: Тестирование без Kubernetes

Если у вас нет готового Kubernetes кластера, используйте validation workflow:

```bash
# Это автоматически запускается при push на k8s/**
# Проверяет синтаксис YAML файлов
https://github.com/vik9541/super-brain-digital-twin/actions/workflows/validate-k8s.yml
```

## Файлы workflows

### 1. `deploy-with-secrets.yml`
- **Назначение**: Deploy на Kubernetes кластер
- **Требует**: Все секреты выше
- **Триггеры**: Push на `main` при изменении k8s/** или workflow файла, или ручной запуск
- **Статус**: ❌ КРАСНЫЙ (требует секреты)

### 2. `validate-k8s.yml` (НОВЫЙ)
- **Назначение**: Проверка синтаксиса Kubernetes YAML файлов
- **Требует**: Ничего
- **Триггеры**: Push на `main` при изменении k8s/**, PR, или ручной запуск
- **Статус**: ✅ ЗЕЛЁНЫЙ (работает без секретов)

## Как добавить secrets из DigitalOcean

### DigitalOcean API Token:

```bash
# 1. Перейти в: DigitalOcean Console → Account → API
# 2. Нажать "Generate New Token"
# 3. Скопировать token в KUBECONFIG_PROD
```

### Kubeconfig из DigitalOcean Kubernetes:

```bash
# 1. Установить doctl
brew install doctl

# 2. Авторизоваться
doctl auth init

# 3. Получить kubeconfig
doctl kubernetes cluster kubeconfig show <cluster-name> | base64 -w 0

# 4. Скопировать весь output в KUBECONFIG_PROD secret
```

### Supabase Keys:

```bash
# 1. Перейти в: supabase.com → Your Project
# 2. Settings → API
# 3. Скопировать:
#    - Project URL → SUPABASE_URL
#    - anon public key → SUPABASE_ANON_KEY
#    - service_role secret key → SUPABASE_SERVICE_ROLE_KEY
```

### Telegram Bot Token:

```bash
# 1. Написать @BotFather в Telegram
# 2. Создать новый bot: /newbot
# 3. Скопировать token в TELEGRAM_BOT_TOKEN
```

### DigitalOcean Container Registry:

```bash
# 1. DigitalOcean Console → Container Registry
# 2. API → New API Token
# 3. Использовать как DO_REGISTRY_TOKEN
# 4. Юзернейм: обычно email или custom username
```

## Troubleshooting

### Если workflow всё ещё красный:

1. **Проверьте логи**:
   ```
   Actions → Deploy Workflow → Latest Run → Logs
   ```

2. **Синтаксис kubeconfig**:
   - Убедитесь что это base64 encoded
   - Проверьте что нет лишних пробелов или символов переноса

3. **Проверьте доступ к кластеру**:
   ```bash
   # На локальной машине
   kubectl --kubeconfig=<your-config> cluster-info
   ```

4. **Убедитесь что namespace существует**:
   ```bash
   kubectl create namespace super-brain-prod
   ```

## Дальнейшие шаги

После успешной установки secrets:

1. ✅ Deploy workflow начнёт работать
2. ✅ Автоматическое развёртывание на Kubernetes при push
3. ✅ Проверка синтаксис YAML файлов
4. ✅ Автоматическое управление секретами

## Дополнительная информация

- [GitHub Actions: Using secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [DigitalOcean: Kubernetes kubeconfig](https://docs.digitalocean.com/products/kubernetes/how-to/connect-kubeconfig/)
- [Kubernetes: Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)
