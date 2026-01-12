import os
from flask import Flask, request
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'kml_clbs.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 数据库
    from .models import db
    db.init_app(app)

    # 路由
    from .routes import home_route
    app.register_blueprint(home_route.bp)

    from .routes import pcr_route
    app.register_blueprint(pcr_route.bp)

    from .routes import monitor_route
    app.register_blueprint(monitor_route.bp)

    # 启用访问日志中间件
    from .utils.access_log_util import access_log_middleware
    access_log_middleware(app)

    return app
