## Планировщик автоматических событий

Модуль запускается cron по расписанию, например, каждые 5 минут.
Для рассылок, требующих немедленной отправки, модуль запускается директивно по сигналу django о сохранении такой задачи 
рассылки в базу данных.
Модуль запрашивает из базы данных задачи рассылки со статусом "Pending" и плановым временем исполнения меньше 
текущего времени. 
На основании списков фильтров в поле "user_categories" словаря "context" модуль запрашивает список ids пользователей,
удовлетворяющих данным условиям в AuthAPI. Если заданы другие поля и в модуле настроены их обработчики для запроса данных 
из смежных сервисов (например, запрос информации о фильмах, обложке, жанрах, годе выпуска и др.), осуществляются 
соответствующие запросы в смежные сервисы.

Если список пользователей превышает максимальное значение, установленное для уведомления, то он разбивается на части.
При этом информация об общем количестве частей и номере текущей части указывается в формируемом уведомлении для отправки 
в сервис Notification API.

Входные данные для модуля:
```json
[
  {
    "id": "4478cd72-c09b-4ad1-8ef1-881e4db535c1",
    "service": "admin_panel",
    "created_at": "2022-05-10T20:28:16.117Z",
    "updated_at": "2022-05-10T20:36:35.589Z",
    "title": "Ежемесячная рассылка за май 2022",
    "type_mailing": "To scheduled send",
    "status": "Pending",
    "is_promo": true,
    "priority": "low",
    "template": "28587313-2552-497e-8ed9-9d613bf156ed",
    "context": {
      "user_categories": ["active", "subscriber"]
    },
    "scheduled_datetime": "2022-05-31T12:00:00Z",
    "execution_datetime": null
  },
  {
    "id": "91b5a97a-c20b-4665-9624-a49033d387af",
    "template_type": "weekly_new_movies",
    "created_at": "2022-05-10T19:57:15.299Z",
    "updated_at": "2022-05-10T20:17:20.050Z",
    "title": "Еженедельная подборка фильмов",
    "subject": "Подборка фильмов на выходные",
    "from_email": "noreply@example.com",
    "html_template": "<p><img class=\"mcnImage\" style=\"text-align: center; max-width: 221px; padding-bottom: 0px; vertical-align: bottom; display: block; margin-left: auto; margin-right: auto;\" src=\"https://mcusercontent.com/597bc5462e8302e1e9db1d857/images/7307dfb2-ccc5-4923-937b-4f833c61c341.png\" alt=\"\" width=\"221\" align=\"center\" /></p>\r\n<table style=\"border-collapse: collapse; width: 100%; height: 189.578px; background-color: #c2e0f4;\" border=\"1\">\r\n<tbody>\r\n<tr style=\"text-align: center; height: 34.1562px;\">\r\n<td style=\"width: 100%; height: 34.1562px;\" colspan=\"2\">\r\n<h3 style=\"line-height: 1;\"><span style=\"color: #3e4ff4;\">Здравствуйте, {{ username }}!</span></h3>\r\n</td>\r\n</tr>\r\n<tr style=\"height: 110.641px;\">\r\n<td style=\"width: 100%; height: 110.641px;\" colspan=\"2\">\r\n<p style=\"text-align: center; line-height: 1;\">Вечер пятницы, а это значит что пора отдохнуть от рабочей недели. Закажите пиццу и подумайте какой фильм вам бы хотелось посмотреть. И уж если с пиццей мы вам не сможем облегчить муки выбора, то вполне справимся с фильмом.</p>\r\n<h3 style=\"text-align: center; line-height: 1;\"><span style=\"color: #3e4ff4;\">Ловите персональную подборку</span></h3>\r\n</td>\r\n</tr>\r\n<tr style=\"height: 22.3906px;\">\r\n<td style=\"width: 49.9459%; height: 22.3906px; text-align: center;\">Довод</td>\r\n<td style=\"width: 50.0541%; height: 22.3906px; text-align: center;\">Бегущий по лезвию</td>\r\n</tr>\r\n<tr style=\"height: 22.3906px;\">\r\n<td style=\"width: 49.9459%; height: 22.3906px; text-align: center;\">Апгрейд</td>\r\n<td style=\"width: 50.0541%; height: 22.3906px; text-align: center;\">Электрические сны</td>\r\n</tr>\r\n</tbody>\r\n</table>\r\n<p style=\"text-align: center;\">Чтобы мы писали реже, вы можете <span style=\"text-decoration: underline;\">отписаться от рассылки</span>.</p>",
    "plain_text": "",
    "is_html": true,
    "is_text": false,
    "channel": "email"
  }
]
```

Содержание тела запроса для направления в сервис Notification API:
- для случая с разбиение на части:
```json
{
  "sender": "admin_panel",
  "template_type": "weekly_new_movies",
  "channel": "email",
  "payload": {
    "mailing_id": "4478cd72-c09b-4ad1-8ef1-881e4db535c1",
    "total_chunk": 7,
    "chunk_id": 3,
    "is_promo": true,
    "priority": "low",
    "template_id": "91b5a97a-c20b-4665-9624-a49033d387af",
    "context": {},
    "user_ids": [
      "6567ebaf-0f96-407b-81ad-03670dc3333d",
      "a4aa603a-5b87-4109-a404-4a3ed4b8ef39",
      "986880f0-9b77-4c7f-aa24-a01830e254a2",
      "9a2170c3-53fc-4395-ba3d-a6fffada5eaa",
      "fb2cf3ab-1ff3-46e0-b6a0-e91b688797ce",
      "178ba787-0c57-4d6a-b9ae-cf84081eb3d8",
      "c6120360-4bf8-4941-aa5d-23669fef9422",
      "b2bd34e7-b976-4e09-8e76-8f561505f808",
      "c850237e-252e-4a69-8ed2-775880ff57c7",
      "...",
      "1431e3a3-0f10-469c-96e4-6bad59c8d65e"
    ]
  }
}
```
- для случая с одной частью:
```json
{
  "sender": "admin_panel",
  "template_type": "weekly_new_movies",
  "channel": "email",
  "payload": {
    "mailing_id": "4478cd72-c09b-4ad1-8ef1-881e4db535c1",
    "total_chunk": 1,
    "chunk_id": 1,
    "is_promo": true,
    "priority": "low",
    "template_id": "91b5a97a-c20b-4665-9624-a49033d387af",
    "context": {},
    "user_ids": [
      "6567ebaf-0f96-407b-81ad-03670dc3333d",
      "a4aa603a-5b87-4109-a404-4a3ed4b8ef39",
      "986880f0-9b77-4c7f-aa24-a01830e254a2",
      "9a2170c3-53fc-4395-ba3d-a6fffada5eaa",
      "fb2cf3ab-1ff3-46e0-b6a0-e91b688797ce",
      "178ba787-0c57-4d6a-b9ae-cf84081eb3d8",
      "c6120360-4bf8-4941-aa5d-23669fef9422",
      "b2bd34e7-b976-4e09-8e76-8f561505f808",
      "c850237e-252e-4a69-8ed2-775880ff57c7",
      "...",
      "1431e3a3-0f10-469c-96e4-6bad59c8d65e"
    ]
  }
}
```

Обработка каждой задачи рассылки и запись всех ее частей уведомлений в Notification API должна осуществляться в рамках одной 
транзакции. В случае ошибки в ходе обработки транзакция должна откатываться, для исключения дублирования уведомлений, 
отправляемых для обработки воркерам. Для этого необходимо предусмотреть контроль успешного получения и обработки планировщиком 
и Notification API всех частей уведомлений обрабатываемой задачи рассылки. В случае успешной обработки задачи рассылки планировщиком
статус задачи рассылки в базе данных меняется на "In processing".

