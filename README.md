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

![image](https://github.com/swietlikm/random_games_simulator/assets/121583766/dd6244ea-ad16-4a6c-bedd-fa1488de0745)
![image](https://github.com/swietlikm/random_games_simulator/assets/121583766/74a5b519-0cb8-4801-a08c-6785282fda1e)

