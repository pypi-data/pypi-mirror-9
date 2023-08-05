`db_url` provides the `db` command-line utilty for connecting to databases.

Install via pip:

```
$ pip install db_url
```

### Designed for use with PAAS

```
$ export DATABASE_URL=`heroku config:get DATABASE_URL`
$ db
psql (9.4.0, server 9.3.3)
SSL connection (protocol: TLSv1.2, cipher: DHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
Type "help" for help.

d6p6s3877j3em=>
```

### Use with mysql, postgres, sqlite

```
$ export DATABASE_URL='sqlite://'
$ db
SQLite version 3.8.5 2014-08-15 22:37:57
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite> ^D
$ export DATABASE_URL='mysql://razzi@localhost/test_database'
$ db
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 102
Server version: 5.6.22 Homebrew

Copyright (c) 2000, 2014, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

### Database arguments work as expected

Set startup options:

```
$ db -q --variable=PROMPT1="> " --variable=PROMPT2="  "
> SELECT table_name, table_schema
  FROM information_schema.tables
  WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
         table_name         | table_schema
----------------------------+--------------
 django_migrations          | public
 django_content_type        | public
 django_admin_log           | public
 auth_group_permissions     | public
 django_session             | public
 auth_group                 | public
 auth_user_groups           | public
 auth_permission            | public
 auth_user_user_permissions | public
 auth_user                  | public
(10 rows)
```

Run a command:

```
$ db -tA -c '\dt'
public|auth_group|table|razzi
public|auth_group_permissions|table|razzi
public|auth_permission|table|razzi
public|auth_user|table|razzi
public|auth_user_groups|table|razzi
public|auth_user_user_permissions|table|razzi
public|django_admin_log|table|razzi
public|django_content_type|table|razzi
public|django_migrations|table|razzi
public|django_session|table|razzi
```

### Tips + tricks

Connect to local databases

```
$ createdb testdb
$ export DATABASE_URL=postgres:///testdb
$ db
psql (9.4.0)
Type "help" for help.

testdb=#
```
