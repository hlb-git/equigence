# Equigence

![Screenshot from 2024-05-14 05-23-39](https://github.com/hlb-git/WeeRent/assets/93451988/c8614db0-7550-4e15-ae57-0a09b0edc28e)

Portfolio Project That Aims to Solve and Automate the Fundamental Data Analyses of Equities for Investors.

### Getting Started
run ``` ./dependencies.sh ``` // for linux users

run ```./mac_dep.sh``` // for mac users


In addition to the above dependencies script, please run the commands below in your
MySQL server to create a user for sqlalchemy

Commands
```
CREATE DATABASE weerent;
CREATE USER 'test'@'localhost' IDENTIFIED BY 'weerentflask200';
GRANT ALL PRIVILEGES ON weerent.* TO 'test'@'localhost';
```
To initialize MySQL on your machine, run this code below:
```
python3 setub_db.py
```

To initialize Gunicorn, run this code below:
```
gunicorn -b 0.0.0.0:5000 run:app
```


