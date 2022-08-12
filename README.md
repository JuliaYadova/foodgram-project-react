![example workflow](https://github.com/JuliaYadova/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Foodgram - продуктовый помощник
---
## Описание проекта
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### 
---
### Описание Workflow
Workflow состоит из четырёх шагов:
+ tests:
Проверка кода на соответствие PEP8.
+ build_and_push_to_docker_hub:
Сборка и публикация образа на DockerHub.
+ deploy:
Автоматический деплой на боевой сервер при пуше в главную ветку.
+ send_massage:
Отправка уведомления в телеграм-чат.
---
## Подготовка и запуск проекта

1. Клонирование репозитория
Склонируйте репозиторий на локальную машину:
```
git clone https://github.com/JuliaYadova/foodgram-project-react
```
2. Установка на удаленном сервере (Ubuntu):
 + Выполните вход на свой удаленный сервер
   Прежде, чем приступать к работе, необходимо выполнить вход на свой удаленный сервер.

 + Установите docker на сервер:
   Введите команду:
   ```
   sudo apt install docker.io 
   ```
 + Установите docker-compose на сервер:
   Инструкции с официального сайта:
  [Инструкция](https://docs.docker.com/compose/install/)

 + Локально отредактируйте файл nginx.conf
   Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP.

 + Скопируйте подготовленные файлы из каталога infra:
   Скопируйте подготовленные файлы infra/docker-compose.yml и infra/nginx.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yml и home/<ваш_username>/nginx.conf соответственно. Введите команду из корневой папки проекта:
   ```
   scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
   scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
   ```
 + Cоздайте .env файл:
   На сервере создайте файл nano .env и заполните переменные окружения (или создайте этот файл локально и скопируйте файл по аналогии с предыдущим шагом):
   ```
   SECRET_KEY=<xxx> # указывается для защиты работы приложения от посторенного вмешательства подробнее: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key )
   DB_ENGINE=<xxx> # указываем с какой системой управления базами данных (БД) работаем
   DB_NAME=<xxx> # имя БД которая будет создана для приложения
   POSTGRES_USER=<xxx> # логин для подключения к БД
   POSTGRES_PASSWORD=<xxx> # пароль для подключения к БД
   DB_HOST=<xxx> # название сервиса (контейнера)  *Необходимо проверить связанность с настройками в файлах запуска*
   DB_PORT=<xxx> # порт для подключения к БД 
   ```
 + Добавьте Secrets:

   Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432

   DOCKER_PASSWORD=<пароль DockerHub>
   DOCKER_USERNAME=<имя пользователя DockerHub>

   USER=<username для подключения к серверу>
   HOST=<IP сервера>
   PASSPHRASE=<пароль для сервера, если он установлен>
   SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

   TELEGRAM_TO=<ID своего телеграм-аккаунта>
   TELEGRAM_TOKEN=<токен вашего бота>
   ```
 + После успешного деплоя:
   Зайдите на боевой сервер и выполните команды:

   На сервере соберите docker-compose:
   ```
   sudo docker-compose up -d --build
   ```
   Создаем и применяем миграции:
   ```
   sudo docker-compose exec backend python manage.py makemigrations --noinput
   sudo docker-compose exec backend python manage.py migrate --noinput
   ```
   Подгружаем статику
   ```
   sudo docker-compose exec backend python manage.py collectstatic --noinput 
   ```
   Заполнить базу данных:
   ```
   sudo docker-compose exec backend python manage.py from_csv 
   ```
   Создать суперпользователя Django:
   ```
   sudo docker-compose exec backend python manage.py createsuperuser
   ```
 + Проект запущен:
   Проект будет доступен по вашему IP-адресу.
### Документация
Полная документация после запуска доступна по адресу:
```
   /redoc/
```
---
## Автор:
Ядова Юлия

## Сайт:
[Главная страница:](http://178.154.194.146/index)




