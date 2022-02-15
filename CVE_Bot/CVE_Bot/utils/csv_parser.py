# from pathlib import Path
from pathlib import Path

import pandas as pd

from bot_root_dir import get_source_data_dir


def cve_all_csv_exist(data_dir) -> bool:
    # 检查csv文件是否存在
    if not data_dir.joinpath("cve_all.csv").exists():
        print("'cve_all.csv' don't exist.")
        return False
    else:
        print("'cve_all.csv' exist.")
        return True


def cve_all_clean_csv_exist(data_dir) -> bool:
    # 检查csv文件是否存在
    if not data_dir.joinpath("cve_all_clean.csv").exists():
        print("'cve_all_clean.csv' don't exist.")
        return False
    else:
        print("'cve_all_clean.csv' exist.")
        return True


def get_clean_csv_path() -> Path:
    return get_source_data_dir().joinpath("cve_all_clean.csv")


def parse_cve_all_csv():
    data_dir = get_source_data_dir()
    in_file = data_dir.joinpath("cve_all.csv")
    if not cve_all_csv_exist(in_file):  # 检查输入文件是否存在
        return

    # 分块迭代读取文件，每次读入chunk-size行
    csv_iterator = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=10000,
                               skiprows=lambda x: x in [0, 1, 3, 4, 5, 6, 7, 8, 9], header=0, index_col=0)
    out_file = data_dir.joinpath("cve_all_clean.csv")  # 输出文件名，与输入文件同路径
    for chunk in csv_iterator:
        # 删去Description列以“**”开头的行，如“** RESERVED ** This candidate has been reserved……”
        chunk = chunk[~chunk["Description"].str.startswith("**")]

        # print(chunk.to_string())
        chunk.to_csv(out_file, mode='a', header=not out_file.exists(), quotechar='"', sep=",", na_rep="", quoting=2)


parse_cve_all_csv()
