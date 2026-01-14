from flask import request

IGNORE_PATHS = ['/static/', '/favicon.ico']


def access_log_middleware(app):
    """
    访问日志中间件，记录每个请求的信息到数据库。
    """
    @app.before_request
    def log_request_info():
        # 不记录IGNORE_PATHS中的路径的请求
        if any(request.path.startswith(path) for path in IGNORE_PATHS):
            return

        # 记录请求信息到数据库
        from src.kml_clbs.models.db import get_db
        db = get_db()
        db.execute(
            'INSERT INTO access_logs (path, method, ip, user_agent, referrer, timestamp) VALUES (?, ?, ?, ?, ?, datetime(\'now\'))',
            (request.path, request.method, request.remote_addr,
             request.user_agent.string, request.referrer)
        )
        db.commit()
