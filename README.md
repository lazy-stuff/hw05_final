# Yatube


##### Социальная сеть для блогеров

Веб-приложение для блог-платформы. Позволяет создавать собственные аккаунты, писать посты с добавлением картинок и комментировать посты других пользователей. Также осуществлена возможность подписки на других пользователей.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
$ git clone https://github.com/lazy-stuff/hw05_final
$ cd hw05_final
```
Cоздать и активировать виртуальное окружение:

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
$ python3 -m pip install --upgrade pip
$ pip install -r requirements.txt
```

Выполнить миграции:

```
$ python3 manage.py migrate
```

Запустить проект:

```
$ python3 manage.py runserver
```

#### Технологии
  
* [Python](https://www.python.org)

* [Django](https://www.djangoproject.com)

#### Автор
Настя