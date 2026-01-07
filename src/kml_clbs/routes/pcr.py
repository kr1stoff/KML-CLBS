from flask import Blueprint, render_template, request

bp = Blueprint('pcr', __name__, url_prefix='/pcr')


@bp.route('/')
def index():
    return render_template('pcr/index.html', title='PCR')


@bp.route('/kras', methods=['GET', 'POST'])
def kras():
    if request.method == 'POST':
        # 处理表单提交
        nas_path = request.form.get('nas_path')
        return f"收到NAS路径: {nas_path}"
    return render_template('pcr/kras.html', title='KRAS')
