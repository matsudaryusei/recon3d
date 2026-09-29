# 次にやること

> **迷ったらまずこのページです。** 下の [§1](#w02) の表から、空いているものを1つ取るだけです。
> **W01 からの持ち越し（[T01](tasks/T01-pairpro1-io.md)〜[T10](tasks/T10-read-scope.md)）はすべて完了しました。** 一覧は [§5](#done) に移してあります。**いまの表は W02 から始まる実装作業です。**

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
**W01 の持ち越し（[T01](tasks/T01-pairpro1-io.md)〜[T10](tasks/T10-read-scope.md)）はすべて完了しました。**
**他ジャンルの前提も外れているので、[§1 の W02 作業](#w02)（G1・G2・G3・G7）に着手できます。**
→ 経緯は [README の現在地](README.md)、詰まった点と学びは `docs/notes/`。

---

<a id="w02"></a>
## 1. 次にやること（W02 実装作業）

**W01 からの持ち越し（[T01](tasks/T01-pairpro1-io.md)〜[T10](tasks/T10-read-scope.md)）はすべて完了したので、この表からは外しました。** 一覧・完了日は [§5 終わったタスクの置き場](#done) にあります。

**いま着手できるのは、[計画書 §10 Phase 0](plan.md#s10) が決めている W02 の実装作業です。担当者は書きません。取れる人が取ってください**（[計画書 §3-2](plan.md#s3-2)）。取ったら Issue に自分を入れてください。

### W02 の流れ（この順に進めます）

```
【松田・Blender 端末】                        【関口・Blender なし】

 T11 マスク方式を決める（2人・30分）
      │
 T12 元モデルを .blend に整える／長さの単位を決める     T14 画像なしの合成シーン生成器（G7）
      │                                                   ↑ T11〜T13 と独立。いつでも着手可
 T13 blender_render.py（G2）── data/synthetic_cup/ を対面で渡す ──┐
                                                                  ↓
                                                     T15 OpenCV 版パイプライン（G1・G3）
                                                                  │
                                                         W03（実測・実写）へ
```

| # | 手順書 | ジャンル | 誰が | 実装の芯（**手順書は空けている**） | 状態 |
|---|---|---|---|---|---|
| T11 | [マスク方式を決める](tasks/T11-decide-mask-method.md) | G2・G3 | 2人（EEVEE 確認は松田） | 採用方式の判断 | ⬜ 未着手 |
| T12 | [元モデルを `.blend` に整える・長さの単位を決める](tasks/T12-prepare-blend.md) | G2 | 松田 | 単位の判断 | ⬜ 未着手 |
| T13 | [`blender_render.py`（20方向レンダリング）](tasks/T13-blender-render.md) | G2 | 松田 | カメラ配置・`R`,`t`・`fx`,`cx` の導出 | ⬜ 未着手 |
| T14 | [`synthetic_scene.py`（画像なしの合成シーン）](tasks/T14-synthetic-scene.md) | G7 | 取れる人 | 生成器の設計・テストの期待値 | ⬜ 未着手 |
| T15 | [OpenCV 版パイプライン](tasks/T15-opencv-pipeline.md) | G1・G3 | 関口（T13 の出力待ち） | 関数のつなぎ方・`solvePnP` の 3D 点の出どころ | ⬜ 未着手 |

> **T13 が終わるまでの関口の待ち方**：[T14](tasks/T14-synthetic-scene.md) を進めるか、[学びの入口 G1・G3](learning.md) の資料を読み始めてください（T15 の前提知識です）。
> **手順書に書いてあるのは、環境・コマンド・置き場所・確認の仕方です。** 導出・実装・設計判断は [書かないと決めている範囲](tasks/README.md)なので空けてあります。
> **前提だった [T01](tasks/T01-pairpro1-io.md) は完了済みです**（2026-09-05・PR #4）。担当者は書かず、取ったら Issue に自分を入れてください。
> 取りかかる前に、**[学びの入口](learning.md) のそのジャンルの行**を読んでください。

---

### この表と GitHub Issue の使い分け

**二重に管理しないための取り決めです。**

> **✅ [T06](tasks/T06-labels-and-board.md) は 2026-09-07 に完了。いまは上の表（§1）の「T06 のあと」の運用です。**

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

> **手順書付きのタスク（[T01](tasks/T01-pairpro1-io.md)〜[T10](tasks/T10-read-scope.md)）はすべて完了したため、時間で選べる小粒のタスクはもうありません。**
> **いま残っているのは [§1 の W02 実装作業](#w02)（G1・G2・G3・G7）だけで、どれも「実装そのもの」なので45分〜2時間には収まりません。** 空き時間が短いときは、[計画書 §10](plan.md#s10) と該当ジャンルの [学びの入口](learning.md) を読むところから始めてください。

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

<a id="done"></a>
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
