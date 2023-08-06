# iasap の setup.py

from distutils.core import setup

setup(
    name = "iasap",
    packages = ["iasap"],
    version = "0.0.2",
    description = "interactive as sonn as possible",
    author = "梅濁酒(umedoblock)",
    author_email = "umedoblock@gmail.com",
    url='http://pypi.python.org/pypi/iasap/',
    download_url = "",
    license='MIT License',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    keywords=['tkinter', 'curses', 'sqlite3', 'key-value store',
              'incremental search'],
    # see
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Topic :: Education',
    ],
    long_description = """\
| interactive as soon as possible (a.k.a iasap)
| --------------------------------------------
| iasap は、key-value store 形式のテキスト検索を目的として開発しました。
| iasap は、incremental 検索機能を実現しています。
| 
| iasap は、key-value store の key, value の保存先として、sqlite3 を使用していま
| す。
| iasap は、tkinter, curses, command prompt のいずれかで、対話的に検索できます。
| iasap は、検索単語に空白を入力せずに検索すると、一致検索を実行します。
| iasap は、検索単語の前に空白を入力すると前方一致検索、 検索単語の後に空白を入力
| すると後方一致検索、を実行します。
| 
| 開発者の私は、手元の PC で英辞郎を使いたくて、
| iasap を開発しました。
| 英辞郎を PC で辞書として使う方法について詳しくは、
| 同梱の README.txt をご覧下さい。
| 
| このバージョンの iasap は、Python3.x で使用してください。
"""
)
