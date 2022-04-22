from cvss import CVSS2, CVSS3


def vector_v2_to_v3(v2str):
    c = CVSS2(v2str)
    v3str = v2str
    res = CVSS3(v3str)
    return res


if __name__ == '__main__':
    vector_v2_to_v3('AV:N/AC:L/Au:N/C:N/I:N/A:P')
