# -*- coding: utf-8 -*-
__author__ = 'jayin'

from path import Path
import _
import os
import copy
import click

# 注意文件名不能用冒号`:`，干脆直接替换成空格!

_Chinese_Punction = [
    u'“', u'”', u'；', u'《', u'》', u'。', u'、', u'，', u'【', u'】', u'（', u'）', u'？', u'：', u':'
]
_English_Punction = [
    u'"', u'"', u';', u'<', u'>', u'.', u',', u',', u'[', u']', u'(', u')', u'?', u' ', u' '
]

# Chinese 2 English
C2E = dict(map(lambda x, y: [x, y], _Chinese_Punction, _English_Punction))


def check(path='.', _echo=True):
    """
    检查路径目录(默认是当前)下的文件名是否存在中文字符的标点
    :param path: 给定目录
    :param _echo: 是否输出log
    :return:  dist
        tpl = {
            'src': '',
            'dest': ''
        }
    """

    path = Path(path)

    result = []
    tpl = {
        'src': '',
        'dest': ''
    }

    def walk(p):
        if p.isfile() and _.is_markdown_file(p):
            # 检查->改名
            _name = p.name
            for prounction in _Chinese_Punction:
                if prounction in _name:
                    # 替换标点
                    _name = _name.replace(prounction, C2E[prounction])

            if _name != p.name:
                rename = copy.deepcopy(tpl)
                rename['src'] = p.abspath()
                rename['dest'] = os.path.join(os.path.dirname(p.abspath()), _name)
                result.append(rename)

        elif p.isdir():
            for f in p.listdir():
                walk(f)

    walk(path)

    if _echo:
        if len(result) == 0:
            click.echo('Good! Not found!')
        else:
            for x in result:
                click.echo(x['src'])

    return result


def fix(path):
    """
    修复存在中文标点的
    :param path:  给定路径
    """

    result = check(path, False)

    for x in result:
        click.echo('mv %s %s' % (x['src'], x['dest']))
        Path.move(x['src'], x['dest'])

    click.echo('Finish: fix all!')





