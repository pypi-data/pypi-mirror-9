# Copyright 2011-2015 梅濁酒(umedoblock)

= 概要
interactive as soon as possible (a.k.a iasap)

iasap は、key-value store 形式のテキスト検索を目的として開発しました。
iasap は、incremental 検索機能を実現しています。

iasap は、key-value store の key, value の保存先として、sqlite3 を使用していま
す。
iasap は、tkinter, curses, command prompt のいずれかで、対話的に検索できます。
iasap は、検索単語に空白を入力せずに検索すると、一致検索を実行します。
iasap は、検索単語の前に空白を入力すると前方一致検索、 検索単語の後に空白を入力
すると後方一致検索、を実行します。

= ライセンス
iasap のライセンスは、「Mit License」です。
詳しくは、LICENSE.txt をご覧下さい。
LICENSE.txt の参考として、LICENSE.ja.txt もご覧下さい。

= 具体的な使い方
英語の辞書としての使用を想定しています。
開発者の私は、手元のPCで英辞郎を使用したくて、iasap の開発を始めました。

私の用意している script を使って英辞郎を使うには、一行テキスト形式の英辞郎辞書
ファイルが必要です。
PDIC を使うなどして、一行テキスト形式の英辞郎辞書ファイルを手に入れてください。

「一行テキスト形式の英辞郎辞書ファイル」とは、以下のように、英単語と日本語訳を
" /// " で区切っているファイルのことです。

abc /// エービーシー
def /// ディーイーエフ
ghi /// ジーエイチアイ

以下では、一行テキスト形式の英辞郎辞書ファイルを
eijiro98.txt
と仮定して、iasapの使用方法を説明します。

= 英辞郎を iasap で使えるようにするまで
iasap の root directory を、IASAP_ROOT とします。

まず、IASAP_ROOT directory まで移動します。
$ cd IASAP_ROOT

移動先の IASAP_ROOT directory 以下に、iasap, kit directory が配置されている
ことを確認します。

確認後、 eijiroXXX directory に移動します。
$ cd ./kit/eijiroXXX/

英辞郎辞書データのバージョンを確認します。
「英辞郎辞書データVer98.」をお使いなら、以下のように、
--xxx=98
を指定して、python3 で init_eijiroXXX.py を実行します。

$ python3 ./init_eijiroXXX.py --xxx=98

すると、IASAP_ROOT/kit/ 以下に、eijiro98 directory が作成されるので移動します。

$ cd ../eijiro98

移動先の eijiro98 directory 以下に、一行テキスト形式の英辞郎辞書ファイルである、
eijiro98.txt をコピーします。

$ cp /tmp/eijiro98.txt .

Linux 環境では、 create_eijiro98_sqlite3.sh を以下のように実行します。
$ bash ./create_eijiro98_sqlite3.sh

Linux 環境では、 create_eijiro98_sqlite3.bat を以下のように実行します。
$ ./create_eijiro98_sqlite3.bat

IASAP_ROOT/kit/eijiro98 directory 以下に、
eijiro98.sqlite3 が作成されていれば、実行環境は整いました。

== 色々な mode
以下のようにして実行すると、tkinter mode で iasap が起動します。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=tkinter

以下のようにして実行すると、curses mode で iasap が起動します。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=curses

以下のようにして実行すると、command mode で iasap が起動します。
下の検索では、"arbitrary" の意味を調べています。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=one-shot arbitrary

--mode を指定しない場合、 tkinter mode で iasap が起動します。

== 前方一致検索・後方一致検索
下の検索では、"arbitrar" で後方一致検索をしています。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=one-shot "arbitrar "
検索語の最後が空白一つであることに注意してください。

下の検索では、"tly" で前方一致検索をしています。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=one-shot " tly"
検索語の先頭が空白一つであることに注意してください。

tkinter mode, curses mode でも同じように、検索語の前後に空白一つを入れ
ることで、前方一致検索・後方一致検索を実行することが出来ます。

== 例文検索
下の検索では、例文に "word" を含む例文を検索しています。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=one-shot "  word  "
検索語の前後に、連続する空白が2つずつ入っていることに注意してください。

下の検索では、例文の日本語訳に、"絶対に" を含む英文を検索しています。
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --mode=one-shot " 絶対に "
検索語の前後に、空白が1つずつ入っていることに注意してください。

tkinter mode, curses mode のどちらでも同じように、検索語の前後に空白を入れる
ことで、例文検索を実行することが出来ます。

== 詳しい使い方
$ python3 IASAP_ROOT/kit/eijiro98/eijiro98.py --help
help に書いています。。。参考にしてください。。。読んでください。。。
