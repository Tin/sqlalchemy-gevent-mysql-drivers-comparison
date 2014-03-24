sqlalchemy-gevent-mysql-drivers-comparison
==========================================

Compare different mysql drivers working with SQLAlchemy and gevent, see if they support cooperative multitasking using coroutines.

The main purpose of this test is to find which mysql driver has best concurrency performance when we use SQLAlchemy and gevent together.
So we won't test umysql, which isn't compatible with DBAPI 2.0.

## Verdict

- Pure c version mysql driver has best performance in low concurrency scenario. It's about 2x to 2.5x faster than pure python version. Oursql is the fatest in this category.
- Pure python mysql driver support gevent patch without any hack. And they brings same level of concurrency performance with gevent. PyMySQL has a consistent codebase and good community polularity at pure python mysql driver category. mysql-connector-python has better score, but the pypi package has some problem, so we will won't use it for now. PyMySQL is our choice this time.
- greenify patched MySQLdb (the official native c mysql driver) gives best overall concurrency and absolute performance, but it has a complicated compile process, and we need to rely on a fork of official MySQLdb codebase which is not stable over time.

## Result

### 100 sessions, 20 concurrency, each session take 0.5 seconds (by `select sleep`), simulate high concurrency scenario

```
mysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 50.5239 seconds
mysql+pymysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6847 seconds
mysql+oursql://root:@localhost:3306/mysql_drivers_test total 100 (20) 50.4289 seconds
mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6682 seconds
```

With greenify ptached MySQLdb (mysql-python).

```
mysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.5790 seconds
mysql+pymysql://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6618 seconds
mysql+oursql://root:@localhost:3306/mysql_drivers_test total 100 (20) 50.4437 seconds
mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test total 100 (20) 2.6340 seconds
```

Pure python driver support gevent's monkey patch, so they support cooperative multitasking using coroutines.
That means the main thread won't be block by MySQL calls when you use PyMySQL or mysql-connector-python.

### 1000 sessions, 100 concurrency, each session only have 1 insert and 1 select, simulate high throughput low concurrency scenario

```
mysql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 10.1098 seconds
mysql+pymysql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 26.8285 seconds
mysql+oursql://root:@localhost:3306/mysql_drivers_test total 1000 (100) 6.4626 seconds
mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test total 1000 (100) 22.4569 seconds
```

Oursql is faster than MySQLdb in this case.
In pure python driver, mysql-connector-python is a bit faster than PyMySQL.
use greenify or not won't affect the testing result in this user scenario.

## How to setup greenify

```
mkvirtualenv mysql_drivers_test # workon mysql_drivers_test
pip install --upgrade setuptools pip cython
pip install -r requirements.txt
python mysql_drivers_comparison.py
```

Test with greenify MySQL-python (on OSX with homebrew).

```
mkvirtualenv mysql_drivers_test # workon mysql_drivers_test
pip install --upgrade setuptools pip cython
pip install -r requirements.txt
git clone https://github.com/CMGS/greenify
cd greenify
cmake -G 'Unix Makefiles' -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV CMakeLists.txt
make & make install
cd ..
export LIBGREENIFY_PREFIX=$VIRTUAL_ENV
pip install git+git://github.com/CMGS/greenify.git#egg=greenify # if you are using zsh, use \#egg=greenify
git clone https://github.com/CMGS/mysql-connector-c
cd mysql-connector-c
export DYLD_LIBRARY_PATH=$VIRTUAL_ENV/lib
cmake -G 'Unix Makefiles' -D GREENIFY_INCLUDE_DIR=$VIRTUAL_ENV/include -D GREENIFY_LIB_DIR=$VIRTUAL_ENV/lib -D WITH_GREENIFY=1 -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV CMakeLists.txt
make & make install
cd ..
git clone https://github.com/CMGS/MySQL-python.git
cd MySQL-python
export DYLD_LIBRARY_PATH=$VIRTUAL_ENV/lib
export LIBRARY_DIRS=$VIRTUAL_ENV/lib
export INCLUDE_DIRS=$VIRTUAL_ENV/include
unlink /usr/local/lib/libmysqlclient.18.dylib
ln -s $VIRTUAL_ENV/lib/libmysql.16.dylib /usr/local/lib/libmysqlclient.18.dylib
python setup.py install
brew switch mysql [version] # brew switch mysql 5.6.15 on my env, brew info mysql to check which version is available on your env
cd ..
python mysql_drivers_comparison.py
```

If the greenify doesn't work for you, you can use `otool -L _mysql.so` in your `$VIRTUAL_ENV/lib/python2.7/site-packages` MySQL-python folder. Can't find otool even after you installed XCode's command line tools? Follow this [link](http://reversi.ng/post/63714801645/make-otx-works-in-os-x-mavericks-with-xcode-5).

I need say thank you to [CMGS](https://github.com/CMGS/). He guided me how to install greenify and how it works, he also help me triage the issues I met (include the `otool` part). Make greenify and mysql work on OSX make no sense, you shold do it on your application server which probably will be a linux, hope you will figure out how to.

