# T06 — ラベルを登録して Projects ボードを1枚作る

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G9 ドキュメント・運用** |
| 目安時間 | **45分**（ラベルとボードで15分、Issue 10件で30分。**Issue は3件だけ先に作る手もあります**） |
| 前提 | リポジトリ設定の変更権限（**2026-08-16 に取得済み**） |
| 作るもの | GitHub のラベル17個と Projects ボード1枚（ファイルは増えません） |
| 仕様の出どころ | [計画書 §8-3](../plan.md#s8-3) |

---

> **先に読むもの**：特にありません。**コマンドを貼るだけです。**

## なぜやるのか

**「誰がやるか」を決めない運用（[計画書 §3-2](../plan.md#s3-2)）は、代わりに「何の作業か」が一目で分かる必要があります。**

いまラベルは GitHub の既定（`bug` `enhancement` など）しかなく、**ジャンル G1〜G9 が登録されていません。** Issue を切っても分類できない状態です。

---

## ステップ1：ラベルを登録する

### `gh` コマンドが使える場合（速い）

`gh --version` が通るか確認してください。通るなら**下をそのままターミナルに貼り付けます。**

```bash
# ジャンル（§3-3）— 青
gh label create "G1:数理コア"     --color 1D76DB --description "DLT・三角測量・バンドル調整・ソルバ" --force
gh label create "G2:3DCG"         --color 1D76DB --description "Blender・合成データ生成" --force
gh label create "G3:画像処理"     --color 1D76DB --description "セグメンテーション・特徴点" --force
gh label create "G4:メッシュ"     --color 1D76DB --description "Marching Cubes・簡略化・平滑化・テクスチャ" --force
gh label create "G5:ボクセル統合" --color 1D76DB --description "ボクセル彫刻・点群による補正" --force
gh label create "G6:基盤IO"       --color 1D76DB --description "cameras.json・座標変換・CLI・環境" --force
gh label create "G7:テストCI"     --color 1D76DB --description "pytest・GitHub Actions" --force
gh label create "G8:実験可視化"   --color 1D76DB --description "E1〜E7・グラフ・デモ" --force
gh label create "G9:ドキュメント" --color 1D76DB --description "README・メモ・Issue運用・進捗" --force

# フェーズ — 紫
gh label create "phase:0" --color 5319E7 --description "技術検証 W01-W03" --force
gh label create "phase:1" --color 5319E7 --description "要件定義・基本設計 W04-W05" --force
gh label create "phase:2" --color 5319E7 --description "数理コアの自作 W06-W11" --force
gh label create "phase:3" --color 5319E7 --description "Visual Hull統合とメッシュ化 W12-W15" --force
gh label create "phase:4" --color 5319E7 --description "評価実験 W16-W18" --force

# 特殊
gh label create "pair"             --color FBCA04 --description "ペアプロ対象（2人で同時に作業する）" --force
gh label create "blocked"          --color B60205 --description "他のタスク待ちで進められない" --force
gh label create "good-first-issue" --color 0E8A16 --description "新しく入った人向け" --force
```

> `--force` は「同じ名前があれば上書き」。**何度流しても壊れません。**

### `gh` が無い場合（Web でやる）

1. リポジトリの **`Issues` タブ** → 右上の **`Labels`**
2. **`New label`** を押す
3. 上のコマンドの `"..."` がラベル名、`--color` の6桁が色（`#` は入れない）、`--description` が説明
4. **17個ぶん繰り返す**

**`gh` を入れておくと今後も楽です**（`brew install gh` → `gh auth login`）。

---

## ステップ2：既定のラベルを片付ける

**GitHub が最初から作る `duplicate` `invalid` `wontfix` などは使いません。** 残っていると選ぶときに邪魔なので消してよいです。

```bash
gh label delete "duplicate" --yes
gh label delete "invalid"   --yes
gh label delete "wontfix"   --yes
gh label delete "question"  --yes
gh label delete "help wanted" --yes
```

**`bug` `enhancement` `documentation` は残してよい**（併用して困りません）。

---

## ステップ3：Projects ボードを1枚作る

1. リポジトリの **`Projects` タブ** → **`New project`**
2. テンプレートは **`Board`** を選ぶ
3. 名前：**`3D復元 開発ボード`**
4. **列（Status）を4つにする**（[計画書 §8-3](../plan.md#s8-3)）：

| 列 | 意味 |
|---|---|
| `Todo` | 切ったが未着手 |
| `In Progress` | 誰かが着手中（**Assignee がここで初めて入る**） |
| `In Review` | PR を出してレビュー待ち |
| `Done` | マージ済み |

既定では `Todo` / `In Progress` / `Done` の3列なので、**`In Review` を1つ足します**（列見出しの `+` から）。

---

## ステップ4：いま残っているタスクを Issue にする

**[次にやること](../next.md) の表にある T01〜T10 を、そのまま Issue にします。**

1つずつ手で作ってもよいですが、`gh` があるなら：

```bash
gh issue create \
  --title "T01 ペアプロ#1：座標系と cameras.json を決めて実装する" \
  --body "手順書: docs/tasks/T01-pairpro1-io.md" \
  --label "G6:基盤IO" --label "phase:0" --label "pair"
```

**残り9件も同じ形で作ります。** ラベルの対応：

| Issue | ラベル |
|---|---|
| T01 ペアプロ#1 | `G6:基盤IO` `phase:0` `pair` |
| T02 口頭で決める4件 | `G9:ドキュメント` `phase:0` |
| T03 CI の雛形 | `G7:テストCI` `phase:0` |
| T04 ブランチ保護 | `G7:テストCI` `phase:0` |
| T05 Git の練習 | `G9:ドキュメント` `phase:0` `good-first-issue` |
| T06 ラベルとボード | `G9:ドキュメント` `phase:0` |
| T07 マスク方式の候補 | `G3:画像処理` `phase:0` |
| T08 Blender 入口メモ | `G2:3DCG` `phase:0` `good-first-issue` |
| T09 3Dモデル探し | `G2:3DCG` `phase:0` `good-first-issue` |
| T10 スコープを読む | `G9:ドキュメント` `phase:0` `good-first-issue` |

**作った Issue をボードの `Todo` に入れます**（Issue ページ右の `Projects` から選ぶ）。

> ⚠️ **Assignee（担当者）はいま入れません。** [計画書 §3-2](../plan.md#s3-2) のとおり、**着手する時点で自分を入れる**運用です。**未着手の Issue に担当者が入っていないのは正常**です。

---

## 完了判定

- [ ] `Issues` → `Labels` に **`G1:数理コア` 〜 `G9:ドキュメント` の9個**が並んでいる
- [ ] `phase:0` 〜 `phase:4` の5個がある
- [ ] `pair` / `blocked` / `good-first-issue` の3個がある
- [ ] `Projects` に **`3D復元 開発ボード`** があり、列が **`Todo` / `In Progress` / `In Review` / `Done`** の4つ
- [ ] **T01〜T10 の Issue が10件**でき、全部が `Todo` にあり、**全部にジャンルのラベルが付いている**
- [ ] **どの Issue にも Assignee が入っていない**
- [ ] **[next.md](../next.md) の「この表と GitHub Issue の使い分け」を読み、以降は着手の記録を Issue 側に寄せることを全員が把握している**

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `gh: command not found` | `brew install gh`（mac）／[GitHub CLI](https://cli.github.com/) を入れる。**入れずに Web でやっても構いません**（ステップ1の後半） |
| `gh auth login` を求められる | ブラウザが開くので、そこで許可します。**1回だけ** |
| **`HTTP 403` / 権限が無いと言われる** | リポジトリ設定の変更権限が要ります。**2026-08-16 に取得済み**のはずなので、通らなければ関口に相談 |
| **ラベル名の日本語が文字化けする** | ターミナルの文字コードの問題。**Web の画面から作れば確実**です |
| `already exists` と出る | `--force` を付けているので上書きされます。**エラーではありません** |
| **`Projects` タブが見当たらない** | `Settings` → `General` → `Features` で `Projects` にチェックが入っているか確認 |
| **`gh project create` が権限エラーになる** | Projects は別スコープが要ります。`gh auth refresh -s project`、または**Web で作るほうが早い** |
| Issue を10件も手で作るのがつらい | **T01〜T03 の3件だけ先に作れば十分**です。残りは着手するときに作れば構いません |

## 終わったら

1. **詰まった点・学んだことを `docs/notes/` に1本残す**
2. [次にやること](../next.md) の T06 の状態を `✅ 完了` に書き換える
3. **連絡帳（`Notice.md`・public 化で廃止） に1行**：「Issue を**（実際に作った件数）**件切りました。**取るときは Assignee に自分を入れて `In Progress` へ。** `next.md` の表は、完了したときに `✅` を付けるだけでよくなりました」
