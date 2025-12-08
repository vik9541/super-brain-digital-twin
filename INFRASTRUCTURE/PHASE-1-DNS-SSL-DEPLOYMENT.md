# 🎯 ФАЗА 1: Развертывание DNS и SSL

**Статус:** 🟢 Готово к применению  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Кластер:** super-brain-prod (NYC2)  
**LoadBalancer IP:** 138.197.242.93  
**Дата:** 8 декабря 2025

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ УСЛОВИЯ

- ✅ Kubernetes кластер super-brain-prod создан
- ✅ NGINX Ingress Controller установлен
- ✅ Cert-Manager установлен
- ✅ LoadBalancer создан (IP: 138.197.242.93)
- ✅ Файлы конфигурации созданы:
  - `k8s/cert-manager/cluster-issuer.yaml`
  - `k8s/ingress/api-ingress.yaml`

---

## ⚙️ ШАГ 1: НАСТРОЙКА DNS ЗАПИСЕЙ

### 1.1. Открыть панель регистратора домена 97v.ru

Перейти в панель управления DNS записями для домена 97v.ru.

### 1.2. Добавить/Обновить DNS записи

Добавьте или обновите следующие записи:

```
Тип    Имя             Значение              TTL
----------------------------------------------------
A      @               138.197.242.93      3600
A      api             138.197.242.93      3600
CNAME  www             97v.ru              3600
```

**Пояснения:**
- `@` - корневой домен 97v.ru
- `api` - поддомен api.97v.ru
- `www` - CNAME запись на основной домен

### 1.3. Проверить распространение DNS

Подождите 2-10 минут и проверьте:

```bash
# Проверка основного домена
dig 97v.ru +short
# Ожидаемый результат: 138.197.242.93

# Проверка API поддомена
dig api.97v.ru +short
# Ожидаемый результат: 138.197.242.93

# Проверка WWW поддомена
dig www.97v.ru +short
# Ожидаемый результат: 97v.ru
# Затем: 138.197.242.93

# Проверка с разных DNS серверов
dig 97v.ru @8.8.8.8 +short      # Google DNS
dig 97v.ru @1.1.1.1 +short      # Cloudflare DNS
dig 97v.ru @8.8.4.4 +short      # Google DNS второй
```

**✅ Checklist DNS:**
- [ ] A-запись 97v.ru → 138.197.242.93
- [ ] A-запись api.97v.ru → 138.197.242.93
- [ ] CNAME www.97v.ru → 97v.ru
- [ ] DNS распространился на 3+ DNS серверах
- [ ] ping 97v.ru успешен

---

## 🔐 ШАГ 2: ПРИМЕНЕНИЕ KUBERNETES КОНФИГУРАЦИЙ

### 2.1. Подключение к кластеру

```bash
# Подключить kubectl к DigitalOcean кластеру
doctl kubernetes cluster kubeconfig save 3fbf1852-b6c2-437f-b86e-9aefe81d2ec6

# Проверить подключение
kubectl cluster-info
kubectl get nodes
```

### 2.2. Создание namespace production

```bash
# Создать namespace (если еще не создан)
kubectl create namespace production

# Проверить
kubectl get namespace production
```

### 2.3. Применение ClusterIssuer

```bash
# Применить конфигурацию ClusterIssuer
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml

# Проверить статус
kubectl get clusterissuer

# Ожидаемый вывод:
# NAME                  READY   AGE
# letsencrypt-prod      True    Xs
# letsencrypt-staging   True    Xs

# Детальная информация
kubectl describe clusterissuer letsencrypt-prod
```

**✅ Checklist ClusterIssuer:**
- [ ] ClusterIssuer letsencrypt-prod создан
- [ ] ClusterIssuer letsencrypt-staging создан
- [ ] Статус READY = True
- [ ] Email указан верно (vik9541@bk.ru)

### 2.4. Применение Ingress

```bash
# Применить конфигурацию Ingress
kubectl apply -f k8s/ingress/api-ingress.yaml

# Проверить статус Ingress
kubectl get ingress -n production

# Ожидаемый вывод:
# NAME                   CLASS    HOSTS                                  ADDRESS           PORTS     AGE
# super-brain-ingress    nginx    97v.ru,www.97v.ru,api.97v.ru          138.197.242.93    80, 443   Xs

# Детальная информация
kubectl describe ingress super-brain-ingress -n production
```

**✅ Checklist Ingress:**
- [ ] Ingress super-brain-ingress создан
- [ ] ADDRESS = 138.197.242.93
- [ ] PORTS = 80, 443
- [ ] Hosts настроены: 97v.ru, www.97v.ru, api.97v.ru

---

## 🛡️ ШАГ 3: ПОЛУЧЕНИЕ SSL СЕРТИФИКАТА

### 3.1. Мониторинг создания сертификата

cert-manager автоматически создаст Certificate ресурс. Процесс занимает 2-5 минут.

```bash
# Проверить создание сертификата
kubectl get certificate -n production

# Ожидаемый вывод:
# NAME                    READY   SECRET                  AGE
# super-brain-tls-cert    True    super-brain-tls-cert    Xm

# Детальная информация
kubectl describe certificate super-brain-tls-cert -n production

# Проверить Challenge (в процессе получения)
kubectl get challenge -n production

# Проверить Order
kubectl get order -n production
kubectl describe order -n production

# Проверить Secret
kubectl get secret super-brain-tls-cert -n production
kubectl describe secret super-brain-tls-cert -n production
```

### 3.2. Логи cert-manager (при проблемах)

```bash
# Просмотр логов cert-manager
kubectl logs -n cert-manager deployment/cert-manager -f

# Логи webhook
kubectl logs -n cert-manager deployment/cert-manager-webhook -f

# Логи cainjector
kubectl logs -n cert-manager deployment/cert-manager-cainjector -f
```

**✅ Checklist Certificate:**
- [ ] Certificate super-brain-tls-cert создан
- [ ] Challenge пройден (state: valid)
- [ ] Order завершен (state: valid)
- [ ] Secret super-brain-tls-cert создан
- [ ] READY = True

---

## ✅ ШАГ 4: ПРОВЕРКА HTTPS

### 4.1. Проверка HTTPS доступа

```bash
# Проверить HTTPS доступ
curl -I https://97v.ru
# Ожидаемый результат:
# HTTP/2 503 (backend еще не развернут - это нормально!)
# или HTTP/2 200 (если backend работает)

# Проверка поддоменов
curl -I https://www.97v.ru
curl -I https://api.97v.ru

# Проверка HTTP → HTTPS редиректа
curl -I http://97v.ru
# Ожидаемый результат:
# HTTP/1.1 308 Permanent Redirect
# Location: https://97v.ru/
```

### 4.2. Проверка сертификата

```bash
# Проверить даты действия сертификата
openssl s_client -connect 97v.ru:443 -servername 97v.ru < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Проверить издателя сертификата
openssl s_client -connect 97v.ru:443 -servername 97v.ru < /dev/null 2>/dev/null | openssl x509 -noout -issuer
# Ожидаемый результат: issuer=C = US, O = Let's Encrypt, CN = ...

# Проверить субъект сертификата
openssl s_client -connect 97v.ru:443 -servername 97v.ru < /dev/null 2>/dev/null | openssl x509 -noout -text | grep "DNS:"
# Ожидаемый результат: DNS:97v.ru, DNS:www.97v.ru, DNS:api.97v.ru
```

### 4.3. Онлайн проверка SSL

Откройте в браузере:
- https://www.ssllabs.com/ssltest/analyze.html?d=97v.ru
- https://www.digicert.com/help/

**✅ Checklist HTTPS:**
- [ ] HTTPS работает для 97v.ru
- [ ] HTTPS работает для www.97v.ru
- [ ] HTTPS работает для api.97v.ru
- [ ] HTTP → HTTPS редирект работает
- [ ] Сертификат валидный (не истек)
- [ ] Сертификат от Let's Encrypt
- [ ] Нет ошибок SSL в браузере

---

## 🔧 TROUBLESHOOTING

### Проблема: DNS не распространяется

```bash
# Очистить локальный кэш DNS (Linux)
sudo systemctl restart systemd-resolved

# Очистить локальный кэш DNS (macOS)
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Проверить TTL
dig 97v.ru +noall +answer

# Проверить распространение на разных DNS серверах
for ns in 8.8.8.8 1.1.1.1 8.8.4.4 1.0.0.1; do
  echo "DNS Server: $ns"
  dig @$ns 97v.ru +short
done
```

### Проблема: Certificate не выдается

```bash
# Проверить статус Challenge
kubectl describe challenge -n production

# Проверить Order
kubectl describe order -n production

# Проверить логи cert-manager
kubectl logs -n cert-manager deployment/cert-manager --tail=100

# Проверить доступность домена извне
curl -I http://97v.ru/.well-known/acme-challenge/test

# Удалить и пересоздать сертификат (крайняя мера)
kubectl delete certificate super-brain-tls-cert -n production
kubectl apply -f k8s/ingress/api-ingress.yaml
```

### Проблема: 503 Service Temporarily Unavailable

Это **нормально**! Backend (API service) еще не развернут.
Если HTTPS работает и сертификат валиден → **ФАЗА 1 ЗАВЕРШЕНА ✅**

Backend будет развернут в ФАЗЕ 2.

---

## 🎯 КРИТЕРИИ УСПЕХА

**ФАЗА 1 считается завершенной, когда:**

- ✅ DNS записи обновлены (dig 97v.ru → 138.197.242.93)
- ✅ DNS распространился (проверено с 3+ DNS серверов)
- ✅ ClusterIssuer создан и Ready
- ✅ Ingress создан
- ✅ SSL сертификат получен от Let's Encrypt
- ✅ HTTPS доступен (даже если возвращает 503)
- ✅ HTTP редирект на HTTPS работает
- ✅ Нет ошибок SSL

---

## 📝 ОТЧЕТ О ЗАВЕРШЕНИи

После успешного выполнения, добавьте комментарий в Issue #31:

```markdown
## ✅ ФАЗА 1 ЗАВЕРШЕНА

**Дата:** [DD.MM.YYYY]
**Время выполнения:** [X] минут

### DNS
- ✅ A-запись 97v.ru → 138.197.242.93
- ✅ A-запись api.97v.ru → 138.197.242.93
- ✅ CNAME www.97v.ru → 97v.ru
- ✅ DNS распространился за [X] минут

### SSL/TLS
- ✅ ClusterIssuer letsencrypt-prod создан
- ✅ ClusterIssuer letsencrypt-staging создан
- ✅ Ingress super-brain-ingress создан
- ✅ Certificate получен от Let's Encrypt
- ✅ Срок действия: [notAfter date]

### Проверка HTTPS
```bash
curl -I https://97v.ru
# HTTP/2 503 (backend не развернут - это нормально)
# или
# HTTP/2 200 (если backend уже работает)
```

### Проверка редиректа
```bash
curl -I http://97v.ru
# HTTP/1.1 308 Permanent Redirect
# Location: https://97v.ru/
```

**Статус:** ✅ ГОТОВО К ФАЗЕ 2  
**Следующий шаг:** Развертывание API и Bot
```

---

## 🔗 СЛЕДУЮЩИЕ ШАГИ

После завершения ФАЗЫ 1:

1. 📝 Добавить отчет о завершении в Issue #31
2. ✅ Закрыть Issue #31
3. 🆕 Создать Issue для ФАЗЫ 2 (Secrets и Deployments)
4. 📊 Обновить прогресс в основном README.md

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- **Issue #31:** https://github.com/vik9541/super-brain-digital-twin/issues/31
- **Cluster Dashboard:** https://cloud.digitalocean.com/kubernetes/clusters/3fbf1852-b6c2-437f-b86e-9aefe81d2ec6
- **Infrastructure Docs:** https://github.com/vik9541/super-brain-digital-twin/blob/main/INFRASTRUCTURE/NEW-CLUSTER-SETUP-DEC8-2025.md
- **Let's Encrypt Rate Limits:** https://letsencrypt.org/docs/rate-limits/
- **cert-manager Docs:** https://cert-manager.io/docs/
- **NGINX Ingress Docs:** https://kubernetes.github.io/ingress-nginx/

---

**Кластер:** super-brain-prod (3fbf1852-b6c2-437f-b86e-9aefe81d2ec6)  
**LoadBalancer IP:** 138.197.242.93  
**Домен:** 97v.ru  
**SSL Provider:** Let's Encrypt (Production)
