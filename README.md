# TSE - Sonic Adventure 2: Battle Boards

The goal of this website is to create an aggregate leaderboard with insightful statistics from the two that already exist, soniccenter.com and speedrun.com.

Currently, this does not contain bosses, single-segment runs, or category extension ILs but will do so in the future.

## Building

Get a secret key from https://djecrety.ir/ then run ``echo secretkeyhere > secret.txt``

To install dependencies and load the db run
```
pip install -r requirements.txt
python manage.py loaddata db.json
```


To run the server, run ``python manage.py runserver`` and navigate to http://localhost:8000

If you need a debug stacktrace for some reason after running the server, set the environment variable ``DEBUG`` to ``1``.

