import pandas as pd

from CVE_Bot.utils.csv_parser import get_clean_csv_path

in_file = get_clean_csv_path()
# 分块迭代读取文件，每次读入chunk-size行
df = pd.read_csv(in_file, encoding='utf-8', iterator=True, chunksize=10, header=0)
urls = []
for chunk in df:
    # print(chunk)
    cve_ids = chunk['Name']
    for cve_id in cve_ids:
        url = 'https://www.cvedetails.com/cve/' + cve_id
        urls.append(url)

print(urls)
