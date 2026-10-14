# QTD1 詳細設計

## 1. 文書概要

本書は、STM32U575CIT6を使用するQTD1ファームウェアおよび周辺回路の基本構成、ピン割り当て、通信インターフェースの排他制御方針を定義する。

### 1.1 対象機能

- 24-bit ADC（ADS127L11）
- SPI接続LCD（型番未定）
- 操作スイッチ
- 2-bit DIPスイッチによる通信インターフェース選択
  - RS-232C
  - RS-485
  - SPI LAN（WIZ850io）
  - MACアドレスEEPROM（25AA02E48想定）
  - IO-Link Device（L6364想定）
- 状態表示LED
- USB Device／DFU
- ST-LINKによるSWDデバッグ

### 1.2 前提

- MCUはSTM32U575CIT6（LQFP48）とする。
- MCUおよびデジタルI/O電圧は3.3 Vとする。
- ADS127L11のIOVDDは3.3 Vとする。
- U575基板のUSB-Cは電源供給およびUSB Device／DFUに使用する。
- SWDデバッグ用にPA13、PA14およびNRSTを予約する。
- LEDは既存回路どおりPA15を使用する。
- LCDの型番と詳細信号は未確定とし、本書では暫定予約のみ行う。

## 2. システム構成

```text
ADS127L11 ── SPI1 + DRDY ──┐
                            │
SPI LCD ─────── SPI3 ──────┤
                            │
DIPSW / 操作SW ─── GPIO ───┤ STM32U575CIT6
                            │
RS-232C ─┐                  │
RS-485 ──┤                  │
WIZ850io ┼─ 排他選択 ───────┤ USART3 / SPI2
IO-Link ─┘                  │
MAC EEPROM ── SPI2 ─────────┤（SPI LANモード時のみ）
                            │
USB-C ───── USB Device ─────┤
ST-LINK ─────── SWD ────────┘
```

## 3. ピン割り当て

### 3.1 ADS127L11

ADS127L11はQSPIではなく、SPI Mode 1（CPOL=0、CPHA=1）の4線SPIデバイスとして使用する。SPI1はADC専用とし、他デバイスとは共有しない。

| ADS127L11信号 | STM32U575 | MCU設定 | 備考 |
|---|---|---|---|
| CS | PA4 | GPIO Output | Active Low |
| SCLK | PA5 | SPI1_SCK | SPI Mode 1 |
| SDO | PA6 | SPI1_MISO | ADCからMCU |
| SDI | PA7 | SPI1_MOSI | MCUからADC |
| DRDY | PA0 | GPIO EXTI | Falling edge、DMA読出し開始要求 |
| START | PA1 | GPIO Output | 連続変換開始／同期制御 |
| RESET | PA2 | GPIO Output | Active Low |
| CLK | PA8 | MCO | 25.6 MHzをADS127L11へ供給 |

PA8からMCOで25.6 MHzを出力し、ADS127L11の外部クロックとして使用する。クロック精度はU575のHSEクロック源に依存する。要求ジッタを満たせない場合は、低ジッタ発振器をADS127L11へ直接供給する構成へ変更する。

### 3.2 LCD（暫定予約）

LCD型番決定後に確定する。現時点では一般的な4線SPI LCDを想定し、SPI3を予約する。

| LCD信号 | STM32U575 | MCU設定 | 備考 |
|---|---|---|---|
| SCK | PB3 | SPI3_SCK | PB3使用時はSWOトレースを使用不可 |
| MISO | PB4 | SPI3_MISO | LCDからの読出しが必要な場合のみ |
| MOSI | PB5 | SPI3_MOSI | 画像・コマンド送信 |
| CS | PB6 | GPIO Output | 暫定 |
| D/C | PB7 | GPIO Output | 暫定 |
| RESET | PB8 | GPIO Output | 暫定 |

LCDのTE、バックライトPWM、タッチパネル、SDカード等は型番決定後に追加検討する。

### 3.3 スイッチ入力

| 信号 | STM32U575 | MCU設定 | 備考 |
|---|---|---|---|
| 操作SW | 未確定 | GPIO Input / EXTI | LCD仕様確定後に割り当てる |
| DIP1 | PC13 | GPIO Input Pull-up | OFF=High、ON=Low |
| DIP2 | PB9 | GPIO Input Pull-up | OFF=High、ON=Low |

DIPスイッチはGNDへ接続する構成とし、MCU内部Pull-upを使用する。ノイズ耐性が必要な場合は外付け10 kΩ Pull-upおよび0.01～0.1 µFのコンデンサを追加する。

### 3.4 通信インターフェース排他グループ

USART3とSPI2の代替機能を利用し、RS-232C、RS-485、SPI LAN、IO-Linkを排他的に有効化する。IO-LinkはL6364をDevice側のPHYとして使用し、Multi-octet SPIモードで通信する前提とする。

| STM32U575 | RS-232C | RS-485 | WIZ850io | IO-Link L6364 |
|---|---|---|---|---|
| PB10 | USART3_TX | USART3_TX | SPI2_SCK（共通） | SPI2_SCK |
| PB11 | USART3_RX | USART3_RX | 未使用 | 未使用 |
| PB14 | 未使用 | USART3_DE | SPI2_MISO（共通） | SPI2_MISO |
| PB15 | 未使用 | 未使用 | SPI2_MOSI（共通） | SPI2_MOSI |
| PB12 | Transceiver制御候補 | Transceiver制御候補 | WIZ_CS | L6364_SS |
| PB13 | 未使用 | Transceiver制御候補 | WIZ_INT | L6364_INT |
| PA3 | Transceiver制御候補 | Transceiver制御候補 | WIZ_RST | L6364_CTLD（任意） |
| PA10 | High固定 | High固定 | MAC_EEPROM_CS | High固定 |

L6364の必要MCU信号数は、SPIの4本（SCK、MOSI、MISO、SS）とINTの合計5本である。DIOラインを直接制御するCTLDも使用する場合は合計6本となる。本設計では将来の拡張性を考慮してPA3へCTLDを割り当てる。

RS-232C／RS-485トランシーバ、WIZ850io、L6364を基板上へ同時実装する場合、非選択デバイスが信号線を駆動しないよう、Shutdown／Enable端子、電源スイッチまたは外付けバススイッチで電気的に切り離す。複数の出力端子を直接接続しない。

### 3.5 予約ピン

| STM32U575 | 用途 |
|---|---|
| PA9 | USB VBUS検出を使用する場合に予約 |
| PA10 | MACアドレスEEPROM CS（Active Low） |
| PA11 | USB DM |
| PA12 | USB DP |
| PA13 | SWDIO |
| PA14 | SWCLK |
| PA15 | LED |
| NRST | ST-LINKリセット |
| PH0 / PH1 | HSE発振子 |
| PC14 / PC15 | LSE使用時に予約 |
| PH3 | BOOT0 |

## 4. DIPスイッチによるモード選択

### 4.1 モード表

スイッチの物理表示を基準として、以下の通信モードを選択する。

| DIP1 | DIP2 | GPIO読値 PC13/PB9 | 選択モード |
|---|---|---|---|
| OFF | OFF | High / High | RS-232C |
| OFF | ON | High / Low | RS-485 |
| ON | OFF | Low / High | SPI LAN |
| ON | ON | Low / Low | IO-Link Device |

### 4.2 読取りタイミング

- DIPSWは電源投入またはリセット後に読み取る。
- GPIO初期化後、10 ms以上待って2回読み取り、値が一致した場合に確定する。
- 運用中のDIPSW変更は反映しない。設定変更後はリセットを必要とする。
- DIPSWが不安定または読取り不一致の場合はUSART3、SPI2および各トランシーバを無効状態にする。

### 4.3 切替シーケンス

1. PB10～PB15およびPA3を安全なGPIO入力状態で初期化する。
2. DIP1／DIP2を読み取って通信モードを確定する。
3. 非選択トランシーバ、WIZ850io、L6364をShutdown、Resetまたは電源OFF状態にする。
4. 選択モードに必要なGPIO出力レベルを先に設定する。
5. 対象ピンのAlternate Functionを設定する。
6. USART3またはSPI2を初期化する。
7. 選択デバイスのShutdown／Resetを解除する。

## 5. ADS127L11サンプリング設計

### 5.1 サンプリング仕様

| 項目 | 設定 |
|---|---|
| 目標出力データレート | 40 kSPS |
| ADCクロック源 | STM32U575 PA8 MCO外部クロック |
| SPEED_MODE | High-speed mode |
| ADC入力クロック | 25.6 MHz |
| U575 SYSCLK | 128 MHz |
| MCO設定 | SYSCLK / 5 |
| デジタルフィルタ | sinc4 + sinc1 |
| sinc4 OSR | 32 |
| sinc1 OSR | 10 |
| SPIモード | Mode 1（CPOL=0、CPHA=1） |
| 変換方式 | 連続変換 |
| データ取得通知 | DRDY Falling-edge EXTI |
| データ転送 | SPI1 RX/TX DMA推奨 |

ADS127L11では変調クロックが入力クロックの1/2となるため、出力データレートは次式となる。

```text
fDATA = 25.6 MHz / 2 / (32 × 10) = 40 kSPS
```

U575の40 kHzタイマで変換開始パルスを生成する方式ではなく、PA8から25.6 MHzを連続供給し、ADS127L11が40 kSPSで連続変換する。

### 5.2 データ取得フロー

1. U575がADS127L11をRESETする。
2. PA8 MCOの25.6 MHz出力が安定したことを確認する。
3. SPI1でHigh-speed mode、外部クロック、sinc4+sinc1フィルタ、OSRを設定する。
4. STARTを有効にして連続変換を開始する。
5. ADS127L11が変換データごとにDRDYをLowへ遷移させる。
6. PA0のEXTI割り込みでは、SPI1 DMA転送の開始要求のみを行う。
7. DMA完了割り込みで24-bitデータを符号拡張し、リングバッファへ格納する。
8. 信号処理、表示および通信処理はリングバッファからデータを取得する。

40 kSPSの周期は25 µsである。割り込み内で演算やLCD更新を行わず、SPI DMAとバッファリングを使用する。

### 5.3 クロック精度に関する制約

ADCクロックはU575のSYSCLKをPA8 MCOから分周出力する。現在想定する20 MHz HSEを基準に、PLL1をM=5、N=64、R=2として128 MHzを生成し、MCOを5分周して25.6 MHzを得る。PLL入力・VCO範囲とFlashレイテンシはSTM32CubeMXで最終検証する。

```text
HSE 20 MHz → PLL1 → SYSCLK 128 MHz → MCO / 5 → 25.6 MHz
```

40 kSPSの絶対精度はHSE発振子の初期偏差、温度特性、経年変化およびPLL/MCOジッタに依存する。「正確な40 kHz」の許容誤差をppm単位で決定し、HSEの仕様が満たすことを確認する。満たせない場合はTCXO等の高精度・低ジッタ発振器をADS127L11へ直接接続する。

SYSCLKを従来の160 MHzから128 MHzへ変更するため、SysTick、UART、SPI、USBおよび各タイマのクロック設定を再生成・再確認する。USB用48 MHzクロックはHSI48または専用PLL出力から生成し、MCO設定の影響を受けない構成とする。

## 6. 通信モード仕様

### 6.1 RS-232Cモード

- USART3をPB10 TX、PB11 RXで使用する。
- RS-232Cトランシーバのみ有効化する。
- RS-485トランシーバとWIZ850ioはShutdown／Reset状態にする。
- ボーレート等の通信条件は上位仕様で決定する。

### 6.2 RS-485モード

- USART3をPB10 TX、PB11 RXで使用する。
- PB14のUSART3_DE機能を使用し、送受信方向をハードウェア制御する。
- RS-485トランシーバのみ有効化する。
- 終端抵抗およびバイアス抵抗の実装有無は基板仕様で決定する。

### 6.3 SPI LANモード

- WIZ850ioをSPI2で使用する。
- WIZ850ioとMACアドレスEEPROMでSPI2のSCK、MOSI、MISOを共有する。
- WIZ850ioはSPI Mode 0およびホスト制御CSによるVariable Length Data Modeを使用する。
- PB12をWIZ850io用CS、PA10をMACアドレスEEPROM用CSとして個別に制御する。
- 両CSには外付けPull-upを設け、リセット中およびGPIO初期化前に両デバイスが非選択となるようにする。
- PB13のWIZ_INTはFalling-edge EXTIとして使用する。
- PA3のWIZ_RSTはActive Lowとし、500 µs以上Lowを保持する。
- RS-232CおよびRS-485トランシーバをShutdown状態にする。

#### 6.3.1 MACアドレスEEPROM

- EEPROMはMicrochip 25AA02E48を想定する。
- 25AA02E48は出荷時に書き込まれた一意なEUI-48を持つ。
- EUI-48の6 byteはEEPROMアドレス0xFA～0xFFから読み出す。
- EEPROMはSPI Mode 0,0を使用し、WIZ850ioとSPIモードを共通化する。
- EEPROMを3.3 Vで使用する場合の最大SCKは5 MHzのため、MAC読出し時のSPI2は5 MHz以下とする（10 MHzは4.5 V以上の場合のみ）。
- MAC読出し完了後、SPI2を停止してWIZ850io用周波数へ再設定する。
- EEPROMへの書込み命令、Write Enable命令およびStatus Register書込み命令はFWから使用しない。
- 8-pin品を使用する場合、WPおよびHOLDは適切にPull-upして非アクティブに固定する。

#### 6.3.2 SPI LAN起動シーケンス

1. PA10のMAC_EEPROM_CSとPB12のWIZ_CSをHighにした状態でGPIOを初期化する。
2. PA3のWIZ_RSTをLowにしてWIZ850ioをリセット状態に保持する。
3. SPI2をMode 0、5 MHz以下で初期化する。
4. WIZ_CSがHighであることを確認する。
5. MAC_EEPROM_CSだけをLowにし、READ命令で0xFA～0xFFの6 byteを連続読出しする。
6. MAC_EEPROM_CSをHighに戻す。
7. MACアドレスを検証する。
8. SPI2を停止し、WIZ850io用のSPI周波数で再初期化する。
9. WIZ_RSTを500 µs以上Lowに保持した後Highへ戻す。
10. WIZ850ioを初期化し、EEPROMから読んだMACアドレスを設定する。
11. WIZ850ioのネットワーク動作を開始する。

MACアドレスは、全byteが0x00または0xFFでないこと、および先頭byteのI/G bitが0（ユニキャスト）であることを確認する。25AA02E48を使用する場合はMicrochip OUI `00-04-A3`も診断情報として確認できる。読出しまたは検証に失敗した場合は重複MACによるネットワーク障害を避けるためLANを開始せず、エラー状態とする。固定の共通MACアドレスへフォールバックしない。

#### 6.3.3 TCPソケット構成

W5500のハードウェアソケットを2個使用する。TCP Serverを主用途とし、TCP ClientはEFMSRからポーティングした既存機能を維持する。

| W5500 Socket | 用途 | 同時セッション数 | 備考 |
|---|---|---:|---|
| Socket 0 | TCP Server | 1 | QTD1の主通信。コマンド受信と応答 |
| Socket 1 | TCP Client | 1 | EFMSR由来の既存Client機能 |
| Socket 2～7 | 未使用 | 0 | 将来予約。バッファサイズ0に設定 |

W5500の送受信メモリは、初期値としてSocket 0とSocket 1へTX 8 KiB、RX 8 KiBずつ割り当てる。W5500のTXメモリ合計16 KiB、RXメモリ合計16 KiBを2ソケットで使用する。実測した通信量に応じてServer側を優先する場合は再配分する。

#### 6.3.4 TCP Server仕様

- Socket 0を使用する。
- Serverの待受Port番号は設定値とし、初期値は別途決定する。
- 同時接続は1セッションだけ許可する。
- Socket 0がESTABLISHEDの間は追加接続を受け付けない。
- W5500ではBSD Socketの独立したaccept処理ではなく、LISTENからESTABLISHEDへの状態遷移を接続成立として扱う。
- 接続中のクライアントが切断されるまで、別クライアント用のServerソケットは生成しない。
- クライアント切断、通信タイムアウトまたは異常発生後はSocket 0をCLOSEし、再度OPEN、LISTENして次の接続を待つ。
- Session開始要求を受信した後にアプリケーションセッションを開始する。
- Session未成立状態では、許可されたSession制御コマンド以外を実行しない。
- 1つの受信TCPセグメントが1コマンドと一致することを前提にしない。
- 分割受信と複数コマンドの結合受信に対応するため、受信リングバッファ上でコマンドフレームを組み立てる。
- 応答送信がW5500の空きTXサイズを超える場合は分割して送信する。
- 最大コマンド長、フレーム形式、無通信タイムアウトおよびSession終了コマンドは通信プロトコル仕様で決定する。

TCP Serverの基本状態遷移を以下に示す。

```text
CLOSED
  ↓ socket(Socket 0, TCP, port)
INIT
  ↓ listen()
LISTEN
  ↓ Sn_SR == ESTABLISHED
CONNECTED
  ↓ Session要求受信
SESSION
  ↓ コマンド受信／応答
SESSION
  ↓ Session終了、切断、タイムアウトまたは異常
CLOSE
  ↓ close()
CLOSED → INIT → LISTEN
```

#### 6.3.5 TCP Client仕様

- Socket 1を使用する。
- EFMSRからポーティングしたTCP Client処理を基本的に維持する。
- STM32U575のSPI2、GPIO、TickおよびW5500初期化部だけをQTD1のハードウェア層へ置き換える。
- TCP ServerとTCP Clientは独立した状態機械として処理する。
- Client機能を使用しない設定でもSocket 1の状態をCLOSEDに保ち、Socket 0のServer動作へ影響させない。

#### 6.3.6 W5500ソフトウェア構成

EFMSR由来の以下のソースをポーティング元として使用し、既存Client処理を残したままServer処理を追加する。

| ファイル | 役割 |
|---|---|
| W5500.c / W5500.h | W5500レジスタおよびSPIアクセス |
| wizchip_conf.c / wizchip_conf.h | WIZchipコールバック、メモリ、ネットワーク設定 |
| socket.c / socket.h | W5500ハードウェアソケットAPI |
| net.c / net.h | MAC、IP、Gateway、Subnet等のネットワーク管理 |
| tcp.c / tcp.h | TCP Clientおよび新規TCP Server状態機械 |

W5500ドライバ層へSTM32 HALを直接分散させず、SPI2送受信、WIZ_CS、WIZ_RST、割り込み禁止、Tick取得をQTD1用ハードウェア抽象化関数へ集約する。TCP Server追加時も既存Client APIの動作を変更しない。

### 6.4 IO-Link Deviceモード

- L6364をIO-Link Device側PHYとして使用する。
- SPI2を使用し、PB12をSlave Selectとする。CPOL、CPHAおよび最大SCKは採用するL6364リビジョンのSPIタイミング仕様に合わせて確定する。
- PB13のL6364_INTをEXTI入力として使用する。
- PA3のL6364_CTLDは必要な場合のみ使用する。
- 基本方式はMulti-octet SPIモードとし、IO-LinkデータをSPI経由で交換する。
- Transparentモードへ変更する場合はUART TX/RXが追加で必要となるため、本ピン配置を再検討する。
- RS-232C、RS-485トランシーバおよびWIZ850ioを無効状態にする。
- L6364はDevice用であり、QTD1をIO-Link Masterとして使用する場合には適用しない。

## 7. 初期化順序

1. HAL、HSE、PLLおよび128 MHzシステムクロック初期化
2. PA8 MCO 25.6 MHz出力開始
3. 安全状態用GPIO初期化
4. ICACHE初期化
5. DIPSW読取りと通信モード確定
6. SPI1、DMA、EXTI初期化
7. ADS127L11初期化および連続変換開始
8. LCD初期化（型番確定後）
9. SPI LANモードの場合、MAC EEPROM読出し後にWIZ850ioを初期化
10. その他の場合、選択された通信インターフェースのみ初期化
11. メイン処理開始

## 8. 未確定事項

- LCD型番、解像度、SPI最大周波数、追加信号
- 操作スイッチ数と割り当て
- RS-232C／RS-485トランシーバ型番およびEnable極性
- 各通信モードのボーレート、フレーム形式、プロトコル
- WIZ850ioのネットワーク設定方式
- TCP Serverの待受Port番号
- TCPコマンドのフレーム形式、最大長、Session要求／終了コマンド
- TCP Serverの無通信タイムアウト
- TCP Client機能の起動条件、接続先IPおよびPort番号
- MACアドレスEEPROMの正式型番およびパッケージ
- WIZ850io運用時のSPI2クロック周波数
- ADS127L11の入力レンジ、基準電圧、バッファ設定、CRC使用有無
- ADC測定対象がDC主体かAC主体か
- ADCクロック精度およびジッタの要求値（ppm）
- HSE発振子の周波数許容差、温度特性および経年変化
- IO-LinkでQTD1をDevice側として使用することの確認
- IO-Link PHYをL6364とすることの確認
- L6364のCTLD使用有無およびMulti-octetモードの適合確認

## 9. 参照資料

- STMicroelectronics, STM32U575xx Datasheet, DS13737
  - https://www.st.com/resource/en/datasheet/stm32u575ci.pdf
- Texas Instruments, ADS127L11 Datasheet, SBAS946
  - https://www.ti.com/lit/ds/symlink/ads127l11.pdf
- WIZnet, WIZ850io Product Information
  - https://wiznet.io/products/ethernet-modules/wiz850io
- Microchip, 25AA02E48/25AA02E64 Datasheet
  - https://ww1.microchip.com/downloads/en/DeviceDoc/25AA02E48-25AA02E64-2K-SPI-Bus-Serial-EEPROM-Data%20Sheet_DS20002123G.pdf
- STMicroelectronics, L6364 Datasheet
  - https://www.st.com/resource/en/datasheet/l6364.pdf
- STMicroelectronics, STM32U5 Reference Manual, RM0456
  - https://www.st.com/resource/en/reference_manual/rm0456-stm32u5-series-armbased-32bit-mcus-stmicroelectronics.pdf
