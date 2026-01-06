from flask import Blueprint, render_template, request

bp = Blueprint('ngs', __name__, url_prefix='/ngs')


@bp.route('/')
def nav():
    return render_template('ngs/nav.html')


# Illumina 下机数据拆分部分
@bp.route('/bcl2fastq', methods=['GET', 'POST'])
def bcl2fastq():
    
    return render_template('ngs/bcl2fastq.html')
