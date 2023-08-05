# -*- coding: utf-8 -*-

from path import Path
import copy
import json

MODE_TREE = 'tree'
MODE_FILE = 'file'

file_tpl = {
    'mode': '',
    'name': '',
    'path': ''
}

info_tpl = {
    'files': [],
    'mode': '',
    'name': '',
    'path': ''
}

root = Path('./markdown')


def check():
    """
    检查是否存在'./markdown'
    :return:
    """
    if not root.exists():
        raise IOError('Not found : dir ./markdown ')


def gen_info(p):
    """
    在`./markdown`下生成info.json
    :param p:
    """
    info = copy.deepcopy(info_tpl)
    info['mode'] = MODE_TREE if p.isdir() else MODE_FILE
    info['name'] = p.name
    info['path'] = p.lstrip('./')
    info['mtime'] = p.mtime
    for f in p.listdir():
        _file = copy.deepcopy(file_tpl)
        _file['mode'] = MODE_TREE if f.isdir() else MODE_FILE
        _file['name'] = f.name
        _file['path'] = info['path'] + '/' + f.name
        _file['mtime'] = f.mtime
        info['files'].append(_file)

    with open(p + '/info.json', mode='w') as f:
        f.write(json.dumps(info))
    for f in p.dirs():
        gen_info(f)


def clean_up(path='./markdown'):
    """
    清除目录下的所有`*.json文件`
    :param path: 清除目录
    """
    import os

    os.system("find {path} -name '*.json' | xargs rm -f ".format(path=path))
    print('Finish: clean up all `*.json` !')


def create_info():
    clean_up()
    check()
    gen_info(root)
    print('Finish: generate info.json')


def dist_zip(lang):
    import os
    cwd = os.getcwd()
    dest = os.path.join(cwd, 'dist')
    if not os.path.exists(dest):
        os.makedirs(dest)

    cmds = [
        'cp -r %s %s ' % (os.path.join(cwd, 'markdown'), os.path.join(dest, lang)),
        'cd %s' % dest,
        'zip -q -r %s.zip %s' % (lang, lang),
        'rm -r %s' % lang
    ]
    os.system(' && '.join(cmds))
    print('Finish dist')



