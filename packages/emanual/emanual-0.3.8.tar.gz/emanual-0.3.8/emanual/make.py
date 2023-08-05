# -*- coding: utf-8 -*-

from path import Path
from pypinyin import lazy_pinyin
import copy
import json
import os
import _

MODE_TREE = 'tree'
MODE_FILE = 'file'

file_tpl = {
    'mode': '',
    'name': '',
    'rname': '',
    'path': ''
}

info_tpl = {
    'files': [],
    'mode': '',
    'name': '',
    'rname': '',
    'path': ''
}

raw_md_root = Path('./markdown')
dist_root = Path('./dist')
info_dist_root = './dist/{lang}'


def check_path():
    """
    检查是否存在'./markdown' './dist'
    :return:
    """
    if not raw_md_root.exists():
        raise IOError('Not found : dir ./markdown ')

    if not dist_root.exists():
        dist_root.mkdir()


def gen_info(p):
    """
    在`./markdown`下生成info.json
    :param p: the path
    """
    info = copy.deepcopy(info_tpl)
    info['mode'] = MODE_TREE if p.isdir() else MODE_FILE
    info['name'] = ''.join(lazy_pinyin(p.name))
    info['rname'] = p.name
    # p.rename(info['name'])# 路径也变为拼音
    info['path'] = ''.join(lazy_pinyin(p.lstrip(dist_root)))
    info['mtime'] = p.mtime
    for f in p.listdir():
        _file = copy.deepcopy(file_tpl)
        _file['mode'] = MODE_TREE if f.isdir() else MODE_FILE
        _file['name'] = ''.join(lazy_pinyin(f.name))
        _file['rname'] = f.name
        # _file['path'] = info['path'] + '/' + _file['name']
        _file['path'] = os.path.join(info['path'], _file['name'])
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
    os.system("find {path} -name '*.json' | xargs rm -f ".format(path=path))
    print('Finish: clean up all `*.json` !')


def dirs_pinyin(p):
    """
    将指定的目录下得所有
    :param p:  给定目录
    """
    if p.isfile():
        pinyin = ''.join(lazy_pinyin(p.name))
        # 拼音先隔离dirname，因为父文件夹是最后才转换成拼音
        Path.move(p.abspath(), os.path.join(p.dirname(), pinyin))
        return
    else:
        for x in p.listdir():
            dirs_pinyin(x)
            if x.isdir():
                pinyin = ''.join(lazy_pinyin(x.name))
                Path.move(x.abspath(), os.path.join(x.dirname(), pinyin))


def create_info(lang):
    """
    创建生成info.json文件以及把中文文件名变为拼音
    :return:
    """
    check_path()
    lang_info_dist_root = info_dist_root.format(lang=lang)
    p = Path(lang_info_dist_root)
    if p.exists():
        os.system('rm -fr %s' % lang_info_dist_root)
    Path.copytree(raw_md_root, p)
    gen_info(p)
    dirs_pinyin(p)
    print('Finish: generate info.json, please checkout `%s`' % p)


def dist_zip(lang):
    """
    压缩create后在dist/{lang}下的文件夹到-> `{lang}.zip`
    :param lang: 语言
    """
    cwd = os.getcwd()
    dest = os.path.join(cwd, 'dist')
    if not os.path.exists(dest):
        os.makedirs(dest)

    cmds = [
        'cd %s' % dest,
        'zip -q -r %s.zip %s/' % (lang, lang),
    ]
    os.system(' && '.join(cmds))
    print('Finish dist')


def newsfeeds_update():
    """
    更新newsfeeds模块的信息
    :return:
    """
    # newsfeeds_root -> ./dist/newsfeeds
    check_path()
    newsfeeds_root = Path(os.path.join(dist_root, 'newsfeeds'))
    if newsfeeds_root.exists():
        os.system('rm -fr %s' % newsfeeds_root)
    clean_up(dist_root)

    Path.copytree(raw_md_root, newsfeeds_root)

    files = []

    def get_files(p):
        for f in p.listdir():
            if f.isfile() and _.is_markdown_file(f.name):
                files.append(f)
            elif f.isdir():
                get_files(f)

    def gen_page_info(files):
        tpl = {
            'name': '',
            'rname': '',
            'path': '',
            'description': ''
        }
        sigle_page = 10  # 单页数量
        files.reverse()
        for page in range(1, len(files) / sigle_page + 2):
            _data = []
            for x in files[(page - 1) * sigle_page: page * sigle_page + 1]:
                _tmp = copy.deepcopy(tpl)
                _tmp['name'] = ''.join(lazy_pinyin(x.name))
                _tmp['rname'] = x.name
                _tmp['path'] = ''.join(lazy_pinyin(x.lstrip(dist_root)))
                _tmp['description'] = _.get_markdown_p(_.read_file(x.abspath()))
                _data.append(_tmp)
            with open(os.path.join(dist_root, '%d.json' % page), mode='w') as f:
                f.write(json.dumps(_data))

    get_files(newsfeeds_root)
    gen_page_info(files)
    dirs_pinyin(newsfeeds_root)
    print('Finish newsfeeds update!\ntotal:%d' % len(files))





