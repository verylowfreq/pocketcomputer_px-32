# PocketComputer PX-32

ポケットコンピューター PX-32 は、「ポケコンをモダンに作ってみたらどうなるか？」という発想から生まれた、DIYポケコンです。

![Photo PX-32](https://github.com/user-attachments/assets/fa189b7b-1a0f-44e5-bae8-5556eb46d618)


技術同人誌『令和のポケコン製作記』にて詳細を紹介しています。（2025年11月 技術書典19 初出）

https://techbookfest.org/product/gQyMySu4Wg3ARh4vRMThmK?productVariantID=qDntKiaD1wEZSGtM00F8Fp

## おもな特徴

- メインMCU : M5Stack M5StampS3A (ESP32-S3)
- サブMCU : WCH CH32V203C8T6
- MicroPython
- 外部接続端子 : GPIO (8 pin), I2C, UART
- WiFi, BLE, ESP-NOWなど無線機能が利用可能
- 電源 : 単3型電池 2本 （充電池・乾電池）


## ファイル

- boot.py
    - 組み込み関数 print(), input() を上書きします。
- main.py
    - ポケコン起動時にテキストエディタを呼び出します。
- editor.py
    - テキストエディタアプリ本体です。
- files.py
    - 簡易ファイルブラウザ本体です。
- examples/
    - MicroPythonのサンプルプログラムです。
- submcu_ch32v203/
    - I/Oを担当するサブMCU CH32V203C8T6 のファームウェアです。
- PX-32 Schematic.pdf
    - 本機の回路図です。


## メインMCUのMicroPythonファームウェア

https://micropython.org/download/ESP32_GENERIC_S3/ を参照してください。


## License

MIT License (C) 2025 Mitsumine Suzu

