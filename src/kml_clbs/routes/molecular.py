from flask import Blueprint, render_template, request

bp = Blueprint('molecular', __name__, url_prefix='/molecular')


@bp.route('/')
def nav():
    return render_template('molecular/nav.html')


# Illumina 下机数据拆分部分
@bp.route('/bcl2fastq', methods=['GET', 'POST'])
def bcl2fastq():
    
    return render_template('molecular/bcl2fastq.html')
