from flask import request

# 访问日志中间件
def access_log_middleware(app):
    @app.before_request
    def log_request_info():
        # 记录请求信息到数据库
        from src.kml_clbs.models.db import get_db
        db = get_db()
        db.execute(
            'INSERT INTO access_logs (path, method, ip, user_agent, referrer, timestamp) VALUES (?, ?, ?, ?, ?, datetime(\'now\'))',
            (request.path, request.method, request.remote_addr,
             request.user_agent.string, request.referrer)
        )
        db.commit()
