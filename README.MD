Standardized Hanyu PROnunciation TEster
===

![Python version](https://badgen.net/badge/python/v3.11/blue)
![Node.js version](https://badgen.net/badge/node.js/v20/blue)

This program was created in order to help MSLU students who learn Chinese improve or check their pronunciation

Install all the needed libraries and git hooks to run shprote server:

```sh
pip install pipenv

pipenv install
npm install
npx husky install
```

Development server is started via command ```inv dev```.

`MySQL 5.7` and newer is required. Before running the app, execute these commands in `mysql` default shell:

```SQL
create database shprote_db;
alter database shprote_db character set utf8 collate utf8_general_ci;
create user shprote_db_user@localhost;
grant all privileges on shprote_db.* to shprote_db_user@localhost;
alter user shprote_db_user@localhost identified by 'shprote_db_user_password';
flush privileges;
```

### Windows setup
Make sure you have `gettext` available. It's also a part of `poedit`, add `...Poedit\GettextTools\bin` to your `PATH` and reboot.

> All trees start as seeds, but only their effort determine wether they remain so
