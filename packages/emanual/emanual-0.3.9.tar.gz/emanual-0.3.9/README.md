EManual-CLI
-----------
[![PyPI version](https://badge.fury.io/py/emanual.svg)](http://badge.fury.io/py/emanual)
[![Downloads](https://pypip.in/download/emanual/badge.png)](https://pypi.python.org/pypi/emanual/)

Command Line Interface for EManual

install
-------
```shell
$ pip install emanual
```

Usage
-----

## 语言资料模块

1. 创建`info.json` & 把中文文件名变为拼音
```shell
$ cd path/to/md-xxx
$ emanual create {lang}
// `./dist/{lang}`就是生成的内容
````

2. 生成lang.zip
```shell
$ emanual dist {lang} //lang为指定的语言，小写
```

## NewsFeeds模块

1. 更新
```shell
$ emanual newsfeeds update
```


Development
-----------

1. 使用virtualenv,未安装则`pip install virtualenv`
```shell
//创建虚拟的python开发环境
$ virtualenv env

//开启
$ source env/bin/activate

//退出
$ activate
```

2. 安装依赖
```
$ pip install -r requirements-dev.txt
```

3. 动态加载当前库
```shell
$ cd path/to/EManual-CLI
$ pip install --edit .
//or
$ pip install -e .
```

4. 安装测试
```shell
$ python setup.py install
$ emanual --version
```

dependency
--

- 命令行创建工具[click](https://github.com/mitsuhiko/click)
- 路径解释[path.py](https://github.com/jaraco/path.py)
- 中文转拼音[pypinyin](https://github.com/smallqiao/pypinyin)
- markdown渲染[mistune](https://github.com/lepture/mistune)
- DOM操作[beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)


License
-------

MIT
