import greenify;greenify.greenify()
from gevent import monkey;monkey.patch_all()
from sqlalchemy import create_engine
from gevent.pool import Pool
import time
import logging


total_transactions = 100
concurrency = 20


def visit_mysql(db, item_id):
    conn = db.connect()
    tran = conn.begin()
    test_id = 'example'
    try:
        #     | id                     | varchar(255) | NO   | PRI | NULL    |       |
        #     | name                   | varchar(255) | NO   |     | NULL    |       |
        #     | test_id                | varchar(255) | NO   | PRI | NULL    |       |
        #     | expires_at             | datetime     | YES  |     | NULL    |       |
        #     | created_at             | datetime     | NO   |     | NULL    |       |
        #     | updated_at             | datetime     | NO   |     | NULL    |       |
        #     | bool_prop              | tinyint(1)   | NO   |     | 0       |       |
        #     | type                   | varchar(255) | YES  |     |         |       |
        conn.execute("insert into tests values('%s', '%s', '%s', null, now(), now(), 0, '')" %
                     (item_id, item_id, test_id))
        tran.commit()
        conn.execute("select id, name, test_id, expires_at, created_at, updated_at, bool_prop, "
                      "type from tests").fetchall()
        conn.execute("select sleep(0.5)")
    except:
        tran.rollback()
        logging.exception("visit mysql")
    finally:
        conn.close()


def clear_database(db):
    conn = db.connect()
    tran = conn.begin()
    try:
        conn.execute("delete from tests")
        tran.commit()
    except:
        tran.rollback()
        logging.exception("tear down")
    finally:
        conn.close()


def g_exception_handler(greenlet):
    logging.warn('{0}'.format(greenlet.exception))


def test_mysql_with(uri):
    db = create_engine(uri, pool_size=concurrency, max_overflow=10)
    clear_database(db)

    start = time.time()

    pool = Pool(concurrency)

    for i in xrange(total_transactions):
        g = pool.spawn(visit_mysql, db, "test%d" % i)
        g.link_exception(g_exception_handler)

    pool.join()
    time_elapse = time.time() - start
    print "%s total %d (%d) %.4f seconds" % (uri, total_transactions, concurrency, time_elapse)


if __name__ == "__main__":
    connection_uris = [
        "mysql://root:@localhost:3306/mysql_drivers_test",
        "mysql+pymysql://root:@localhost:3306/mysql_drivers_test",
        "mysql+oursql://root:@localhost:3306/mysql_drivers_test",
        # "mysql+cymysql://root:@localhost:3306/mysql_drivers_test",
        "mysql+mysqlconnector://root:@localhost:3306/mysql_drivers_test"
    ]
    map(test_mysql_with, connection_uris)
