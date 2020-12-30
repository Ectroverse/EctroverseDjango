## Getting it setup on a new machine:

(you'll need docker and docker-compose installed, google how to do it for your OS)

0. Copy .env.template to .env (`cp .env.template .env`) and change the secret key if you care about security
1. `docker-compose up -d`
2. `docker exec -it ectroversedjango_python_1 /bin/bash`
3. `python manage.py makemigrations app`
4. `python manage.py migrate`
5. `python manage.py createsuperuser` create a user named admin, with whatever pass you want, you can skip email
6. `python manage.py collectstatic --noinput`
7. `python manage.py generate_planets` (can take a while if its a big galaxy with a lot of planets)
8. FOR NOW- go to http://127.0.0.1:8000/admin and edit the Userstatus for admin, set race and home planet, then go back and go to planets and pick a planet and add a portal, else there's a calc error
9. `python manage.py process_tick` (will eventually get called every 10 minutes with a cronjob)

## Starting up server once its setup

1. `docker-compose up -d`

that's it!  without docker this would be a dozen steps

## To rebuild the containers, like if a config setting changed

`docker-compose up -d --no-deps --build`

## Check it's running

`docker ps` should list all three containers as Up

## Shut it down

`docker-compose down`

## Look at logs

Watch Django's console (i.e. the uwsgi log) with
1. `docker exec -it ectroversedjango_python_1 /bin/bash`
2. `tail -f /tmp/mylog.log`

Nginx log:
`docker logs -f ectroversedjango_nginx_1`

MySQL log:
`docker logs -f ectroversedjango_db_1`

## Console into the python container (which runs the Django app) to poke around or debug something

`docker exec -it ectroversedjango_python_1 /bin/bash`
