import os
import sys
from MiniReadability import *


def main(url):
    if len(url) > 0:
        article_finder = MiniReadability(url)
        try:
            article_text = article_finder.get_article_bs()
        except Exception as e:
            print('Что-то пошло не так при парсинге статьи по ссылке')

        try:
            directory, file_name = get_path_and_file_name_from_url(url)
        except Exception as e:
            print('Что-то не так с парсингом ссылки в имя папки')

        try:
            save_text_to_file(article_text, directory, file_name)
            print('article find and write')
            print('article len = ', len(article_text))
        except OSError as e:
            print('Не смог создать или найти папку для записи статьи')
            print(e)



def save_text_to_file(text, directory, file_name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = directory + file_name
    with open(file_name, 'w') as f:
        f.write(text)


def get_path_and_file_name_from_url(url):
    start = r'://'
    index = url.find(start)
    file_name = url[index + len(start):]
    if file_name[-1] == '/':
        file_name = file_name[:-1]
    index = file_name.rfind('/')
    directory = file_name[:index]
    directory = directory.replace('/', '\\')
    directory = os.getcwd() + '\\output\\' + '\\' + directory + '\\'
    file_name = file_name[index + 1:]
    file_name = file_name.replace('.', '_')
    file_name = file_name.replace('?', '_')
    file_name += '.txt'
    # file_name = directory + file_name
    # print('url = ', url)
    # print('path = ',  directory)
    # print('file name = ', file_name)
    return directory, file_name


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        test_url = sys.argv[1]

    # test_url = r'https://lenta.ru/news/2018/08/13/ecological_tax/'
    # test_url = r'http://www.vesti.ru/doc.html?id=2699112&cid=9'
    # test_url = r'http://expert.ru/2015/12/14/kitaj-zateyal-novuyu-igru-protiv-dollara/'
    # test_url = r'http://htmlbook.ru/html/span '
    # test_url = r'http://rtown.ru/sopernikami-poleta-stanut-12-komand.html'
    main(test_url)
    # input()
else:
    print('not main')
