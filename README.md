# Random games simulator

You can participate into lotto game by generating unlimited number of coupons and evaluate your winnings upon numbers update.

Tech used: Django + Postgress + Redis + Celery


[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

License: MIT

## Quick setup

    $ pip install -r requirements/local.txt
    $ python manage.py migrate

Rename .env template into .env and add url to your postgress database
### Setting Up Your Users

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

### Running up locally

- Django:

      $ python manage.py runserver

- Celery

      $ celery -A config.celery_app  worker --pool=solo -l info
