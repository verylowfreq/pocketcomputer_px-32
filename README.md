# PocketComputer PX-32

ポケットコンピューター PX-32 は、「ポケコンをモダンに作ってみたらどうなるか？」という発想から生まれた、DIYポケコンです。

技術同人誌『令和のポケコン製作記』にて詳細を紹介しています。（2025年11月 技術書典19 初出）

## ファイル

- boot.py
    - 組み込み関数 print(), input() を上書きします。
- main.py
    - ポケコン起動時にテキストエディタを呼び出します。
- editor.py
    - テキストエディタアプリ本体
- files.py
    - 簡易ファイルブラウザ本体
- examples/
    - MicroPythonのサンプルプログラム
- submcu_ch32v203/
    - I/Oを担当するサブMCU CH32V203C8T6 のファームウェアです。


## メインMCUのMicroPythonファームウェア

https://micropython.org/download/ESP32_GENERIC_S3/ を参照してください。
