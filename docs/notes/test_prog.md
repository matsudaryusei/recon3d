# Pythonでのテスト用プログラムの作成 2026/9/4

Pythonでテスト用のプログラム開発時に
```python
import re
```
という**正規表現モジュール**と
```python
from pathlib import Path
```
ファイル・ディレクトリ(フォルダ)のパスをオブジェクトとして操作・処理ができるモジュールを利用

Pathを記述するうえで**raw文字列**を知っている必要がある。

## raw文字列

C言語やPythonでは通常```\n```で改行を行うが、これは```\```が特殊な意味を持つためである。しかし、正規表現では```\s```や```\.```など```\```を多用するため、これを文字列として使用すると問題が起こる。

そのため
```python
FORBIDDEN_PATTERNS = [
    re.compile(r"diag\(\s*\[?1(\.0)?\s*,\s*-1(\.0)?\s*,\s*-1(\.0)?"), # diag(1,-1,-1)などのnumpyの対角行列を作る関数の正規表現
    # 略
]
```
のように`r"..."`と記述する必要がある。

## re.compile(...)

上記の`FORBIDDEN_PATTERNS`にもある`re.compile(パターン文字列)`は、そのパターンをあらかじめ**正規表現オブジェクト**に変換する関数である。

つまりやっていることは
```python
pattern_str = r"diag\(\s*\[?1(\.0)?\s*,\s*-1(\.0)?\s*,\s*-1(\.0)?"  # ただのraw文字列
pattern = re.compile(pattern_str)  # 検索に使える正規表現オブジェクトに変換
```
このように制作したオブジェクト```pattern```を以下のように使える。
```python
pattern.search(text)   # text の中に正規表現patternがあるか探す
```

## assertとは

Pythonの**組み込みの文**。「ここでこの条件が成り立っているはず」という前提条件を宣言し、崩れていたら即座に失敗させるためのもの。

```python
assert 条件
assert 条件, メッセージ
```

- 条件が`True`なら何も起きず、次の行へそのまま進む。
- 条件が`False`なら**その場で`AssertionError`を発生させて処理を止める**（メッセージを指定していれば、それも一緒に表示される）。

pytestはテスト関数内の普通の`assert`文を特別扱いする（assertion rewriting）。`assert 実際の値 == 期待値`と書いておくだけで、失敗時に

```
E       assert 1080 == 1079
```

のように**実際の値と期待値の両方を自動で表示する**。だから特別な比較関数を使わなくても、素の`assert`を書くだけで十分なテストになる。

コード内での実例：
- `assert len(py_files) > 0, "走査対象が0件（パスが間違っている可能性）"` → 条件が崩れたら指定したメッセージ付きで失敗
- `assert blender_v_to_opencv_v(0, H) == H - 1` → 期待値と一致しなければpytestが自動で両辺の値を表示して失敗
- `assert np.isclose(np.linalg.det(R_cv), 1.0)` → `np.isclose`が返す`True`/`False`をそのまま検査

**`pytest.fail()`との違い**：`assert`は「条件式が1つあり、それをそのまま検査する」形なのに対し、`pytest.fail(メッセージ)`は**ループの途中など、条件式だけでは表現しづらい場所で明示的に失敗させたいとき**に使う（`test_no_stray_coordinate_conversion`内で使用）。

## テスト用プログラムの関数について

`def test_no_stray_coordinate_conversion():`などpytestは関数名が`test_`で始まるものを自動的にテスト用の関数として実行する。

### def test_no_stray_coordinate_conversion(): について

この関数について一行ずつ解説していく

```python
    src_dir = Path(__file__).resolve().parents[1] / "src"
```

- `__file__`は今実行されているファイルのパスが入っている特殊変数である。つまり`Path(__file__)`は今実行されているファイルのパスをオブジェクトに変換する操作を行っている。
- `.resolve()`で相対パスから絶対パスへの変更を行い、`../`など表現のあいまいさを無くす。
- `.parents[]`で親ディレクトリを遡ることができ`.parents[0]`で1つ上の階層である`tests`へ、`.parents[1]`で2つ上のリポジトリ直下までさかのぼることができる。

以上を踏まえると`.../recon3d/src`という絶対パスを入手していることが分かる。

もしそのまま`Path("src")`と書いてしまう場合「pytestを実行した場所」からの相対パスとなってしまう。この場合、リポジトリ直下以外から`pytest`を実行すると、`src_dir`が見つからず走査対象が0件になる。**しかもこれはエラーにならず、単に何も検出されないまま静かにpassしてしまう**（＝規約違反を永久に見逃す、一番たちの悪い壊れ方）。絶対パスでの記述にすることでこれを防ぐことができる。

```python
    coords_file = src_dir / "recon3d" / "io" / "coords.py"
```

これは「座標変換を書いていい場所」のパスを組み立てている。

```python
    py_files = list(src_dir.rglob("*.py"))
```

- `rglob("*.py")`で`src_dir`配下をサブフォルダも含めて再帰的に検索し、`.py`ファイルを全部見つける。この時、`rglob`ではなく`glob`だと直下の階層だけを探索するため注意する必要がある。
- 戻り値がイテレータであるため`list()`でリスト化をして複数回の走査を可能にしている。

**ここでイテレータという訳の分からない概念が登場したので調べた範囲で解説(表の内容を抑えていればOK)**

そもそもfor文は裏でこのような処理をしている(`for x in something:`と書いた場合)

```python
it = iter(something)   # 1. something から「イテレータ」を取り出す
while True:
    try:
        x = next(it)    # 2. イテレータに「次の値ちょうだい」と聞く
    except StopIteration:
        break            # 3. 「もう無いよ」と言われたら終了
    # ここでforの中身が実行される
```

つまり`for`は毎回イテレータに対して`next()`を呼んで1個ずつ受け取っているだけである。実際にリストからイテレータを作ると以下のようになる。

```python
>>> numbers = [10, 20, 30]        # これは「リスト」
>>> it = iter(numbers)             # リストから「イテレータ」を作る
>>> it
<list_iterator object at 0x...>    # ← リストとは別物の「イテレータ」という型
>>> next(it)
10
>>> next(it)
20
>>> next(it)
30
>>> next(it)
Traceback (most recent call last):
StopIteration                      # ← もう無いので例外が飛ぶ
```

この結果からも`next(it)`を呼ぶたびに次の値が出てきていることが分かる。また、使い切ると`StopIteration`という例外処理が出てきているため`for`文はこの`StopIteration`をキャッチすることでループを終了させていることが分かる。

リストとイテレータの違いは次のようになっている。

```python
>>> numbers = [10, 20, 30]
>>> numbers[0]          # リストはインデックスで何度でもアクセスできる
10
>>> numbers[0]           # 何度呼んでも同じ結果
10
>>> len(numbers)
3
```

```python
>>> it = iter([10, 20, 30])
>>> next(it)
10
>>> next(it)
20
>>> list(it)             # 残りをlist()でまとめて取り出す
[30]
>>> list(it)             # ← もう空！一度取り出した値は消える
[]
```

ここで重要なのは**イテレータは一回きりの使い捨て**ということであり、今どこまで進んだかという位置情報だけを内部に持っていて、前に戻れないという性質があると分かる。

`rglob()`で確認すると

```python
>>> from pathlib import Path
>>> it = Path("src").rglob("*.py")
>>> it
<generator object Path.rglob at 0x...>   # イテレータの一種（generator）
>>> len(it)
Traceback (most recent call last):
TypeError: object of type 'generator' has no len()   # ← len()できない
>>> py_files = list(it)     # 全部取り出してリストに変換
>>> len(py_files)            # リストになったので len() が使える
5
```

`rglob()`は「ファイルシステムを探しながら、見つかるたびに1個ずつ返す」という動き方をするため、戻り値がイテレータ（正確にはジェネレータだけど流石にこれ以上調べるのはキツい）になっている。

これを`list()`で包むことで、「もう全部探し終わった状態のリスト」に変換し`len()`やインデックスアクセスができるようにしている。

まとめ

| | リスト | イテレータ |
|---|---|---|
| 中身 | 全要素が最初から確定している | 「次は？」と聞かれたら1個返す仕組みだけ持つ |
| `len()` | できる | できない |
| `numbers[0]` | できる | できない |
| 何度も使える | できる | **一度使い切ると空になる** |
| `for`で回す | できる | できる |

話を戻すと、この行で`src/`以下にあるすべての`.py`ファイルのパス一覧を取得していることが分かる。

```python
    assert len(py_files) > 0, "走査対象が0件（パスが間違っている可能性）"
```

- `assert 条件, メッセージ`で条件が`False`ならその場でテストが失敗して、メッセージが表示される。
- ここでのチェックは、`py_files`が0件のとき「検出が正しく機能して0件だった」のか「単に`src_dir`のパスが間違っていて何も見つかっていないだけ」なのかを区別できないことへの対策。**0件なら無条件に異常とみなして落とす**ことで、上記の「空振りしたまま静かにpassする」危険を防いでいる。

```python
    for path in py_files:
        if path == coords_file:
            continue
```
1つずつファイルを確認し`coords_file`という許可された場所なら`continue`でスキップ。

```python
        text = path.read_text(encoding="utf-8")
```
ファイルの中身をすべて文字列として読み込み、文字コードの違いによる読み込みエラーを防ぐ。

```python
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                pytest.fail(f"{path}: 座標変換は io/coords.py に書くこと")
```
前述した禁止パターンを1つずつあるか確かめる。`pattern.search(text)`はパターンが部分的に一致していたら真(`Match`)、見つからないなら偽(None)を返すため、見つかった場合は`pytest.fail(メッセージ)`で即座にテスト失敗として終了させ、どのファイルで違反したのかを表示する。

### def test_identity_rotation() について

**「テストを先に書く」ため、まだ`coords.py`の実装は無い状態でこのテストを書く。** 目的は「何ができたら正しいか」を先に固定すること。実装より先にテストがある間は、`ImportError`や失敗で落ちるのが正常。

pytestのテスト関数は基本的に**Arrange（準備）→ Act（実行）→ Assert（確認）**の3段構成で書くらしい。

```python
def test_identity_rotation():
    # Arrange：入力を用意する
    R_blender = np.eye(3)
    t_blender = np.array([0.0, 0.0, 5.0])

    # Act：テストしたい関数を呼ぶ
    R_cv, t_cv = blender_to_opencv_rt(R_blender, t_blender)

    # Assert：紙で出した期待値と一致するか確認する
    expected_R_cv = np.array([[1.0, 0.0, 0.0],
                              [0.0, -1.0, 0.0],
                              [0.0, 0.0, -1.0]])
    expected_t_cv = np.array([0.0, 0.0, -5.0])

    np.testing.assert_allclose(R_cv, expected_R_cv)
    np.testing.assert_allclose(t_cv, expected_t_cv)
```

- `np.testing.assert_allclose(実際の値, 期待値)`は浮動小数点の配列同士を比較する専用関数。`==`だと誤差で失敗することがあるため使う。一致していれば何も起きず、違えば差分付きで失敗する。

**期待値の手計算**(どうせ分かると思うし読み飛ばしても可)

`docs/conventions.md`にある変換式を使う。

```
C = diag(1, -1, -1)
R_cv = C @ R_blender
t_cv = C @ t_blender
```

- `R_blender`は単位行列(`np.eye(3)`)。単位行列を掛けても相手は変わらない（`C @ I = C`）ので、`R_cv`はそのまま`C = diag(1, -1, -1)`、つまり`[[1,0,0],[0,-1,0],[0,0,-1]]`になる。
- `t_cv = C @ t_blender`は対角行列とベクトルの積なので、**各成分にその対角成分を1つずつ掛けるだけ**でよい。`t_blender = [0, 0, 5]`に`C`の対角成分`(1, -1, -1)`を順に掛けると`t_cv = [0, 0, -5]`。

### def test_rotation_is_orthogonal() について

`test_identity_rotation`で出した`R_cv`が**壊れていない回転行列であるか**を確認するテスト。座標変換の符号ミスは、値そのものより**回転行列としての性質が崩れる**形で現れることが多いので、ここを別立てで確認する。

```python
def test_rotation_is_orthogonal():
    R_blender = np.eye(3)
    t_blender = np.array([0.0, 0.0, 5.0])
    R_cv, t_cv = blender_to_opencv_rt(R_blender, t_blender)

    np.testing.assert_allclose(R_cv.T @ R_cv, np.eye(3), atol=1e-10)
    assert np.isclose(np.linalg.det(R_cv), 1.0)
```

確認しているのは2つの性質

1. **直交行列であること**：`R_cv.T @ R_cv`が単位行列`I`に戻るかどうか
2. **鏡映になっていないこと**：`np.linalg.det(R_cv)`（行列式）が`+1`かどうか。`-1`だと鏡像になっている合図。

補足
- `atol=1e-10`は`assert_allclose`の**絶対許容誤差**。浮動小数点演算では誤差が出るため、完全に`0`でなくてもごく小さければ許容する。
- `np.isclose(a, b)`はスカラー同士を誤差込みで比較し`True`/`False`を返すだけの関数なので、`assert_allclose`と違い自分で`assert`を付ける必要がある。
- 直交行列の確認だけでは不十分（壊れた行列でも`det`だけ偶然`+1`になりうる）なので、`R.T @ R ≈ I`と`det(R) ≈ +1`の**両方**を確認して初めて「正しい回転行列」と言える。

### def test_v_edges() について

画像の縦方向（v座標）の反転が、**端から端まで正しく対応しているか**を確認するテスト。

```python
def test_v_edges():
    H = 1080 # サンプル値 
    assert blender_v_to_opencv_v(0, H) == H - 1
    assert blender_v_to_opencv_v(H - 1, H) == 0
```

`docs/conventions.md`の変換式`v_cv = H - 1 - v_blender`を使って手計算する：

- `v_blender = 0`（Blender側で一番下の行）→ `v_cv = H - 1 - 0 = H - 1`（OpenCV側で一番上から数えて最後の行、つまり一番下）
- `v_blender = H - 1`（Blender側で一番上の行）→ `v_cv = H - 1 - (H - 1) = 0`（OpenCV側で一番上の行）

つまり「Blenderの一番下 → OpenCVの一番下」「Blenderの一番上 → OpenCVの一番上」に正しく対応しているかを、**両端**で確認している。中間の値だけ確認して端を見落とすと、off-by-one（`-1`の付け忘れなど）のミスに気づけないため、あえて境界値（0と`H-1`）をテストしている。

## テスト3：壊れた cameras.json を読んだら例外が出ること

正常な`cameras.json`を1つ作り（`valid_camera_dict()`）、それを**1か所だけ壊した**バージョンを`load_cameras()`に読ませて、期待通り例外が出るかを確認する。

```python
import json
from recon3d.io.cameras import load_cameras
```

### valid_camera_dict() について

`docs/plan.md`§5-1のJSON実例をそのままPythonの辞書として書き起こしたもの。これを土台にして、各テストで1か所だけ書き換えて壊す。

```python
def valid_camera_dict():
    return {
        "schema_version": "1.0",
        "convention": {...},
        "image_size": {...},
        "intrinsics": {...},
        "views": [{...}],
        "meta": {...},
    }
```

### def test_load_valid_cameras() について

正常なデータなら例外を投げずに読み込めることを確認する（異常系のテストの前提として、まず正常系が通ることを確認しておく）。

```python
def test_load_valid_cameras(tmp_path):
    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(valid_camera_dict()))
    cameras = load_cameras(path)
    assert cameras.schema_version == "1.0"
```

- `tmp_path`：引数名に書くだけでpytestが自動的に渡してくれる「テスト専用の一時フォルダ」のフィクスチャ。テスト終了後は自動で消える。
- `json.dumps(dict)`：Pythonの辞書をJSON形式の文字列に変換する。
- `path.write_text(...)`：その文字列をファイルに書き込む。

### with文とは（Claude作一般的な説明）

`with`文は、「**ブロックに入る前の準備**」と「**ブロックを抜けるときの後片付け**」を**自動でセットにして実行する**ための構文。

`with`を使わない場合（ファイルを開く例）：

```python
f = open("data.txt")
data = f.read()
f.close()          # ← 開いたら必ず閉じないといけない。書き忘れ/エラーで飛ばされるリスクがある
```

`with`を使う場合：

```python
with open("data.txt") as f:
    data = f.read()
# ← ここでブロックを抜けた瞬間、自動で f.close() が呼ばれる
```

`open("data.txt")`が「準備（ファイルを開く）」を行い、ブロックを抜けるときに**自動で**「後片付け（ファイルを閉じる）」を行ってくれる。**途中でエラーが起きてブロックを抜けた場合でも、後片付けは必ず実行される**のが`with`を使う一番の理由。

**構文の読み方**

```python
with 何か as 変数名:
    ここがブロック（インデントされた範囲）
```

- `with`の右側（`何か`）が「準備・後片付けの仕組みを持ったもの」であること
- `as 変数名`は省略可能（`何か`が返すものを使いたいときだけ書く）
- インデントされている間が「保護された範囲」で、抜けると自動で後片付けが走る

### with文が裏で呼んでいるもの（`__enter__`・`__exit__`）

`with`で使える対象（コンテキストマネージャ）は、**`__enter__`と`__exit__`という2つの特別なメソッドを持ったオブジェクト**。

```python
with X() as v:
    ブロックの中身
```

は、裏側ではおおよそこう動いている。

```python
mgr = X()
v = mgr.__enter__()          # 1. 準備。戻り値がasの変数に入る
try:
    ブロックの中身
except BaseException as e:
    # 2. ブロック内で例外が起きた場合、__exit__にその例外情報を渡す
    handled = mgr.__exit__(type(e), e, e.__traceback__)
    if not handled:
        raise                # __exit__が「処理した」と言わなければ、例外はそのまま外に飛ぶ
else:
    # 3. 例外が起きなかった場合も、必ず__exit__が呼ばれる
    mgr.__exit__(None, None, None)
```

ポイントは、**`__exit__`は「ブロックの中で何が起きたか（例外の型・中身）」を必ず知らされる**こと。そして`__exit__`は「その例外を自分で処理済みにするか（`True`を返す）」「素通しして外に伝播させるか（`False`を返す）」を自分で決められる。

`open()`の場合の`__exit__`は、例外の中身を見ずにただファイルを閉じるだけ（`False`相当・例外はそのまま外へ）だった。

### pytest.raises の `__exit__` が具体的にやっていること

`pytest.raises(ValueError)`は、この`__exit__`を使って**例外の型を検査する**という特殊な動きをする。

```python
with pytest.raises(ValueError):
    load_cameras(path)
```

- **ブロック内で例外が起きなかった場合**（`__exit__`が`exc_type=None`で呼ばれる）→「例外が出るはずなのに出なかった」と判断し、**自分から`pytest.fail("DID NOT RAISE ValueError")`を呼んでテストを失敗させる**
- **ブロック内で`ValueError`（かそのサブクラス）が起きた場合**→「期待通りだ」と判断し、`__exit__`が`True`を返してその例外を**回収（握りつぶす）**。例外は外に伝播せず、`with`ブロックの後（このテストでは関数の終わり）にそのまま進み、**テストは成功**になる
- **ブロック内で違う型の例外（例：`TypeError`）が起きた場合**→`__exit__`は「期待と違う」と判断し`False`を返す→その例外はそのまま外に伝播→**テストはその予期しない例外で失敗**する

つまり`pytest.raises`は、`__exit__`という「ブロックの中で何が起きたか教えてもらえる仕組み」を使って、**「期待した例外が来たかどうかの合否判定装置」として振る舞っている**、ということ。

### 異常系4本の設計

`docs/plan.md`§5-3の検証4項目に対応させ、**1項目につき1か所だけ壊した**JSONを用意する。型はどれも同じ：「`valid_camera_dict()`を取得 → 1か所だけ書き換える → ファイルに書き出す → `pytest.raises(ValueError)`で`load_cameras()`を囲む」。

```python
def test_wrong_schema_version_raises(tmp_path):
    data = valid_camera_dict()
    data["schema_version"] = "invalid"

    path = tmp_path / "cameras.json"
    path.write_text(json.dumps(data))

    with pytest.raises(ValueError):
        load_cameras(path)


def test_wrong_convention_raises(tmp_path):
    data = valid_camera_dict()
    data["convention"]["world_up"] = "invalid"
    ...


def test_non_orthogonal_R_raises(tmp_path):
    data = valid_camera_dict()
    data["views"][0]["R"] = [[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, 0]]
    ...


def test_mirrored_R_raises(tmp_path):
    data = valid_camera_dict()
    data["views"][0]["R"] = [[1, 0, 0],
                             [0, 1, 0],
                             [0, 0, -1]]
    ...
```

**`test_non_orthogonal_R_raises`と`test_mirrored_R_raises`を分けている理由**：`validate()`の検証項目は「`RᵀR ≈ I`（直交性）」と「`det(R) ≈ +1`（鏡映でないか）」の2つに分かれているので、それぞれを**単独で**壊すJSONを用意し、どちらの検証が効いているかを個別に確認できるようにしている。

- `[[1,0,0],[0,1,0],[0,0,0]]` → `RᵀR = diag(1,1,0) ≠ I`（直交性が崩れる）
- `[[1,0,0],[0,1,0],[0,0,-1]]` → `RᵀR = I`（直交性は保たれる）が`det = -1`（鏡映）
