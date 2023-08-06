try:
    import time
except ImportError:
    print "Requirement: 'time' module not found."

try:
    import MySQLdb
except ImportError:
    print "Requirement: 'os' module not found."

try:
    import os
except ImportError:
    print "Requirement: 'os' module not found."

METRIC_NORMAL = 0
METRIC_PER_SECOND = 1

default_settings = {
    'connection': {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'db': 'mysql'
    },
    'limit': []
}


def query_cache(settings=None):
    if not settings:
        settings = default_settings

    data_rows = []
    db = MySQLdb.connect(host=settings['connection']['host'],
                         user=settings['connection']['user'],
                         passwd=settings['connection']['password'],
                         db=settings['connection']['db'])
    cur = db.cursor()
    cur.execute("SHOW STATUS LIKE 'Qcache_%'")

    for row in cur.fetchall():
        if settings['limit']:
            if row[0] in settings['limit']:
                data = {
                    'host': os.uname()[1],
                    'service': row[0],
                    'metric': row[1],
                    'state': 'ok',
                    'time': int(time.time()),
                    'tags': [__name__],
                }
                data_rows.append(data)
        else:
            data = {
                'host': os.uname()[1],
                'service': row[0],
                'metric': row[1],
                'state': 'ok',
                'time': int(time.time()),
                'tags': [__name__],
            }
            data_rows.append(data)

    db.close()
    return data_rows


def queries(settings=None):
    if not settings:
        settings = default_settings

    data_rows = []
    db = MySQLdb.connect(host=settings['connection']['host'],
                         user=settings['connection']['user'],
                         passwd=settings['connection']['password'],
                         db=settings['connection']['db'])
    cur = db.cursor()
    cur.execute("SHOW STATUS LIKE 'Queries'")

    for row in cur.fetchone():
        if row[0] in settings['limit']:
            data = {
                'host': os.uname()[1],
                'service': row[0],
                'metric': row[1],
                'state': 'ok',
                'time': int(time.time()),
                'tags': [__name__],
            }
            data_rows.append(data)

    db.close()
    return data_rows


def status(settings=None):
    if not settings:
        settings = default_settings

    data_rows = []
    db = MySQLdb.connect(host=settings['connection']['host'],
                         user=settings['connection']['user'],
                         passwd=settings['connection']['password'],
                         db=settings['connection']['db'])
    cur = db.cursor()
    cur.execute("SHOW STATUS")

    for row in cur.fetchall():
        if settings['limit']:
            if row[0] in settings['limit']:
                data = {
                    'host': os.uname()[1],
                    'service': row[0],
                    'metric': row[1],
                    'state': 'ok',
                    'time': int(time.time()),
                    'tags': [__name__],
                }
                data_rows.append(data)
        else:
            data = {
                'host': os.uname()[1],
                'service': row[0],
                'metric': row[1],
                'state': 'ok',
                'time': int(time.time()),
                'tags': [__name__],
            }
            data_rows.append(data)

    db.close()
    return data_rows