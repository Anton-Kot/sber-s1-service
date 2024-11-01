# S1 Service - Минисервис обработки HTTP-запросов

## Описание
Минисервис для обработки HTTP-запросов из очереди с поддержкой различных БД и асинхронной обработки.

## Возможности
- Асинхронная обработка HTTP-запросов из таблицы `queue_requests`
- Вывод ответов в таблицу `queue_responses`, NULL + error, если ответ получен не был
- Поддержка SQLite, PostgreSQL
- Оптимистичные блокировки
- Настраиваемое число параллельных запросов
- Обработка таймаутов

## Зависимости
- Python 3.11+
- `pip install -r requirements.txt`

## Конфигурация
В `config.yaml` можно настроить:
- Параметры БД
- Параметры сервиса S2
- Число параллельных запросов
- Число повторных попыток

## Запуск
Для заполнения БД тестовыми данными:
```bash
python example/test_data.py
```

Для запуска сервиса:
```bash
python main.py
```