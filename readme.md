# Code:

### Q) Where is the codes?
inside **\backend** folder
**app**
**db**
**db_merge_scripts**
**db_migrations**

### Q) Where is the .env?
inside **\backend** folder

# Run The Project in Docker:
### Q) What need to install?
Python 3.8.5
https://www.python.org/downloads/release/python-385/
install if for all users
https://www.youtube.com/watch?v=zYdHr-LxsJ0

Docker Desktop Community 3.0.4
Docker 20.10.2

### Q) What's the command to start the application locally?
inside **\backend** folder
(docker command) `docker-compose up`
Check **docker-compose.yml** file

# Application Page:
### Hosted at Docker
[http://localhost:7003/docs](http://localhost:7003/docs)


### Dev


pip install -r requirements.txt
pip list



docker-compose build
docker-compose up
docker-compose up -d
 
for debug run
python debug.py


Remove everything from docker
https://stackoverflow.com/questions/44785585/how-to-delete-all-local-docker-images
docker system prune -a --volumes


DB credentials:

    port: 54320
    db: postgres
    user: admin
    password: secret

API: 
http://localhost:7003/docs


DB:
pool_size and max_overflow https://stackoverflow.com/a/9999411


Update Db and insert master data:
python run_db.py auto
python run_db.py data

# Added Gmail Support, Future Scope: Office360(outlook, hotmail), yahoo.

## Framework: FastAPI

## DB: Postgre

## Features

- filtering
  
- syncing
  
- get thread and email details
  
- download attachment
  
- sent email and reply with attachment

- read email(automatic mark seen)

- thread view

NB: All the API are added for hubspot like interface

## Possible New Features(Future Scope)

- User assignment to thread
- Delete message