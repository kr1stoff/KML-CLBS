from src.kml_clbs.config.software_config import OBSUTIL
from src.kml_clbs.config.path_config import DOWNLOADS_DIR, CLBS_DIR

from subprocess import run
from pathlib import Path
import logging
import pandas as pd
from shutil import rmtree


logging.getLogger(__name__).setLevel(logging.DEBUG)


def kras_service(input_nas_path: str, task_id: str) -> str:
    """
    从PCR室的KRAS检测项目中提取KRAS数据文件夹
    """
    logging.info(f'开始处理KRAS数据文件夹')
    logging.debug(f'input_nas_path: {input_nas_path}')
    logging.debug(f'task_id: {task_id}')

    work_dir = DOWNLOADS_DIR.joinpath(task_id)
    work_dir.mkdir(parents=True, exist_ok=True)

    # 从NAS路径构建OBS路径
    # obs://obs-labfilebackup/NAS/source_data_of_kingmylab/原始记录/PCR室/1_检测项目/16_T14492504-kras(G12C)突变检测/06-样本检测/20251225/
    obs_path = input_nas_path.replace(
        '\\\\10.128.220.21', 'obs://obs-labfilebackup/NAS').replace('\\', '/')
    logging.debug(f'obs_path: {obs_path}')

    # obs 下载到本地的文件夹
    # /data/share/clbs/downloads/test-20260109/20251225
    download_from_obs(obs_path, work_dir)
    local_dir = work_dir.joinpath(obs_path.split('/')[-1])
    logging.debug(f'local_dir: {local_dir}')

    # 处理数据
    result_file = work_dir.joinpath(f'{task_id}.xlsx')
    process_kras(local_dir, result_file)
    logging.info(f'KRAS数据处理完成，结果文件: {result_file}')
    # /data/share/clbs/downloads/test-20260109/KRAS-result-analysis.xlsx
    # ! 删除下载目录
    rmtree(local_dir)
    logging.info(f'删除下载目录: {local_dir}')
    # 返回 nginx 相对路径
    return str(result_file).replace(str(CLBS_DIR), '')


def download_from_obs(obs_path: str, work_dir: Path) -> None:
    """
    从OBS下载文件到本地
    """
    logging.info(f'开始从OBS下载文件到本地')
    # * 使用列表拆分开, 防止路径中包含特殊字符, ( 等
    cmd = [OBSUTIL, 'cp', obs_path, str(work_dir), '-r', '-f']
    logging.debug(f'cmd: {cmd}')
    result = run(cmd, capture_output=True, text=True)
    with open(work_dir.joinpath('obsutil.log'), 'w') as f:
        f.write(result.stdout + '\n' + result.stderr)
    if result.returncode != 0:
        logging.error(f'cmd error: {result.stderr}')
        raise Exception(f'cmd error: {result.stderr}')


def process_kras(local_dir: Path, result_file: Path) -> None:
    """
    处理KRAS数据文件夹
    """
    logging.info(f'开始处理KRAS数据文件夹')
    # 查找目录内的原始数据
    raw_file = list(local_dir.glob('*KRAS*PCR*.xls'))[0]
    df = pd.read_excel(raw_file, sheet_name='Results', skiprows=46, usecols=[
                       'Sample Name', 'Target Name', 'Reporter', 'CT'])
    df_fam = df[df['Reporter'] == 'FAM'][['Sample Name', 'Target Name', 'CT']]
    df_fam['Sample Name'] = df_fam['Sample Name'].str.replace(
        r'-\d', '', regex=True)
    df_wide = df_fam.pivot(index='Target Name',
                           columns='Sample Name', values='CT')
    # 按照LYQ的固定顺序排序
    order = ['G12D', 'G12A', 'G12V', 'G12S', 'G12R', 'G12C', 'G13D', 'waikong']
    df_sorted = df_wide.loc[order, sorted(
        df_wide.columns.tolist(), key=sort_key)]
    df_sorted.to_excel(result_file)


def sort_key(x) -> int:
    """按照 POS, NTC, GEN* 的顺序排序，其它放最后"""
    if x == 'POS':
        return 0
    elif x == 'NTC':
        return 1
    elif x.startswith('GEN'):
        return 2
    else:
        return 99
