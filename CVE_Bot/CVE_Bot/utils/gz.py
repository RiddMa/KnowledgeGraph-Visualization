import gzip


def un_gz(filename):
    """extract .gz file"""
    f_name = filename.parent.joinpath(filename.stem)
    # 获取文件的名称，去掉
    g_file = gzip.GzipFile(filename)
    # 创建gzip对象
    open(f_name, "wb").write(g_file.read())
    # gzip对象用read()打开后，写入open()建立的文件里。
    g_file.close()
    # 关闭gzip对象
