import sys
from MiniReadability import *


def main(argv):
    if len(argv) > 0:
        url = argv[0]
        article_finder = MiniReadability(url)
        article_text = article_finder.get_article
        # article_text = Formatter(article_text)
        file_name = get_file_name_from_url(url)
        # print('article:')
        for s in article_text:
            print(s)
        # print(file_name)


def get_file_name_from_url(url):
    return url


if __name__ == '__main__':
    # print('hell')
    # if len(sys.argv) > 1:
    #     main(sys.argv[1])
    test_url = r'https://lenta.ru/news/2018/08/13/ecological_tax/'
    # test_url = r'http://www.vesti.ru/doc.html?id=2699112&cid=9'
    # test_url = r'http://expert.ru/2015/12/14/kitaj-zateyal-novuyu-igru-protiv-dollara/'
    # test_url = r'http://htmlbook.ru/html/span '
    test_arg = [test_url]
    main(test_arg)
else:
    print('not main')
