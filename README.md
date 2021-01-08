## TODO

Put your name after an item if you want to reserve it for yourself, not all items need assignments though

#### v0.1 Remaining Items

- fleets move/exploration/attack
- battle sequence (Rexer already started it)
- operations- just scouting for now
- news
- auto tick update via cronjob (Rexer)
- 2 players registered into 1 empire? (Vladimir)
- when a player is deleted from an empire decrease its number of players (Vladimir)
- give portal on home planet, fix empire 0 (or 1 whatever) for admin

#### v0.2 Remaining Items

- add proper design to rankings tables
- add deletion possibility to account (Vladimir)
- improve html design inside, some parts are shown badly on phone
- forum
- round reset function
- email password recovery
- round ranks for past rounds

#### v0.3 Remaining Items

- new player tutorial
- map bonuses? ancients
- do we need the market?
- other operations, as well as spells and incantations
- move the menu button to the main header and perhaps draw it nicely
- add device fingerprinting to prevent double accounts
- add sliders for mobile version forms

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
8. go to http://127.0.0.1:8000, log in as admin, and choose a race
9. `python manage.py process_tick` (will eventually get called every 10 minutes with a cronjob)
10. go to http://127.0.0.1:8000 and it should work now

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

Database log:
`docker logs -f ectroversedjango_db_1`

## Console into the python container (which runs the Django app) to poke around or debug something

`docker exec -it ectroversedjango_python_1 /bin/bash`
