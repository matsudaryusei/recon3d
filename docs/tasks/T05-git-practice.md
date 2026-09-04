# T05 — Git の練習を1周する（branch → PR → レビュー → merge）

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **全員**（[計画書 §7-7](../plan.md#s7-7) の入口整備 1） |
| 目安時間 | 1時間 |
| 前提 | clone 済み・`uv run pytest` が通ること |
| 作るもの | **練習用の PR 1本**（マージして終わり。中身は何でもよい） |
| 出どころ | [計画書 §7-7](../plan.md#s7-7) ／ [§8-1](../plan.md#s8-1)・[§8-2](../plan.md#s8-2) |

---

> **先に読むもの**：[Pro Git 日本語版の3章「ブランチ機能」](https://git-scm.com/book/ja/v2)（1.5h）。**読まずに手を動かしてもよい**ですが、
> **conflict が出たときに何が起きているか**は3章を読んでいないと分かりません。→ [学びの入口 G9](../learning.md)

## なぜやるのか

**これまでは `git add` → `commit` → `push origin main` の3つだけで回してきました**（[HowToPush.md](../../HowToPush.md)）。
[T04](T04-branch-protection.md) で `main` が保護されると、**この手順はもう通りません。**

**本番の作業で初めて PR を出すと、慣れていないぶん実装より Git で時間が溶けます。** だから**中身が何でもいい練習を1本**先に通します。**壊しても何も困らない状態でやるのが目的です。**

---

## 用語（先にこれだけ）

| 用語 | 意味 |
|---|---|
| **branch（ブランチ）** | 作業用の枝。`main` を触らずに好きなだけ commit できる |
| **PR（プルリクエスト）** | 「この枝を `main` に入れてください」という申請。**議論の場でもある** |
| **review（レビュー）** | 相手の PR を読んでコメントを付けること |
| **squash merge** | 枝の commit を**1個にまとめて** `main` に入れる方式。履歴が読みやすくなる |
| **conflict（コンフリクト）** | 2人が**同じ行**を別々に直したとき、Git がどちらを採るか決められない状態 |

---

## ステップ1：ブランチを切って何か書く（10分）

```bash
git switch main
git pull origin main
git switch -c docs/git-practice-<自分の名前>     # 例: docs/git-practice-matsuda
```

> **`git switch -c` は「ブランチを新しく作って、そこに移る」。** `-c` は create。
> **ブランチ名の付け方**は [計画書 §8-1](../plan.md#s8-1)（`feat/` `fix/` `docs/` `exp/`）。今回は文書なので `docs/`。

**練習用のファイルを作ります。**

```bash
mkdir -p docs/notes
```

`docs/notes/git-practice-<自分の名前>.md` を作って、**なんでもいいので3行くらい書きます。** 例：

```markdown
# Git 練習メモ（<名前>）

- `git switch -c` でブランチを作った
- 分からなかったこと：
```

**いま自分がどこにいるか確認**：

```bash
git status            # 「On branch docs/git-practice-...」と出るはず
git branch            # * が付いているのが今いるブランチ
```

---

## ステップ2：commit して push する（10分）

```bash
git add docs/notes/git-practice-<自分の名前>.md
git status                    # 緑色で「new file:」と出れば add できている
git commit -m "docs: Git 練習メモを追加（<自分の名前>）"
git push -u origin docs/git-practice-<自分の名前>
```

> **`-u` は初回だけ必要。** 「このローカルブランチは origin のこのブランチに対応する」と覚えさせるオプションです。2回目以降は `git push` だけで通ります。

push すると、ターミナルに **PR を作る URL が表示されます。**

---

## ステップ3：PR を出す（15分）

表示された URL を開くか、GitHub のリポジトリページに出る **`Compare & pull request`** を押します。

**書くこと**（[計画書 §8-2](../plan.md#s8-2)）：

| 欄 | 書き方 |
|---|---|
| **タイトル** | commit メッセージと同じでよい |
| **本文** | **「何を」「なぜ」を1〜3段落。** 相手の専門外を前提に書く |

本文の例：

```
Git の練習として、branch → PR → レビュー → squash merge を1周する。

追加したのは docs/notes/ の練習メモ1本だけで、コードには影響しない。
main のブランチ保護（T04）を入れる前に、全員が PR の手順を通しておくのが目的。
```

**右側の `Labels` から `G9:ドキュメント` を付けてください**（[T06](T06-labels-and-board.md) が終わっていれば選べます。まだなら飛ばしてよい）。

---

## ステップ4：相手にレビューしてもらう（15分）

**PR の右上 `Reviewers` から相手を指定します。**

レビューする側がやること：

1. **`Files changed` タブを開く**（何が変わったかが行単位で見える）
2. 行の左の **`+` を押すとその行にコメントできる**
3. 右上の **`Review changes`** → **`Approve`** を選ぶ
4. **コメント欄に「この PR が何をしているか、自分の言葉で1〜3行」を書く**

---
**Finish your commentsでの項目の意味**
|項目|説明|
|---|---|
|Comment | 承認でも変更要求でもなく、単に感想やコメントだけを残す|
|Approve | 承認して、mergeできる状態にする（今、これが選ばれている）|
|Request changes |「このままではmergeしないでほしい」という意思表示。修正が必要な点を指摘するときに選ぶ|

---


> ⚠️ **「LGTM」だけの承認は禁止です**（[計画書 §8-2](../plan.md#s8-2)）。
> **読んでいないのに通すのを構造的に止めるためのルール**で、これは練習でも守ってください。

**練習として、レビューする側は1つコメントを付けてください。** 何でもいいです（「ここ typo」でも「読みました」でも）。コメントを受けた側は：

```bash
# 同じブランチのまま直して、もう1回 commit → push するだけ
git add -A
git commit -m "docs: レビュー指摘を反映"
git push               # -u は初回だけなので、もう要らない
```

**PR は自動で更新されます。** 新しく PR を出し直す必要はありません。**ここが一番よく誤解される点です。**

---

## ステップ5：squash merge する（5分）

1. PR のページ下部の **`Squash and merge`** を押す（[T04](T04-branch-protection.md) 後はこれしか出ません）
2. commit メッセージを確認して **`Confirm squash and merge`**
3. **`Delete branch`** を押す（GitHub 上の枝を消す。ローカルはまだ残っています）

**手元を片付ける**：

```bash
git switch main
git pull origin main                              # マージされた内容が降りてくる
git branch -D docs/git-practice-<自分の名前>       # ローカルの枝を消す（大文字の -D）
git branch                                        # main だけになっていれば OK
```

> ⚠️ **ここは `-d`（小文字）ではなく `-D`（大文字）です。**
> `-d` を打つと **`error: the branch '...' is not fully merged`** と言われて消せません。**壊れているのではありません。**
>
> **理由**：squash merge は、枝の commit を**そのまま取り込むのではなく、内容をまとめた新しい commit を1個作ります。**
> そのため Git から見ると「枝の commit は `main` に入っていない」ことになり、`-d`（安全な削除）が拒否されます。
> **内容は `main` に入っているので、`-D`（強制削除）で問題ありません。**

---

## ステップ6（余裕があれば）：コンフリクトを1回わざと起こす（15分）

**本番で必ず出会います。** 慌てないために1回見ておくと違います。

1. 2人が**同じファイルの同じ行**を、**別々のブランチ**で書き換える
2. 片方を先にマージする
3. もう片方で `git switch main && git pull && git switch <自分の枝> && git merge main`
4. **`CONFLICT` と出る。** 該当ファイルを開くと下のようになっている：

```
<<<<<<< HEAD
自分が書いた行
=======
相手が書いた行
>>>>>>> main
```

5. **`<<<<<<<` `=======` `>>>>>>>` の3行ごと消して、残したい内容だけにする**
6. `git add <ファイル>` → `git commit`

> ⚠️ **`git commit` を `-m` なしで打つと、エディタが開きます。** 既定のメッセージが入っているので、**そのまま保存して閉じるだけ**です。
> **vim なら** `:wq` と打って Enter。**nano なら** `Ctrl+O` → Enter → `Ctrl+X`。
> **エディタを開きたくなければ `git commit --no-edit`** でも同じことができます。

---

## 完了判定

- [ ] 自分の名前の練習メモが **`main` に入っている**（GitHub 上で `docs/notes/` を見て確認）
- [ ] **`main` 上の履歴で、その PR が1コミットにまとまっている**（squash が効いている）
- [ ] 相手からの **Approve コメントに「自分の言葉での説明1〜3行」が入っている**
- [ ] 手元で `git branch` が `main` だけになっている
- [ ] **`git switch -c` / `git push -u` / `git branch -D` を、手順を見ないで打てる**

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| **`error: the branch '...' is not fully merged`** | **squash merge の後は正常な反応です。** `-d` ではなく **`-D`** を使ってください（上のステップ5の注記） |
| `error: pathspec ... did not match` | ブランチ名の打ち間違い。`git branch -a` で一覧を見る |
| `Updates were rejected` | 相手が先に push している。`git pull --rebase` してから push |
| **間違えて `main` で作業してしまった（まだ commit していない）** | `git switch -c <新しい枝名>` と打つだけで、**変更を持ったまま枝に移れます。** その後 commit すれば OK |
| **間違えて `main` に commit してしまった** | **枝に移るだけでは `main` に commit が残ります**（あとで `git pull` したときに履歴が枝分かれします）。`git switch -c <新しい枝名>` で枝を作ってから、**`git switch main && git reset --hard origin/main` で `main` を戻す**。⚠️ **`reset --hard` は未コミットの変更を消す**ので、`git status` が clean であることを確認してから |
| commit を1個取り消したい | `git reset --soft HEAD~1`（変更は手元に残る）。`--hard` は変更ごと消えるので注意 |
| **何が起きているか分からなくなった** | `git status` と `git log --oneline -5` を貼って [Discuss.md](../../Discuss.md) で聞く。**自力で `--force` を試さないこと** |

---

## 終わったら

1. **詰まった点・学んだことを [`memo/`](../memo/) に1本残す**
2. [次にやること](../next.md) の T05 の状態を `✅ 完了（名前・日付）` に書き換える
3. **練習メモに「分からなかったこと」を書いて残してください。** 次に入る人向けの資料になります（[計画書 §3-7](../plan.md#s3-7)）
