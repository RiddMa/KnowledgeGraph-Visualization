if __name__ == "__main__":
    cpe23uri = 'cpe:2.3:a:\$0.99_kindle_books_project:\$0.99_kindle_books:6:*:*:*:*:android:*:*'
    a = cpe23uri.split(':')
    # cpe:<cpe_version>:<part>:<vendor>:<product>:<version>:<update>:<edition>:<language>:<sw_edition>:<target_sw>:<target_hw>:<other>
    cpe = {
        'part': a[2],
        'vendor': a[3],
        'product': a[4],
        'version': a[5],
        'update': a[6],
        'edition': a[7],
        'language': a[8],
        'sw_edition': a[9],
        'target_sw': a[10],
        'target_hw': a[11],
        'other': a[12]
    }
    pass
