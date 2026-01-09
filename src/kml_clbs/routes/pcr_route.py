from src.kml_clbs.config.network_config import NGINX_PORT, NGINX_IP
from src.kml_clbs.services.pcr_kras_service import kras_service
from flask import Blueprint, render_template, request
import time
import logging


logging.getLogger(__name__).setLevel(logging.DEBUG)

bp = Blueprint('pcr', __name__, url_prefix='/pcr')


@bp.route('/')
def index():
    return render_template('pcr/index.html', title='PCR')


@bp.route('/kras', methods=['GET', 'POST'])
def kras():
    """
    处理KRAS数据文件夹
    TODO 后续把任务记录在数据库
    """
    if request.method == 'POST':
        # 从表单获取NAS路径
        nas_path = request.form.get('nas_path')
        logging.info(f"收到NAS路径: {nas_path}")
        # 生成任务ID, 格式: pcr-kras-20260109101112
        task_id = 'pcr-kras-' + time.strftime('%Y%m%d%H%M%S', time.localtime())
        logging.info(f"生成任务ID: {task_id}")
        nginx_relative_path = kras_service(nas_path, task_id)
        # 构建Nginx路径
        # http://10.255.24.60:5001/api/downloads/test-20260109/KRAS-result-analysis.xlsx
        nginx_path = f'http://{NGINX_IP}:{NGINX_PORT}/api{nginx_relative_path}'
        # return nginx_path
        return render_template('pcr/kras.html', title='KRAS', result=nginx_path)

    return render_template('pcr/kras.html', title='KRAS')
