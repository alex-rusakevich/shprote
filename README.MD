Standardized Hanyu PROnunciation TEster
===
This program was created in order to help MSLU students who learn Chinese improve or check their pronunciation

Install all the needed libraries and git hooks to run shprote server:

```sh
pip install pipenv
pipenv install
npm install
husky install
```

Development server is started via command ```inv dev```.

`MySQL 5.7` and newer is required. Before running the app, execute these commands in `mysql` default shell:

```SQL
create database shprote_db;
create user shprote_db_user@localhost;
grant all privileges on shprote_db.* to shprote_db_user@localhost;
alter user shprote_db_user@localhost identified by 'shprote_db_user_password';
flush privileges;
```

> All trees start as seeds, but only their effort determine wether they remain so
