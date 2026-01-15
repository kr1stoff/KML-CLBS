from src.kml_clbs.config.software_config import OBSUTIL
from src.kml_clbs.config.path_config import DOWNLOADS_DIR, CLBS_DIR

from subprocess import run
from pathlib import Path
import logging
import pandas as pd
from shutil import rmtree

# =============== 输出结果 ===============
# Sample			支持多样本
# DetectionSite	    支持多位点，逗号','分隔
# PosInControl	    阳控是否在控
# NtcInControl	    阴控是否在控
# SampleInControl	样本外控是否在控
# ========================================


logging.getLogger(__name__).setLevel(logging.DEBUG)


def download_from_obs(obs_path: str, work_dir: Path) -> None:
    """从OBS下载文件到本地"""
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


def get_details(raw_file: Path) -> pd.DataFrame:
    """获取 检测位点~样本 数据框"""
    # pcr 仪下机固定格式, 跳过前 46 行
    df = pd.read_excel(raw_file, sheet_name='Results', skiprows=46,
                       usecols=['Sample Name', 'Target Name', 'Reporter', 'CT'])
    # 仅读取 FAM 通道
    df_fam = df[df['Reporter'] == 'FAM'][['Sample Name', 'Target Name', 'CT']]
    # 样本名称中去掉 -1, -2 等后缀, 针对 POS-1, POS-2 等样本
    df_fam['Sample Name'] = df_fam['Sample Name'].str.replace(
        r'-\d', '', regex=True)
    # 转换为宽格式
    df_wide = df_fam.pivot(index='Target Name',
                           columns='Sample Name', values='CT')
    # 按照LYQ的固定顺序排序
    order_targets = ['G12D', 'G12A', 'G12V',
                     'G12S', 'G12R', 'G12C', 'G13D', 'waikong']
    df_sorted = df_wide.loc[order_targets,
                            sorted(df_wide.columns.tolist(), key=sort_key)]
    return df_sorted


def is_pos_in_control(df_replace: pd.DataFrame, ct_diff_abs_dict: dict) -> bool:
    """判断阳性是否在控"""
    pos_ser = df_replace['POS']
    # 阳性外控在 9-23 区间外，阳性失控
    if not 9 <= pos_ser['waikong'] <= 23:
        return False
    # 阳控-外控绝对值差小于等于指定阈值
    for target in ct_diff_abs_dict.keys():
        if abs(pos_ser[target]-pos_ser['waikong']) > ct_diff_abs_dict[target]:
            return False
    return True


def is_ntc_in_control(df_replace: pd.DataFrame, ct_diff_abs_dict: dict) -> bool:
    """判断阴性是否在控"""
    ntc_serter = df_replace['NTC']
    # 外控在 9-23 区间内，阴性失控
    if 9 <= ntc_serter['waikong'] <= 23:
        return False
    # 阴控-外控绝对值差小于等于指定阈值，且阴控Ct在10-23区间内，阴性失控
    for target in ct_diff_abs_dict.keys():
        if (abs(ntc_serter[target]-ntc_serter['waikong']) <= ct_diff_abs_dict[target]) and (10 <= ntc_serter[target] <= 23):
            return False
    return True


def calc_sample_type_and_check_in_control(
        df_replace: pd.DataFrame,
        ct_diff_abs_dict: dict,
        pos_in_control: bool,
        ntc_in_control: bool,
) -> list:
    """
    判断样本结果是否在控
    :param df_replace: 替换 undetermined 为 0, 统一参数的数据类型后的数据框
    :param ct_diff_abs_dict: 阳控-外控绝对值差阈值对应表
    :param pos_in_control: 阳性是否在控
    :param ntc_in_control: 阴性是否在控
    :return: 样本结果列表
    """
    # 所有样本结果表格
    sample_results = []
    # 列名删掉POS/NTC，剩下的样本迭代分析
    columns = df_replace.columns.tolist()
    columns.remove('POS')
    columns.remove('NTC')
    sample_types = []
    for sample in columns:
        sample_ser = df_replace[sample]
        # 3. 判断样本分型
        sample_in_control = True
        # 外控在 9-23 区间外，样本失控
        if not 9 <= sample_ser['waikong'] <= 23:
            sample_in_control = False
        # 样本-外控绝对值差小于等于指定阈值，则是该分型
        for target in ct_diff_abs_dict.keys():
            if abs(sample_ser[target]-sample_ser['waikong']) <= ct_diff_abs_dict[target]:
                sample_types.append(target)
        # 计划输出的结果，三在控 + 样本分型
        result = [sample, ','.join(sample_types), pos_in_control,
                  ntc_in_control, sample_in_control]
        sample_results.append(result)
    return sample_results


def get_type_results(df_sorted: pd.DataFrame) -> pd.DataFrame:
    """
    获取样本分型和质控信息
    :param df_sorted: 排序后的 检测位点~样本 数据框
    :return: 样本分型和质控信息数据框
    """
    # 替换 undetermined 为 0, 统一参数的数据类型
    df_replace = df_sorted.replace(
        to_replace="Undetermined", value=0).astype(float)
    # 阳控-外控绝对值差阈值对应表
    ct_diff_abs_dict = {
        'G12D': 12,
        'G12A': 11,
        'G12V': 13,
        'G12S': 12,
        'G12R': 12,
        'G12C': 10,
        'G13D': 7
    }
    # 1. 查看阳性是否在控
    pos_in_control = is_pos_in_control(df_replace, ct_diff_abs_dict)
    # 2. 查看阴性是否在控
    ntc_in_control = is_ntc_in_control(df_replace, ct_diff_abs_dict)
    # 3. 计算样本分型和质控信息
    sample_results = calc_sample_type_and_check_in_control(
        df_replace, ct_diff_abs_dict, pos_in_control, ntc_in_control)
    # 转换为数据框
    type_res_df = pd.DataFrame(
        sample_results,
        columns=['Sample', 'DetectionSite', 'PosInControl',
                 'NtcInControl', 'SampleInControl']
    )
    return type_res_df


def process_kras(local_dir: Path, result_file: Path) -> None:
    """
    处理KRAS数据文件夹
    :param local_dir: 本地数据文件夹路径
    :param result_file: 处理后的Excel文件路径
    """
    logging.info(f'开始处理KRAS数据文件夹')
    # 查找目录内的原始数据
    raw_file = list(local_dir.glob('*KRAS*PCR*.xls'))[0]
    # 获取 检测位点~样本 数据框
    df_sorted = get_details(raw_file)
    # 获取样本分型和质控信息
    type_res_df = get_type_results(df_sorted)
    # 输出到 Excel 文件
    with pd.ExcelWriter(result_file) as writer:
        type_res_df.to_excel(writer, sheet_name="types", index=False)
        df_sorted.to_excel(writer, sheet_name="details")


def kras_service(input_nas_path: str, task_id: str) -> str:
    """
    从PCR室的KRAS检测项目中提取KRAS数据文件夹
    :param input_nas_path: NAS路径
    :param task_id: 任务ID
    :return: 处理后的Excel文件路径
    """
    logging.info(f'开始处理KRAS数据文件夹')
    logging.debug(f'input_nas_path: {input_nas_path}')
    logging.debug(f'task_id: {task_id}')

    # 下载目录
    # /data/share/clbs/downloads/test-20260109/
    work_dir = DOWNLOADS_DIR.joinpath(task_id)
    work_dir.mkdir(parents=True, exist_ok=True)

    # 从NAS路径构建OBS路径
    # obs://obs-labfilebackup/NAS/source_data_of_kingmylab/原始记录/PCR室/1_检测项目/16_T14492504-kras(G12C)突变检测/06-样本检测/20251225/
    obs_path = input_nas_path.replace(
        '\\\\10.128.220.21', 'obs://obs-labfilebackup/NAS').replace('\\', '/')
    logging.debug(f'obs_path: {obs_path}')

    # obs 下载到本地的文件夹
    download_from_obs(obs_path, work_dir)
    local_dir = work_dir.joinpath(obs_path.split('/')[-1])
    logging.debug(f'local_dir: {local_dir}')

    # 处理数据
    result_file = work_dir.joinpath(f'{task_id}.xlsx')
    process_kras(local_dir, result_file)
    logging.info(f'KRAS数据处理完成，结果文件: {result_file}')

    # ! 删除下载目录
    rmtree(local_dir)
    logging.info(f'删除下载目录: {local_dir}')
    # 返回 nginx 相对路径
    return str(result_file).replace(str(CLBS_DIR) + '/', '')
