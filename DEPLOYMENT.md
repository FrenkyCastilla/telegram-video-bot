# Руководство по развертыванию

Подробные инструкции по развертыванию Telegram Video Bot в различных окружениях.

## Содержание

- [Локальное развертывание](#локальное-развертывание)
- [Docker развертывание](#docker-развертывание)
- [VPS/Облачное развертывание](#vpsоблачное-развертывание)
- [Настройка systemd](#настройка-systemd)
- [Мониторинг и логирование](#мониторинг-и-логирование)

## Локальное развертывание

### Требования

- Python 3.11 или выше
- FFmpeg
- Git

### Шаги

1. **Клонирование репозитория**

```bash
git clone <repository-url>
cd telegram-video-bot
```

2. **Настройка окружения**

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

3. **Установка FFmpeg**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Скачайте с https://ffmpeg.org/download.html
```

4. **Настройка переменных окружения**

```bash
cp .env.example .env
nano .env  # или любой другой редактор
```

Заполните:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

5. **Запуск**

```bash
python main.py
```

## Docker развертывание

### Требования

- Docker
- Docker Compose

### Шаги

1. **Подготовка**

```bash
git clone <repository-url>
cd telegram-video-bot
cp .env.example .env
nano .env  # Заполните токены
```

2. **Сборка и запуск**

```bash
# Сборка образа
docker-compose build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

3. **Обновление**

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Полезные команды Docker

```bash
# Проверка статуса
docker-compose ps

# Перезапуск
docker-compose restart

# Просмотр логов за последний час
docker-compose logs --since 1h

# Вход в контейнер
docker-compose exec telegram-bot bash

# Очистка старых образов
docker system prune -a
```

## VPS/Облачное развертывание

### Рекомендуемые провайдеры

- DigitalOcean (Droplet)
- AWS (EC2)
- Google Cloud (Compute Engine)
- Hetzner
- Linode

### Минимальные требования

- 1 CPU
- 512 MB RAM
- 10 GB SSD
- Ubuntu 22.04 LTS

### Пошаговая инструкция (Ubuntu)

1. **Подключение к серверу**

```bash
ssh root@your-server-ip
```

2. **Обновление системы**

```bash
apt-get update
apt-get upgrade -y
```

3. **Установка Docker**

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
apt-get install docker-compose-plugin -y
```

4. **Создание пользователя (опционально)**

```bash
adduser botuser
usermod -aG docker botuser
su - botuser
```

5. **Клонирование и настройка**

```bash
git clone <repository-url>
cd telegram-video-bot
cp .env.example .env
nano .env  # Заполните токены
```

6. **Запуск**

```bash
docker-compose up -d
```

7. **Настройка автозапуска**

Docker Compose автоматически перезапустит контейнер при перезагрузке сервера благодаря `restart: unless-stopped`.

## Настройка systemd

Для запуска бота без Docker через systemd:

1. **Создание service файла**

```bash
sudo nano /etc/systemd/system/telegram-video-bot.service
```

2. **Содержимое файла**

```ini
[Unit]
Description=Telegram Video Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram-video-bot
Environment="PATH=/home/botuser/telegram-video-bot/venv/bin"
ExecStart=/home/botuser/telegram-video-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Активация и запуск**

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable telegram-video-bot

# Запуск
sudo systemctl start telegram-video-bot

# Проверка статуса
sudo systemctl status telegram-video-bot

# Просмотр логов
sudo journalctl -u telegram-video-bot -f
```

4. **Управление сервисом**

```bash
# Остановка
sudo systemctl stop telegram-video-bot

# Перезапуск
sudo systemctl restart telegram-video-bot

# Отключение автозапуска
sudo systemctl disable telegram-video-bot
```

## Мониторинг и логирование

### Просмотр логов

**Docker:**
```bash
docker-compose logs -f
docker-compose logs --tail=100
docker-compose logs --since 1h
```

**Systemd:**
```bash
sudo journalctl -u telegram-video-bot -f
sudo journalctl -u telegram-video-bot --since "1 hour ago"
```

### Настройка ротации логов

Docker Compose уже настроен на ротацию логов (см. `docker-compose.yml`):
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Мониторинг ресурсов

```bash
# Docker
docker stats telegram-video-bot

# Системные ресурсы
htop
free -h
df -h
```

### Алерты и уведомления

Для production окружения рекомендуется настроить:

- **Healthcheck**: добавить endpoint для проверки здоровья бота
- **Prometheus + Grafana**: для метрик и дашбордов
- **Sentry**: для отслеживания ошибок
- **Uptime monitoring**: UptimeRobot, Pingdom и т.д.

## Безопасность

### Рекомендации

1. **Firewall**

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

2. **SSH ключи**

```bash
# Отключить парольную аутентификацию
sudo nano /etc/ssh/sshd_config
# Установить: PasswordAuthentication no
sudo systemctl restart sshd
```

3. **Обновления**

```bash
# Автоматические обновления безопасности
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

4. **Ограничение доступа к .env**

```bash
chmod 600 .env
```

## Резервное копирование

### Что бэкапить

- `.env` файл (токены)
- Конфигурационные файлы
- Логи (опционально)

### Скрипт бэкапа

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/telegram-bot-$DATE.tar.gz \
    .env \
    docker-compose.yml \
    logs/

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "telegram-bot-*.tar.gz" -mtime +7 -delete
```

## Устранение неполадок

### Бот не запускается

1. Проверьте логи
2. Проверьте .env файл
3. Проверьте доступность API

### Высокое использование ресурсов

1. Проверьте размер temp директории
2. Настройте очистку старых файлов
3. Увеличьте ресурсы сервера

### Ошибки API

1. Проверьте лимиты API
2. Проверьте валидность ключей
3. Проверьте сетевое соединение

## Масштабирование

Для обработки большого количества запросов:

1. **Горизонтальное масштабирование**: запустите несколько инстансов бота
2. **Очередь задач**: используйте Celery + Redis для асинхронной обработки
3. **Балансировка нагрузки**: используйте nginx для распределения запросов
4. **Кэширование**: кэшируйте частые запросы

## Поддержка

При возникновении проблем:

1. Проверьте логи
2. Изучите документацию
3. Создайте issue в репозитории
4. Обратитесь в поддержку
