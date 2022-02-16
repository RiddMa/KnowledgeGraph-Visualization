import pandas as pd

from CVE_Bot.utils.csv_parser import get_cve_all_clean_csv_path

if __name__ == "__main__":
    in_file = get_cve_all_clean_csv_path()
    # 分块迭代读取文件，每次读入chunk-size行
    df = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=10, header=0)
    for chunk in df:
        cve_ids = chunk['Name']
        for cve_id in cve_ids:
            url = 'https://www.cvedetails.com/cve/' + cve_id
            print('Start request ' + url)
