# Pricing Django Based

Pricing Django Based

## Run Server

When running first time, run the following commands
```sh
python -m pip install pipenv
pipenv shell
pipenv install
python manage.py runserver
```

After running the above commands, the server will be running on http://localhost:8000

Next time, run the following command

```sh
pipenv shell
python manage.py runserver
```

## Create Superuser

Run the following command

```sh
python manage.py createsuperuser
```

After running the above command, you will be redirected to the login page! You can create the super user here