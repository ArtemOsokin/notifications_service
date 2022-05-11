## Админ-панель для управления рассылками

### Запуск сервиса

_Все команды в терминале выполняются в каталоге notification_service/admin_

1. Переименовать .env.sample в .env.dev
2. Уточнить при необходимости параметры подключения к базе данных (имя пользователя, пароль)
3. Запустить docker-compose командой:
```shell
docker-compose up --build -d
```
4. Подключиться к postgresql командой:
```shell
docker exec -it admin_db_1 psql -U django_user -t notification_database
```
5. Создать схему `notification` командой:
```postgresql
CREATE SCHEMA notification;
```
6. Отключиться от postgresql - `exit`
7. Выполнить миграции django:
```shell
docker exec -it admin_web_1 python manage.py migrate
```
8. Создать суперпользователя для подключения к админке django
```shell
docker exec -it admin_web_1 python manage.py createsuperuser
```
9. Заполнить бд данными. Для этого выполнить скрипт:
```shell
docker exec -it admin_web_1 python manage.py loaddata fixtures/admin_notification_data.json
```
10. Админка доступна по адресу: 
```http request
http://127.0.0.1:8000/admin
```

### Функциональность
Функциональность работы с админ-панелью описана в [диаграмме](../architecture/admin_sequence_diagram.png). 
Реализовано всё, за исключением предварительного просмотра отрендеренного шаблона с данными менеджера и запуска 
планировщика для немедленной отправки уведомления (TO DO).

### Шаблон рассылки / уведомления

Шаблон для рассылки/уведомлений имеет следующий вид:

```json
{
  "pk": "28587313-2552-497e-8ed9-9d613bf156ed",
  "created_at": "2022-05-10T20:17:05.290Z",
  "updated_at": "2022-05-10T20:18:59.025Z",
  "title": "Ежемесячная персональная статистика",
  "subject": "Новинки Practix",
  "from_email": "noreply@example.com",
  "html_template": "<p><img class=\"mcnImage\" style=\"text-align: center; max-width: 221px; padding-bottom: 0px; vertical-align: bottom; display: block; margin-left: auto; margin-right: auto;\" src=\"https://mcusercontent.com/597bc5462e8302e1e9db1d857/images/7307dfb2-ccc5-4923-937b-4f833c61c341.png\" alt=\"\" width=\"221\" align=\"center\" /></p>\r\n<table style=\"border-collapse: collapse; width: 100%; background-color: #C2E0F4;\" border=\"1\">\r\n<tbody>\r\n<tr>\r\n<td style=\"width: 100%;\" colspan=\"2\">\r\n<h3 style=\"text-align: center;\"><span style=\"color: #3e4ff4;\">Здравствуйте, {{ username }}!</span></h3>\r\n</td>\r\n</tr>\r\n<tr>\r\n<td style=\"width: 100%;\" colspan=\"2\">\r\n<p style=\"text-align: center;\">За этот месяц вышло 13 новых фильмов и 8 сериалов. И все они есть в нашем онлайн-кинотеатре! Но что же вы больше всего смотрели в {{ month }}?</p>\r\n<p style=\"text-align: center;\"><strong>В этом месяце вы посмотрели {{ films_month_count }} фильмов.</strong></p>\r\n<p style=\"text-align: center;\"><strong>Из них {{ film_favourite_genre_count }} - {{ favorite_genre }}.</strong></p>\r\n</td>\r\n</tr>\r\n<tr>\r\n<td style=\"width: 49.9459%;\">\r\n<p>Поздравляем, ваше звание - {{ user_title }}!</p>\r\n<p>{{ user_title_description }}</p>\r\n</td>\r\n<td style=\"width: 50.0541%;\">{{ image_url }}</td>\r\n</tr>\r\n</tbody>\r\n</table>\r\n<p style=\"text-align: center;\">Чтобы мы писали реже, вы можете <span style=\"text-decoration: underline;\">отписаться от рассылки</span>.</p>",
  "plain_text": "",
  "is_html": true,
  "is_text": false,
  "template_key": "monthly_personal_statistic_views",
  "adapter": "email"
}
```

### Задание на рассылку

Задание на рассылку имеет следующий вид:

```json
{
  "pk": "4478cd72-c09b-4ad1-8ef1-881e4db535c1"
  "created_at": "2022-05-10T20:28:16.117Z",
  "updated_at": "2022-05-10T20:36:35.589Z",
  "title": "Ежемесячная рассылка за май 2022",
  "status": "To scheduled send",
  "is_promo": true,
  "priority": "low",
  "template": "28587313-2552-497e-8ed9-9d613bf156ed",
  "context": {
    "user_categories": ["active", "subscriber"]
  },
  "scheduled_datetime": "2022-05-31T12:00:00Z",
  "repeat_frequency": "monthly",
  "execution_datetime": null
}
```

При создании задания задается его наименование, выбирается приоритет для рассылки, способ рассылки 
(e-mail, sms, websocket и т.п.), используемый шаблон уведомления, задается контент для шаблона, дата и время плановой 
рассылки, ее периодичность или немедленная рассылка.

На основании этих данных планировщик автоматических уведомлений формирует уведомления и направляет их в Notification API
для дальнейшей обработки и отправки.