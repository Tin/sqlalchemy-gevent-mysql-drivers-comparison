sqlalchemy-gevent-mysql-drivers-comparison
==========================================

Compare different mysql drivers working with SQLAlchemy and gevent, see if they support cooperative multitasking using coroutines.

The main purpose of this test is to find which mysql driver has best concurrency performance when we use SQLAlchemy and gevent together.
So we won't test umysql, which isn't compatible with DBAPI 2.0.

## Result example

### 100 sessions, 20 concurrency, each session take 0.5 seconds (by `select sleep`)

```
mysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 50.5239 seconds
mysql+pymysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6847 seconds
mysql+oursql://root:@localhost:3306/mysql_drivers_test total 100 (20) 50.4289 seconds
mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6682 seconds
```

Pure python driver support gevent's monkey patch, so they support cooperative multitasking using coroutines.
That means the main thread won't be block by MySQL calls when you use PyMySQL or mysql-connector-python.

### 1000 sessions, 100 concurrency, each session only have 1 insert and 1 select

```
mysql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 10.1098 seconds
mysql+pymysql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 26.8285 seconds
mysql+oursql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 6.4626 seconds
mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test total 1000 (100) 22.4569 seconds
```

Oursql is faster than MySQLdb in this case.
In pure python driver, mysql-connector-python is a bit faster than PyMySQL.

## Setup

```
mkvirtualenv mysql_drivers_test # workon mysql_drivers_test
pip install --upgrade setuptools pip
pip install -r requirements.txt
python mysql_drivers_comparison.py
```
