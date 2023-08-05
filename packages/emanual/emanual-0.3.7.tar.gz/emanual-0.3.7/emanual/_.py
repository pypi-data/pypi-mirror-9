# -*- coding: utf-8 -*-
__author__ = 'jayin'


def is_markdown_file(filename=''):
    """
    判断给定的文件名是否是markdown文件
    """
    if filename.endswith('.md') or filename.endswith('.markdown'):
        return True
    return False


def read_file(file_path):
    import codecs

    with codecs.open(file_path, mode='r', encoding='utf-8') as f:
        return f.read()


def get_markdown_p(content='', word=30):
    """
    获得第一句<p>标签的内容
    :param content: 未渲染,markdown格式内容
    :param word: 若分段失败，则截取内容的长度
    :return: string
    """
    import mistune
    from bs4 import BeautifulSoup

    md = mistune.markdown(content)
    soup = BeautifulSoup(md)

    p = soup.find('p')

    if len(p.text.split(u'。')) > 0:
        return p.text.split(u'。')[0]
    elif len(p.text.split(u'.')) > 0:
        return p.text.split()
    return p.text[0:word]







