# Blender スクリプトの入口

**対象**: Blender 5.0.1 / 内蔵 Python 3.11.13 / numpy 1.26.4
**前提**: `pip install` はしない。`tools/blender_*.py` は `bpy` と `numpy` のみに依存させる（[計画書 §7-4](../plan.md#s7-4)）。同梱の `mathutils` 等を使ってよいかは未決定（使いたくなったら [Notice.md](../../Notice.md) に出して相談する）。

## 0. まず動くことを確かめる

実行コマンド（Windows / PowerShell、リポジトリのルートで実行）：

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" --background --python tools\hello_bpy.py
```

実際に出た出力：

```
==================================================
Blender version : 5.0.1
Python version  : 3.11.13 (main, Sep 23 2025, 09:08:45) [MSC v.1929 64 bit (AMD64)]
numpy version   : 1.26.4
シーン内のオブジェクト: ['Camera', 'Cube', 'Light']
==================================================
```

計画書が前提にしている「Blender 5.0.1 / Python 3.11.13 / numpy 1.26.4」と完全に一致。

## 1. Scripting タブの使い方

- タブの場所：Blenderのウィンドウ上部のワークスペースタブ一覧の中に `Scripting` がある
- **Python Console**（左下）：1行ずつ打って即座に結果を見る場所。`import bpy` → `bpy.app.version_string` のように対話的に試すのに向く
- **Text Editor**（中央）：複数行のスクリプトを書いて `Run Script ▶` で一括実行する場所
- **`Run Script` の出力がどこに出るか** ← 詰まりやすい
  - Text Editor 上には出ない。`print()` の出力は **OSのコンソール（ターミナル）**に出る
  - Windows で GUI から Blender を起動した場合は `Window → Toggle System Console` でコンソールウィンドウを出す必要がある
    - **UIを日本語にしている場合**：`ウィンドウ → システムコンソールの切り替え`（メニューの英語/日本語表記が違うだけで同じ項目）
    - このメニュー項目は **Windows専用**。macOSには無いので、ターミナルから `blender` を起動して確認する
  - ターミナルから `blender`（GUI付きで起動）した場合は、その起動元のターミナルに出力される

## 2. CLI から実行する

- `--background`（略して `-b`）：GUIを開かずに実行する。20枚のレンダリングのような自動化はここが本命
- `--python <file>`：起動時に指定したPythonスクリプトを実行する
- 自分の環境（Windows）での blender 実行ファイルのフルパス：
  ```
  C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
  ```
- **フラグの短縮形に注意**：`--python <file>` の短縮形は **大文字の `-P`**。小文字の `-p` は別の意味（`--window-geometry`、ウィンドウ位置・サイズ指定）なので間違えると意図しない動作になる。`-python`（ハイフン1つ）という書き方は存在しない
  ```powershell
  blender -b -P tools\hello_bpy.py
  ```
- PowerShell / Git Bash から毎回フルパスを打つのは面倒なので、エイリアスや関数を用意すると楽：
  ```powershell
  # PowerShell プロファイルに追加
  function blender { & "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" @args }
  ```
  - **プロファイルに書いただけでは今開いているウィンドウには反映されない。** `. $PROFILE` で読み込み直すか、PowerShellを開き直す（プロファイルはPowerShell起動時に1回だけ読まれるため）
  - **初回は実行ポリシーでブロックされることがある**：`. $PROFILE` が `このシステムではスクリプトの実行が無効になっているため...` というエラーになったら、`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` を実行してから再試行する（Windows既定の `Restricted` はスクリプト実行を全面禁止しており、プロファイル `.ps1` もスクリプト扱いのため止められる）

## 3. よく使う bpy の入口（分かった範囲でよい）

| やりたいこと | 書き方 |
|---|---|
| シーンのオブジェクト一覧 | `bpy.data.objects` |
| カメラを取る | `bpy.data.objects["Camera"]` |
| 出力先を決める | `bpy.context.scene.render.filepath = "..."` |
| レンダリングする | `bpy.ops.render.render(write_still=True)` |
| 背景を透明にする | `bpy.context.scene.render.film_transparent = True` |

（`tools/hello_bpy.py` で動作確認済みなのは `bpy.app.version_string` と `bpy.data.objects` のみ。他はまだ未検証）

## 4. 詰まった点

- **アドオンのログがまじる**：`--background` 実行時、`Rokoko Studio Live for Blender` というアドオンが自動でロード／アンロードされ、`### Loading Rokoko Studio Live...` のようなログが自分の `print()` 出力の前後に混ざって出る。想定していなかった出力なので、初見だと自分のスクリプトが何かおかしいのかと勘違いしかける。実害はない（アドオンの標準出力なだけ）
- **パスにスペースが入る**：`C:\Program Files\Blender Foundation\Blender 5.0\blender.exe` はスペースを含むため、PowerShell では `&` 呼び出し演算子と `""` の両方が必要（`&`無しだとパス文字列がただのコマンドとして解釈されずエラーになる）
- **`--python`/`-P` は相対パスで通った**：リポジトリのルートで実行していれば `tools\hello_bpy.py` のような相対パスで問題なく見つかった
- **実際にルート以外で実行してハマった**：`blender` 関数（エイリアス）を作った直後、ホームディレクトリ（`C:\Users\<ユーザー名>`）にいたまま `blender -b -P tools\hello_bpy.py` を叩いたところ `OSError: Python file "C:\Users\<ユーザー名>\tools\hello_bpy.py" could not be opened` になった。**相対パスは「blenderのインストール場所」ではなく「PowerShellの現在地（カレントディレクトリ）」基準で解決される。** `cd` でリポジトリルート（`C:\4bitcom\recon3d`）に移動してから実行したら解消した

> GUIでの Method A（Python Console）・Method B（Text Editor で Run Script）は、実際に手元で1回ずつ触ってから、気づいた点をこの節に追記してください。特に「Run Script を押したのに何も起きない」体験は、実際に踏んでみないと実感が湧きません。
