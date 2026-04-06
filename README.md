# ChinaGuard

Сервис проверки контрактов с китайскими партнерами по нормам ГК КНР.

## Структура проекта

```
chinaguard/
├── landing/          # Лендинг (index.html)
├── bot/              # Telegram-бот
├── report/           # Генерация PDF-отчетов
└── content/          # Контент для Telegram-канала
```

## Настройка бота

1. Создайте бота через @BotFather в Telegram, получите токен.
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Задайте переменные окружения:
   ```
   export CHINAGUARD_BOT_TOKEN="ваш_токен"
   export CHINAGUARD_ADMIN_ID="ваш_telegram_id"
   ```
4. Запустите бота:
   ```
   python main.py
   ```

## Генерация отчетов

```
cd report
python generate.py
```

## Лендинг

Откройте `landing/index.html` в браузере или разверните на хостинге.

После деплоя замените `YOUR_EMAIL` в форме обратной связи на рабочий адрес.
