import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('models/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """清理存在的数据并创建新表"""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# 访问统计查询函数
def get_total_visits():
    """获取总访问次数"""
    db = get_db()
    result = db.execute('SELECT COUNT(*) as total FROM access_logs').fetchone()
    return result['total'] if result else 0


def get_visits_by_path():
    """按路径分组获取访问次数"""
    db = get_db()
    results = db.execute(
        'SELECT path, COUNT(*) as count FROM access_logs GROUP BY path ORDER BY count DESC'
    ).fetchall()
    return [dict(row) for row in results]


def get_visits_by_day():
    """按天分组获取访问次数"""
    db = get_db()
    results = db.execute(
        "SELECT strftime('%Y-%m-%d', timestamp) as day, COUNT(*) as count "
        'FROM access_logs GROUP BY day ORDER BY day DESC'
    ).fetchall()
    return [dict(row) for row in results]


def get_visits_by_hour():
    """按小时分组获取访问次数"""
    db = get_db()
    results = db.execute(
        "SELECT strftime('%H', timestamp) as hour, COUNT(*) as count "
        'FROM access_logs GROUP BY hour ORDER BY hour'
    ).fetchall()
    return [dict(row) for row in results]


def get_unique_ips():
    """获取唯一IP数量"""
    db = get_db()
    result = db.execute('SELECT COUNT(DISTINCT ip) as unique_ips FROM access_logs').fetchone()
    return result['unique_ips'] if result else 0
