from flask import Blueprint, render_template

from kml_clbs.models.db import (
    get_total_visits,
    get_visits_by_path,
    get_visits_by_day,
    get_visits_by_hour,
    get_unique_ips
)

bp = Blueprint('monitor', __name__, url_prefix='/monitor')


@bp.route('/')
def index():
    """
    显示访问统计监控页面
    """
    # 获取各种统计数据
    total_visits = get_total_visits()
    visits_by_path = get_visits_by_path()
    visits_by_day = get_visits_by_day()
    visits_by_hour = get_visits_by_hour()
    unique_ips = get_unique_ips()
    
    return render_template(
        'monitor/index.html',
        title='访问统计监控',
        total_visits=total_visits,
        visits_by_path=visits_by_path,
        visits_by_day=visits_by_day,
        visits_by_hour=visits_by_hour,
        unique_ips=unique_ips
    )
