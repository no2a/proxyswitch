# これは何か

アクセス先のホスト名に応じて経由するプロキシを切り替えるためのプロキシ

# 使い方

## 設定ファイル

ホスト名とプロキシの対応付けは設定ファイルで行う。
1行ごとにスペース区切りでホスト名とプロキシURLを書く。
ホスト名ifconfig.me,checkip.amazonaws.comにアクセスするときにそれぞれ用のプロキシを使う例。
```
ifconfig.me http://proxy-for-ifconfigme.example.com:3128
checkip.amazonaws.com http://proxy-for-checkipaws.example.com:3128
```

以下、設定ファイルについての諸々

```
# 行頭に#がある行はコメント
# 空行は無視される

# ホスト名を正規表現で指定するには一文字目を/にする
# 例) ifconfig.が先頭につくホスト名を指定する
/ifconfig\..* http://proxy-for-ifconfig-x.example.com:3128

# プロキシURLをDIRECTとするとプロキシを使わない
info.ddo.jp DIRECT
# 上に書いたものほど優先度が高い。従って、デフォルトのプロキシを指定するなら最終行に書く必要がある。
/.* http://proxy-default.example.com:8080

# どのホスト名とも一致しなかった場合はプロキシを使わずアクセスする。
# 最終行に /.* DIRECT と書くのと同じ。
```

## インストール

色々あるのであくまで例。

```
pipx install git+https://github.com/no2a/proxyswitch.git
```

## 実行

設定ファイルは--proxyswitch-configで指定。起動するとlocalhost:8899でlisten状態になる。

```
proxyswitch --port 8899 --plugin proxyswitch.Plugin --proxyswitch-config ~/.proxyswitch.conf
```

なお、本プログラムは[proxy.py](https://github.com/abhinavsingh/proxy.py)というプロキシサーバソフトのプラグインとして作られており、`proxyswitch -h`などでproxy.pyがもつ多数のオプションが表示され実際に使えるものもあるが、ここでは説明しない。必要ならproxy.py本体のドキュメントなどを参照すること。

## 確認

ifconfig.meではプロキシのIPアドレス、ifconfig.coでは自分のIPアドレスが表示される
```
curl --proxy http://localhost:8899 https://ifconfig.me
curl --proxy http://localhost:8899 https://ifconfig.co
```
