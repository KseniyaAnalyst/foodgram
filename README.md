# Foodgram

## Где каждый рецепт — как искусство

### Статус CI/CD
[![Main Foodgram Workflow](https://github.com/KseniyaAnalyst/foodgram/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/KseniyaAnalyst/foodgram/actions/workflows/main.yml) — CI/CD для main branch

---

## Описание проекта

**Foodgram** — онлайн-платформа для публикации рецептов, создания списков покупок и подписок на любимых авторов. Зарегистрированные пользователи могут сохранять рецепты, формировать списки покупок, подписываться на других и делиться своими кулинарными идеями.

---

## Как запустить проект с помощью Docker Compose

1. Клонировать репозиторий:

   ```bash
   git clone https://github.com/KseniyaAnalyst/foodgram.git
   cd foodgram
   ```
2. Перейти в папку infra и запустить проект:

    ```bash
    cd infra
    sudo docker compose up -d
    ```
3. Для загрузки тестовых данных используйте (при необходимости):

    ```bash
    sudo docker compose exec backend python manage.py load_ingredients ../prepared_data/ingredients.json
    sudo docker compose exec backend python manage.py load_tags ../prepared_data/tags.json
    ```

## Основной функционал

- Регистрация и аутентификация пользователей.
- Публикация, редактирование и удаление рецептов.
- Добавление рецептов в избранное.
- Подписка на других пользователей.
- Формирование списка покупок по выбранным рецептам.
- Удобный поиск по тегам и ингредиентам.

## Примеры основных API эндпоинтов

- Получить список пользователей: `GET /api/users/`
- Получить список рецептов: `GET /api/recipes/`
- Добавить рецепт в избранное: `POST /api/recipes/{id}/favorite/`
- Получить список тегов: `GET /api/tags/`
- Поиск ингредиентов: `GET /api/ingredients/?search=...`
- Получить токен: `POST /api/auth/token/login/`

## Документация API

Документация доступна по адресу:  
`/api/docs/`

## Автор

Ваше имя  
Email: your@email.com  
GitHub: [github.com/KseniyaAnalyst](https://github.com/KseniyaAnalyst)
