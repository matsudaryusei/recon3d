# 次にやること

> **迷ったらまずこのページです。** 表の上から順に、空いているものを1つ取るだけです。
> 各タスクには**手順書**が付いています。リンクを開けば「何を打ち込むか」「何ができたら終わりか」まで書いてあります。
>
> **⚠️ この表は「W01 からの持ち越し」だけです。** W02 から始まる本来の実装作業は **[§1-b](#w02)** に別で挙げてあります。

**いまの状況**（このブロックは、下の表の状態を書き換えるときに一緒に更新してください）

**2026-09-23**
**public 化の準備をしました**（[D-42](decisions.md#d-42)）。個人情報を含む `docs/internal/`・`blender_system/`・`Notice.md` を外し、ルートに公開用の `README.md` と `LICENSE`（MIT）を置きました。**対面でないときの連絡は、今後は GitHub の Issue で行います。**
**[T09](tasks/T09-find-3d-model.md) が完了しました**（2026-09-23）。候補は [docs/notes/model-candidates.md](notes/model-candidates.md) に、主データ3件・副データ2件をまとめました（どれも CC0 か自作）。**推す案は、主データ（`synthetic_cup`）が Ceramic Pot、副データ（`synthetic_bunny`）が Food Lychee 01** です（どちらも Poly Haven・CC0）。副データはテクスチャが焼き込み済みなので、貼り足す必要はありません。[計画書 §14](plan.md#s14) の 8 番と [§16](plan.md#s16) の該当行は消し込み済みです。**これで [T01](tasks/T01-pairpro1-io.md)〜[T10](tasks/T10-read-scope.md) はすべて完了しました。**
**[T10](tasks/T10-read-scope.md) が完了しました**（2026-09-23）。関口・松田の2人でスコープ（§3-8）と撤退ライン（§12）を読み合わせ、完了判定3問に回答（詳細は [決定記録 D-41](decisions.md#d-41)）。**public 化の時期を「今すぐ」に決定**（[D-27](decisions.md#d-27)・[D-40](decisions.md#d-40)⑤の「完成後」から前倒し）。[計画書 §16](plan.md#s16) の該当行は削除済み。**リポジトリの改名（[D-27](decisions.md#d-27)）と実際の公開設定はまだ未実施。**

**2026-09-22**
**[T08](tasks/T08-blender-entry-note.md) が完了しました**（2026-09-22）。動作確認用の `tools/hello_bpy.py` と、入口メモ `docs/notes/blender-entry.md` を追加。`blender -b -P tools/hello_bpy.py` で Blender 5.0.1 / Python 3.11.13 / numpy 1.26.4（計画書の前提と一致）を確認済み。PowerShellのエイリアス化（プロファイルへの追記・実行ポリシー `RemoteSigned` への変更が必要だった点）、相対パスがカレントディレクトリ基準で解決される点などを詰まった点として記録した。

**2026-09-07 / W03**
**[T06](tasks/T06-labels-and-board.md) が完了しました**（2026-09-07）。GitHub のラベル17個（`G1`〜`G9` ジャンル／`phase:0`〜`phase:4`／`pair`・`blocked`・`good-first-issue`）を登録し、既定ラベル（`duplicate` など）を整理。Projects ボード **`3D復元 開発ボード`**（`Todo` / `In Progress` / `In Review` / `Done` の4列）を作成しました。**T01〜T10 を Issue 10件**にしてジャンルのラベルを付与し、ボードの `Todo` に配置（完了済みの T01〜T05 は `Done` へ移動）。**これ以降、「誰が何を作業中か」の管理は GitHub Issue（Assignee＋`In Progress` 列）に移ります。この表は完了時に `✅` を付けるだけです**（下の「この表と GitHub Issue の使い分け」）。
**[T05](tasks/T05-git-practice.md) が完了しました**（2026-09-07）。関口・松田とも branch → PR → レビュー → squash merge を1周（練習PR #8 ほか）。以降の本番作業は全員 PR 経由です。
**[T04](tasks/T04-branch-protection.md) が完了しました**（2026-09-07）。GitHub の Ruleset `protect-main` で `main` への直 push を禁止し、PR 必須・`pytest (ubuntu-latest)` / `pytest (windows-latest)` のステータスチェック必須にしました。マージ方式も `Squash and merge` のみに統一済み。push が拒否されることの実地確認も完了（[D-22](decisions.md#d-22)）。
**[T03](tasks/T03-ci-workflow.md) が完了しました**（2026-09-06・PR #6）。`.github/workflows/ci.yml` を追加し、**PR と `main` への push で Ubuntu と Windows の2環境の `uv run pytest`** が自動で回るようになりました。手順書どおり `astral-sh/setup-uv@v5` で通り、`@v3` への降格は不要。両環境とも緑・ログの `uv run python -V` は `Python 3.11.13`・`10 passed` を確認（[D-24](decisions.md#d-24)）。
**[T02](tasks/T02-oral-decisions.md) が完了しました**（保留5件を確定）。最終成果物は `.blend`／撤退ラインは目標 L3 で認識合わせ済み／週の進め方は縛らず各自の空き時間で／メッシュ自作範囲は現行どおり／public 化の時期は [T10](tasks/T10-read-scope.md) 完了後に決める。詳細は [決定記録 D-40](decisions.md#d-40)。
**[T01](tasks/T01-pairpro1-io.md) も完了済み**（2026-09-05・PR #4）。座標系規約・`cameras.json` 仕様・`io/coords.py`・`io/cameras.py`・`tests/test_conventions.py` が入り、`uv run pytest` は **10 passed**。
**W01 の持ち越し（[T01](tasks/T01-pairpro1-io.md)〜[T06](tasks/T06-labels-and-board.md)）はすべて完了しました。**
**他ジャンルの前提も外れているので、[§1-b の W02 作業](#w02)（G1・G2・G3・G7）に着手できます。**
→ 経緯は [README の現在地](README.md)、詰まった点と学びは `docs/notes/`。

---

## 1. 表：残っているタスク

**担当者は書きません。取れる人が取ってください**（[計画書 §3-2](plan.md#s3-2)）。取ったら Issue に自分を入れてください。

| 優先 | # | タスク | ジャンル | 目安 | 前提 | 状態 |
|---|---|---|---|---|---|---|
| ✅ 済 | [T01](tasks/T01-pairpro1-io.md) | **ペアプロ#1：座標系と `cameras.json` を決めて実装する** | G6 基盤・I/O | 2h（2人） | **2人そろうこと**・`uv run pytest` が通ること | ✅ 完了（2026-09-05・#4） |
| ✅ 済 | [T02](tasks/T02-oral-decisions.md) | **保留になっている5件を口頭で決める** | 全員 | 15分 | **2人そろうこと**（T01 と同じ場でやる） | ✅ 完了（2026-09-07・[D-40](decisions.md#d-40)） |
| ✅ 済 | [T03](tasks/T03-ci-workflow.md) | CI（GitHub Actions）の雛形を置く | G7 テスト・CI | 1h | なし | ✅ 完了（2026-09-06・#6） |
| ✅ 済 | [T05](tasks/T05-git-practice.md) | Git の練習を1周する（branch → PR → merge） | 全員 | 1h | clone 済み・`uv run pytest` が通ること | ✅ 完了（2026-09-07・#8 ほか） |
| ✅ 済 | [T04](tasks/T04-branch-protection.md) | `main` ブランチを保護する | G7 テスト・CI | 30分 | **T05** が済んでいること（T03 は 2026-09-06 完了） | ✅ 完了（2026-09-07） |
| ✅ 済 | [T06](tasks/T06-labels-and-board.md) | ラベルを登録して Projects ボードを1枚作る | G9 ドキュメント・運用 | 45分 | **リポジトリ設定の変更権限**（取得済み） | ✅ 完了（2026-09-07） |
| ✅ 済 | [T07](tasks/T07-mask-options.md) | マスク生成方式の候補を1枚にまとめる（**W02 中に決める**） | G3 画像処理 | 2h | なし（Blender 不要） | ✅ 完了（2026-09-16・実機確認込み） |
| ✅ 済 | [T08](tasks/T08-blender-entry-note.md) | Blender スクリプトの入口メモを1本書く | G2 3DCG | 1.5h | Blender が入っている端末 | ✅ 完了（2026-09-22） |
| ✅ 済 | [T09](tasks/T09-find-3d-model.md) | 合成データ用の3Dモデルを探す（**凹み形状が必須**） | G2 3DCG | 1h | なし | ✅ 完了（2026-09-23） |
| ✅ 済 | [T10](tasks/T10-read-scope.md) | スコープと撤退ラインに目を通す | 全員 | 15分 | なし | ✅ 完了（2026-09-23） |

<a id="w02"></a>
### 1-b. W02 から始まる作業（手順書はまだありません）

**上の表は W01 の持ち越しです。** これとは別に、[計画書 §10 Phase 0](plan.md#s10) は W02 の作業を次のように決めています。

| ジャンル | やること | 出どころ |
|---|---|---|
| **G1・G3** | OpenCV の既存関数で**一直線にパイプラインを通す**（SIFT → `solvePnP` → `triangulatePoints` → Open3D 表示） | [計画書 §10](plan.md#s10) |
| **G2** | `tools/blender_render.py` を実装。`synthetic_cup` を20方向レンダリングし、`images/`・`masks/`・`cameras.json`・`gt_mesh.ply` を出力 | 同上 |
| **G7** | `tests/fixtures/synthetic_scene.py`（画像を使わない合成シーン生成器）を実装 | [計画書 §9-1](plan.md#s9-1) |

> **これらに手順書はまだありません。** 中身が**実装そのもの**で、[手順書に書かないと決めている範囲](tasks/README.md)だからです。
> **前提だった [T01](tasks/T01-pairpro1-io.md) は完了済みです**（2026-09-05・PR #4）。座標系と `cameras.json` は決まったので、着手できます。
> 取りかかるときは [計画書 §10](plan.md#s10) と該当ジャンルの節を読み、**[学びの入口](learning.md) のそのジャンルの行**から始めてください。

---

### この表と GitHub Issue の使い分け

**二重に管理しないための取り決めです。**

> **✅ [T06](tasks/T06-labels-and-board.md) は 2026-09-07 に完了。いまは下の表の「T06 のあと」の運用です。**

| 時期 | 「誰が何を作業中か」の正 | この表の役割 |
|---|---|---|
| ~~**[T06](tasks/T06-labels-and-board.md) が終わるまで**~~ | ~~**この表**。`🔄 作業中（名前）` と書く~~ | ~~唯一の管理表~~ |
| **T06 のあと（＝いま）** | **GitHub Issue**（Assignee と `In Progress` 列） | **完了したものに `✅` を付けるだけ。着手中はここを触らない** |

**なぜ分けるか**：`main` は [T04](tasks/T04-branch-protection.md) で保護されるので、**この表を1行直すだけでも PR が要ります。**
着手のたびに PR を出すのは重いので、**着手の記録は Issue に寄せ、この表はタスクの PR に混ぜて `✅` にする**運用にします。

**状態の書き方**: `⬜ 未着手` / `🔄 作業中（名前）` / `✅ 完了（日付・PR番号）`

---

## 2. 時間で選ぶ

**「今日は◯分しかない」ときの取り方です。**

| 空いている時間 | おすすめ |
|---|---|
| **15分** | ~~[T10 スコープを読む](tasks/T10-read-scope.md)~~ **完了済み（2026-09-23・public 化の時期は [D-41](decisions.md#d-41) で決定）** |
| **30分** | ~~[T04 ブランチ保護](tasks/T04-branch-protection.md)~~ **完了済み（2026-09-07）** |
| **45分〜1時間** | ~~[T03 CI の雛形](tasks/T03-ci-workflow.md)~~ **完了済み（2026-09-06・#6）** ／ ~~[T05 Git の練習](tasks/T05-git-practice.md)~~ **完了済み（2026-09-07）** ／ ~~[T06 ラベルとボード](tasks/T06-labels-and-board.md)~~ **完了済み（2026-09-07）** ／ ~~[T09 3Dモデル探し](tasks/T09-find-3d-model.md)~~ **完了済み（2026-09-23）** |
| **2時間・2人そろう** | ~~[T01 ペアプロ#1](tasks/T01-pairpro1-io.md)~~ **完了済み（2026-09-05・#4）**。次は [§1-b の W02 作業](#w02) |
| **1.5〜2時間・1人** | ~~[T07 マスク方式の候補](tasks/T07-mask-options.md)~~ **完了済み（2026-09-16）** ／ ~~[T08 Blender 入口メモ](tasks/T08-blender-entry-note.md)~~ **完了済み（2026-09-22）** |

---

## 3. どのタスクを取ってもやること（前後の作法）

**手順書の中にも書いてありますが、共通なのでここにまとめます。**

### 始めるとき

```bash
git switch main
git pull origin main
uv sync                      # 依存が変わっていたときのため。毎回1回流して損はない
git switch -c feat/<何をするか>   # 例: feat/ci-workflow
```

ブランチ名の付け方は [計画書 §8-1](plan.md#s8-1)（`feat/` `fix/` `docs/` `exp/`）。

### 終わったとき

1. **PR を出す。** 説明文は「何を」「なぜ」を1〜3段落（[計画書 §8-2](plan.md#s8-2)）
2. **このページの表の「状態」を `✅ 完了（日付・PR番号）` に書き換える**（完了日の記録はここが正）
3. **詰まった点・学んだことを `docs/notes/` に残す**
4. 計画や決定を変えたときは、[決定記録の「計画を変えた記録」](decisions.md#changes)に1行残す（[D-28](decisions.md#d-28)）

---

## 4. このページと他の文書の関係

| 知りたいこと | 開くもの |
|---|---|
| **次に何をするか・どうやるか** | **本ページと `tasks/` の手順書** |
| **言葉の意味が分からない** | [用語集](glossary.md) |
| **知識が足りなくて書けない** | [学びの入口](learning.md)（ジャンル別に資料3本まで） |
| **詰まった点・学んだことを残したい** | `docs/notes/` |
| いま全体のどこにいるか | [README](README.md) |
| 仕様・日程・決めごとの本文 | [計画書](plan.md) |
| なぜそう決めたか | [決定記録](decisions.md) |

> **手順書（`tasks/*.md`）は「やり方」だけを書く場所です。** 仕様そのものは計画書に、理由は決定記録にあります。
> **食い違ったときは計画書と決定記録が正**です。手順書のほうを直してください。

> ### 手順書に「答え」が書いていないのは、わざとです
>
> **環境構築とツール操作は全部書いてあります**（詰まっても学びがないので）。
> **一方で、導出・実装・設計の判断は空けてあります。** そこが本プロジェクトの芯だからです（[計画書 §3-8](plan.md#s3-8)・[D-33](decisions.md#d-33)）。
> **足りないのは知識であって答えではない**ので、行き先は [学びの入口](learning.md) に置いてあります。

---

## 5. 終わったタスクの置き場

**完了したら表から消さず、状態を `✅` にして下に移してください。** 何をやったかの一覧が残ります。

| # | タスク | 完了 |
|---|---|---|
| — | G6：`.gitattributes` / `.gitignore` / `pyproject.toml` / `.python-version` / pytest 導入 | ✅ 2026-08-17〜08-20 |
| — | G6：ディレクトリ骨格（[計画書 §6-2](plan.md#s6-2) の範囲）と `import recon3d` の疎通 | ✅ 2026-08-20（push 済み） |
| — | 全員：3台（mac / Windows / Ubuntu）で `uv sync` + `uv run pytest` が `1 passed` | ✅ 2026-08-24 |
| [T01](tasks/T01-pairpro1-io.md) | ペアプロ#1：座標系と `cameras.json` を決めて実装 | ✅ 2026-09-05（#4） |
| [T03](tasks/T03-ci-workflow.md) | CI（GitHub Actions）の雛形を置く（`.github/workflows/ci.yml`。Ubuntu + Windows で `pytest`） | ✅ 2026-09-06（#6） |
| [T02](tasks/T02-oral-decisions.md) | 保留5件を口頭で決める（→ [D-40](decisions.md#d-40)） | ✅ 2026-09-07 |
| [T04](tasks/T04-branch-protection.md) | `main` ブランチを保護する（Ruleset `protect-main`。PR 必須・ステータスチェック必須・squash merge のみ） | ✅ 2026-09-07 |
| [T05](tasks/T05-git-practice.md) | Git の練習を1周する（branch → PR → レビュー → squash merge。練習メモを `notes/` に追加） | ✅ 2026-09-07（#8 ほか） |
| [T06](tasks/T06-labels-and-board.md) | ラベル17個の登録と Projects ボード `3D復元 開発ボード` の作成（T01〜T10 を Issue 化） | ✅ 2026-09-07 |
| [T07](tasks/T07-mask-options.md) | マスク生成方式の候補を1枚にまとめる（`docs/notes/mask-options.md`。ID Mask 方式を推す案として実機確認。決定は [計画書 §16](plan.md#s16) で継続） | ✅ 2026-09-16（#20） |
| [T08](tasks/T08-blender-entry-note.md) | Blenderスクリプトの入口メモ（`tools/hello_bpy.py`・`docs/notes/blender-entry.md`）を作成し、CLI実行を実機確認 | ✅ 2026-09-22（#21） |
| [T09](tasks/T09-find-3d-model.md) | 合成データ用3Dモデルの候補（`docs/notes/model-candidates.md`。主データ3件・副データ2件、すべて CC0 か自作）。推す案は主 Ceramic Pot・副 Food Lychee 01 | ✅ 2026-09-23 |
| [T10](tasks/T10-read-scope.md) | スコープ（§3-8）・撤退ライン（§12）を2人で通読。完了判定3問に回答し、public 化の時期を「今すぐ」に決定（→ [D-41](decisions.md#d-41)） | ✅ 2026-09-23 |
