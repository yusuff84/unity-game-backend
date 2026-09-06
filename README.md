# Unity WebGL Backend API

Backend-сервис для Unity WebGL игры на стеке **Django + Django REST Framework + PostgreSQL + SimpleJWT**, полностью контейнеризированный в **Docker**.

---

## 🎯 Архитектура проекта (Clean Architecture)

В проекте реализовано разделение ответственности по слоям:

```
magomed-game/
├── config/                     # Слой конфигурации проекта
│   ├── settings.py             # Настройки (PostgreSQL, JWT, CORS, HTTPS-security)
│   ├── urls.py                 # Маршруты проекта (Admin, API, Swagger docs)
│   ├── wsgi.py / asgi.py       # WSGI / ASGI интерфейсы
├── apps/
│   └── users/                  # Изолированный доменный модуль пользователей/игроков
│       ├── models.py           # Доменная модель User (username, password hash, email, lives >= 0)
│       ├── services.py         # Сервисный слой (чистая бизнес-логика: регистрация, выдача токенов, жизни)
│       ├── serializers.py      # Слой валидации и сериализации (DRF Serializers)
│       ├── views.py            # Контроллеры/эндпоинты API с Swagger-аннотациями
│       ├── urls.py             # Маршрутизация эндпоинтов авторизации и профиля
│       ├── admin.py            # Чистая архитектура Django Admin (кастомные формы, бейджи, группировка, действия)
│       └── tests/              # Комплексный набор тестов (модели, сервисы, API, админка)
├── docker-compose.yml          # Оркестрация сервисов Web + PostgreSQL
├── Dockerfile                  # Оптимизированный Docker-образ Python 3.12-slim
├── docker-entrypoint.sh        # Скрипт ожидания БД, выполнения миграций и сбора статики
├── requirements.txt            # Зависимости проекта
└── .env.example / .env         # Переменные окружения
```

---

## 🚀 Быстрый запуск в Docker

### 1. Клонирование и настройка окружения
```bash
cp .env.example .env
```
*(При необходимости скорректируйте порты и параметры в `.env`)*

### 2. Запуск контейнеров
```bash
docker compose up -d --build
```

Сервисы:
* **API / Backend:** `http://localhost:8001` (или порт из `WEB_PORT` в `.env`)
* **PostgreSQL:** `localhost:5434` (или порт из `DB_PORT_HOST` в `.env`)
* **Swagger UI документация:** `http://localhost:8001/api/docs/`
* **Django Admin:** `http://localhost:8001/admin/`

### 3. Создание суперпользователя (для входа в админку)
```bash
docker compose exec web python manage.py createsuperuser
```
Или используйте тестового суперпользователя: `admin` / `admin123456`.

---

## 🛡️ Google Material You (M3) Rounded Admin & Чистая архитектура

Административная панель оформлена в стилистике **Google Material You (M3)** с закругленными формами, светлой и темной темами, без лишних элементов и с полной функциональностью:

1. **Google Rounded Design:**
   * **Закругленные Pill-кнопки и бейджи:** все кнопки действий и бейджи имеют закругление `border-radius: 9999px` (форма пилюли, как в современных сервисах Google).
   * **Закругленные карточки и таблицы:** блоки, карточки форм и таблицы имеют плавные радиусы `20px`.
   * **Закругленные поля ввода:** инпуты, селекты и текстовые области с радиусом `14px` и фирменным акцентом Google Blue при фокусе.
   * **Две полноценные темы (Светлая и Тёмная):**
     * ☀️ **Светлая тема (Google Clean White):** мягкий фон `#f8fafd`, белоснежные карточки `#ffffff`, акцент Google Blue `#1a73e8`.
     * 🌙 **Тёмная тема (Google Dark Slate):** глубокий графитовый фон `#131314`, карточки `#1e1f20`, мягкий голубой акцент `#8ab4f8`.
     * Переключатель тем вынесен на видное место в верхнюю панель.

2. **Управление и смена паролей игроков:**
   * **Смена пароля игрока в 1 клик:** в таблице игроков добавлена быстрая кнопка «🔑 Сменить пароль» в каждой строке.
   * **Кнопка смены пароля в карточке игрока:** вверху формы редактирования и в блоке «Учетные данные игрока» расположена заметная кнопка-пилюля «🔑 Сменить пароль игрока».
   * **Валидация и безопасность:** форма смены пароля проверяет совпадение и сложность пароля, сохраняя безопасный хэш PBKDF2 SHA256 (пароли никогда не хранятся в открытом виде).

3. **Ничего лишнего, максимальная понятность:**
   * Боковая панель содержит только нужные разделы: **Игроки (Players)** и **Swagger / ReDoc документация**.
   * Четкие и понятные кнопки: «Войти», «Сохранить», «Добавить игрока», «Удалить».
   * Русскоязычный интерфейс панели управления.

3. **Группировка полей (Fieldsets):**
   * **Account Credentials:** логин, управление хэшированным паролем.
   * **Player Profile & Game Stats:** email, количество жизней `lives`.
   * **Permissions & Status:** права доступа, статусы активности.
   * **Timestamps & Metadata:** дата регистрации и входа.

4. **Визуальные Google-Pill бейджи жизней (`lives_badge`):**
   * 🟢 Зеленый: `>= 5` жизней.
   * 🟡 Янтарный: `1-4` жизней.
   * 🔴 Красный: `0` жизней (Game Over).

5. **Групповые действия для гейм-мастеров:**
   * Сбросить жизни выбранных игроков на 5 (по умолчанию).
   * Добавить `+1` жизнь выбранным игрокам.
   * Обнулить жизни (`0`) выбранным игрокам.

---

## 📡 Спецификация API

### 1. Регистрация игрока
* **URL:** `POST /api/auth/register/`
* **Доступ:** Публичный
* **Тело запроса:**
```json
{
  "username": "player123",
  "password": "password123"
}
```
*(Опционально можно передать `"email": "player@test.com"`)*
* **Ответ (HTTP 201 Created):**
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi...",
  "user": {
    "id": 1,
    "username": "player123",
    "lives": 5
  }
}
```

---

### 2. Авторизация (Логин)
* **URL:** `POST /api/auth/login/`
* **Доступ:** Публичный
* **Тело запроса:**
```json
{
  "username": "player123",
  "password": "password123"
}
```
* **Ответ (HTTP 200 OK):**
```json
{
  "access": "eyJhbGciOi...",
  "refresh": "eyJhbGciOi..."
}
```

---

### 3. Обновление access токена
* **URL:** `POST /api/auth/token/refresh/`
* **Доступ:** Публичный
* **Тело запроса:**
```json
{
  "refresh": "eyJhbGciOi..."
}
```
* **Ответ (HTTP 200 OK):**
```json
{
  "access": "eyJhbGciOi..."
}
```

---

### 4. Получение профиля текущего игрока
* **URL:** `GET /api/auth/me/`
* **Доступ:** Защищен JWT
* **Заголовок:** `Authorization: Bearer <access_token>`
* **Ответ (HTTP 200 OK):**
```json
{
  "id": 1,
  "username": "player123",
  "email": "",
  "lives": 5
}
```

---

### 5. Изменение количества жизней
* **URL:** `PATCH /api/auth/me/lives/`
* **Доступ:** Защищен JWT
* **Заголовок:** `Authorization: Bearer <access_token>`
* **Тело запроса:**
```json
{
  "lives": 4
}
```
* **Ответ при успехе (HTTP 200 OK):**
```json
{
  "lives": 4
}
```
* **Валидация:** Значение `lives < 0` отклоняется с кодом **HTTP 400 Bad Request**:
```json
{
  "lives": [
    "Lives count cannot be negative."
  ]
}
```

---

## 🎮 Пример интеграции в Unity (C# WebGL)

```csharp
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class ApiClient : MonoBehaviour
{
    private const string BaseUrl = "http://localhost:8001/api/auth";
    private string _accessToken = "";

    [System.Serializable]
    public class LivesPayload
    {
        public int lives;
    }

    public IEnumerator UpdateLives(int newLives)
    {
        string json = JsonUtility.ToJson(new LivesPayload { lives = newLives });
        using (UnityWebRequest request = new UnityWebRequest($"{BaseUrl}/me/lives/", "PATCH"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", "Bearer " + _accessToken);

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Lives updated: " + request.downloadHandler.text);
            }
            else
            {
                Debug.LogError("Error updating lives: " + request.downloadHandler.text);
            }
        }
    }
}
```

---

## 🔒 Безопасность и Production-настройки

* **CORS:** настроен через `django-cors-headers`. Разрешенные домены WebGL настраиваются через переменную `CORS_ALLOWED_ORIGINS` (по умолчанию включены локальные и WebGL-порты).
* **HTTPS в production:**
  * Поддержка `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`.
  * `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` конфигурируются через `.env`.
* **Хэширование паролей:** используется стандартный алгоритм Django (PBKDF2 SHA256) без сохранения паролей в открытом виде.

---

## 🧪 Запуск автоматических тестов

В проекте написаны 28 модульных и интеграционных тестов (модель, бизнес-логика сервисов, все REST API эндпоинты, проверка граничных значений и валидации, админка).

Запуск тестов внутри Docker:
```bash
docker compose exec web python manage.py test apps.users
```
Или локально/в изолированном контейнере:
```bash
docker run --rm -v "$(pwd):/app" -e USE_SQLITE=True unity-game-backend:test manage.py test apps.users
```
