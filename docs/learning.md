# 学びの入口

**「書けそうにない」と思ったときに開くページです。**
ジャンルごとに、**そこを書けるようになるための資料を3本まで**に絞ってあります。

---

## この文書の方針

**[D-33](decisions.md#d-33) で「生成AIを使わずにコードを書く」と決めています。**
その前提を成り立たせるには、**答えの代わりに、答えにたどり着く道**が要ります。それがこの文書です。

> ### ⚠️ ここに書かないこと（意図的に空けてあります）
>
> | 書かない | 理由 |
> |---|---|
> | **アルゴリズムの導出・数式の変形** | **ここが本プロジェクトの芯です**（[計画書 §3-8](plan.md#s3-8)「反復解法・最適化・幾何アルゴリズムは自作する」）。答えを書いたら自作した意味がなくなります |
> | **実装コード** | 同上。手順書に載せるのは関数の形（シグネチャ）と通すべきテストまで |
> | **設計の選択の結論** | 「どちらが良いか」は自分たちで比べて決めるところです。決めた結果は [決定記録](decisions.md) に残します |
> | **資料の要約** | 要約を読むと、読んだ気になって身につきません。**リンクと「何が分かるか」だけ**にしてあります |
>
> **逆に、環境構築・ツールの操作・設定ファイルは [手順書](tasks/) に全部書いてあります。**
> あそこで詰まっても何も学べないので、時間を使わせない方針です。

---

## 0. まず共通（どのジャンルでも要る）

**Python 歴が数か月なら、ここから。下の3本で合計3時間ほどです。**

| # | 資料 | 何が分かるか | 目安 |
|---|---|---|---|
| 1 | [Python 公式チュートリアル（日本語）](https://docs.python.org/ja/3/tutorial/) — **3〜6章だけ**でよい | 3〜4章＝制御フローと関数、**5章＝リスト・辞書（C との違いが一番大きい）**、6章＝モジュール | 2h |
| 2 | [型ヒント（`typing`）](https://docs.python.org/ja/3/library/typing.html) — **冒頭の例だけ**でよい | `def f(x: int) -> str:` の読み方。**本プロジェクトは PR で型ヒントを指摘対象にします**（[計画書 §7-7](plan.md#s7-7)） | 30分 |
| 3 | [`pathlib`](https://docs.python.org/ja/3/library/pathlib.html) | ファイルパスの扱い。**`os.path` ではなくこちらを使います**（Windows と mac の差を吸収してくれる） | 30分 |

**環境まわり（`uv`・仮想環境）で詰まったら** → [uv 公式ドキュメント](https://docs.astral.sh/uv/)。
ただし**基本的に手順書に書いてあるコマンドをそのまま打てば通ります。** 詰まったら GitHub の Issue で聞いてください。

---

## ジャンル別

**[計画書 §3-3 の作業ジャンル](plan.md#s3-3)に対応しています。取ったジャンルの行だけ見てください。**

### G6 基盤・I/O ＋ G7 テスト・CI 〔W01から〕

**最初に着手するジャンルなので、ここだけは早めに。**

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [`dataclasses`](https://docs.python.org/ja/3/library/dataclasses.html) | 値を持つだけのクラスの書き方。**`cameras.json` の読み書きがこれで書けます**（[T01](tasks/T01-pairpro1-io.md)） | 30分 |
| [pytest の入門](https://docs.pytest.org/en/stable/getting-started.html) | テストの書き方・`assert` の使い方・`pytest.raises` で例外を確かめる方法 | 1h |
| [NumPy 初心者向けガイド](https://numpy.org/doc/stable/user/absolute_beginners.html) | 配列の作り方・形（shape）・スライス。**`@`（行列積）と `*`（要素ごとの積）の違いは必ず押さえる** | 1.5h |

### G1 数理コア 〔W06–W11・一番重い〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| **Szeliski, *Computer Vision: Algorithms and Applications*** — [著者が全文PDFを公開](https://szeliski.org/Book/) | 三角測量・カメラモデル・バンドル調整の**全体像**。まず「どこに何があるか」を掴む用 | 該当章のみ |
| **Hartley & Zisserman, *Multiple View Geometry*** — [書籍サポートページ](https://www.robots.ox.ac.uk/~vgg/hzbook/) | **DLT と三角測量の定番**。本プロジェクトが自作する部分の原典 | 該当節のみ |
| **Shewchuk, *An Introduction to the Conjugate Gradient Method Without the Agonizing Pain*** — [CMU 公開PDF](https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf) | **CG法の説明として定評のある無料資料。** 図が多く、なぜ収束するかが追える | 1〜2日 |

**補助**：[SciPy の疎行列](https://docs.scipy.org/doc/scipy/reference/sparse.html) — 自作した CG 法の答え合わせに使います（[計画書 §9-1](plan.md#s9-1) 第2層）。

### G2 3DCG・データ生成 〔W02–W03〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [Blender Python API クイックスタート](https://docs.blender.org/api/current/info_quickstart.html) | `bpy` の考え方。**オブジェクトをどう取り、どう設定するか** | 1h |
| [Blender マニュアル：スクリプティング入門](https://docs.blender.org/manual/en/latest/advanced/scripting/introduction.html) | Scripting タブと、GUI の操作がどの Python 呼び出しに対応するか | 30分 |
| （自前）[T08 の入口メモ](tasks/T08-blender-entry-note.md) | **CLI（`blender --background`）での実行手順。書いたら `docs/notes/` に残す** | — |

> ⚠️ **Blender は `uv` で作った `.venv` とは別の Python で動きます。** `uv add` で入れた `scipy` などは**Blender 側からは見えません**。
> **[計画書 §7-4](plan.md#s7-4) は「`tools/blender_*.py` は `bpy` と `numpy` のみに依存させる」と決めています**（環境に他が無いという意味ではなく、**自分たちに課した制約**です）。
> **`pip install` を前提にした記事は、その制約から外れます。**

### G3 画像処理 〔W06–W09〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [OpenCV 公式チュートリアル](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html) | 画像の読み書き・特徴点検出・マッチング | 該当節のみ |
| [OpenCV-Python チュートリアル（旧版ミラー）](https://opencv-python-tutroals.readthedocs.io/en/latest/) | 構成が平易で読みやすい。⚠️ **OpenCV 2.4／3.0 時代のまま更新が止まっており、4.x とコードが食い違う箇所があります**（`cv2.findContours` の戻り値の個数、`cv2.SIFT()`、`cv2.cv` 定数など）。**考え方を掴む用。動かすコードは公式の 4.x を見ること** | 該当節のみ |
| [NumPy のブロードキャスト](https://numpy.org/doc/stable/user/basics.broadcasting.html) | 画像を for ループで回さずに処理する考え方。**速度に直結** | 30分 |

### G4 メッシュ処理 〔W10–W15〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| **Szeliski 本**（G1 と同じ、[PDF](https://szeliski.org/Book/)） | 3D表現・メッシュの章 | 該当章のみ |
| [Open3D のメッシュ操作](https://www.open3d.org/docs/release/tutorial/geometry/mesh.html) | メッシュのデータ構造（頂点配列と面配列）の実物。**自作の答え合わせ用** | 30分 |
| （自前）[用語集の §4](glossary.md) | Marching Cubes・QEM・cotan重みが**何であるか**の1行定義 | 5分 |

> **自作の範囲は 2026-09-07（[T02](tasks/T02-oral-decisions.md)④）で現行どおり確定しました**（→ [D-40](decisions.md#d-40)）。Marching Cubes・QEM・ラプラシアン平滑化・テクスチャ投影は自作、**UV展開だけ Blender の Smart UV Project** に任せます。

### G5 ボクセル・統合 〔W12–W13〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [NumPy のブロードキャスト](https://numpy.org/doc/stable/user/basics.broadcasting.html) | **ボクセル彫刻を行列演算で書くための土台。** for ループで書くと終わりません | 30分 |
| [NumPy のインデックス参照](https://numpy.org/doc/stable/user/basics.indexing.html) | 大きな3D配列を切り分けて扱う（チャンク分割）ときの書き方 | 30分 |

> **256³ のボクセルをメモリ 16GB で扱います**（[計画書 §7-6](plan.md)）。**どう分割するかは自分たちで設計するところ**なので、ここには書きません。

### G8 評価実験・可視化 〔W16–W18〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [Matplotlib の pyplot 入門](https://matplotlib.org/stable/tutorials/pyplot.html) | グラフの描き方。実験 E1〜E7 の図に使う | 1h |

> **何を測るか・どう見せるかは実験設計そのもの**なので、[計画書 §11](plan.md#s11) を読んで自分たちで決めてください。

### G9 ドキュメント・運用 〔通期〕

| 資料 | 何が分かるか | 目安 |
|---|---|---|
| [Pro Git（日本語・全文無料）](https://git-scm.com/book/ja/v2) — **3章「ブランチ機能」だけ**でよい | ブランチが何をしているか。**conflict が怖くなくなります** | 1.5h |
| [GitHub Actions のドキュメント（日本語）](https://docs.github.com/ja/actions) | CI の設定ファイルの読み方（[T03](tasks/T03-ci-workflow.md) で使う） | 30分 |

---

## いつ読むか（タスクとの対応）

**手順書の冒頭にも同じことが書いてあります。** 着手前に該当する行だけ読めば足ります。

| これから取るタスク | 先に読むもの |
|---|---|
| [T01 ペアプロ#1](tasks/T01-pairpro1-io.md) | **共通 1〜3 ＋ G6 の3本**（dataclass・pytest・NumPy） |
| [T03 CI の雛形](tasks/T03-ci-workflow.md) | G9 の GitHub Actions（読まなくても手順どおりで通ります） |
| [T05 Git の練習](tasks/T05-git-practice.md) | G9 の Pro Git 3章 |
| [T07 マスク方式の候補](tasks/T07-mask-options.md) | G2 の Blender マニュアル |
| [T08 Blender 入口メモ](tasks/T08-blender-entry-note.md) | G2 の3本 |
| W06 以降（数理コア） | **G1 の3本。W05 のうちに読み始めておくこと** |

---

## 足し方

**読んで良かったものは、ここに1行足してください。** ただし**ジャンルごとに3本まで**です。

| ルール | 理由 |
|---|---|
| **1ジャンル3本まで** | 10本並ぶと「どれから読めばいいか分からない」になり、結局読まれません。**入れ替える形で足す** |
| **「何が分かるか」を必ず書く** | リンクだけ並んでいても選べません |
| **無料で読めるものを優先** | 全員がすぐ開けることを優先します |
| **要約は書かない** | 読んだ気になるだけです。**要約したくなったら、それは `docs/notes/` に自分の言葉で書くべき内容**です |

> **リンクが切れていたら直してください。** なお `docs.opencv.org` は `curl` などの自動アクセスを `403` で拒否しますが、**ブラウザでは正常に開けます**（リンク切れではありません）。**リンクを自動検査する仕組みはまだ入っていません。**
