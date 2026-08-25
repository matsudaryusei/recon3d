# T04 — `main` ブランチを保護する

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G7 テスト・CI** |
| 目安時間 | **30分**（画面操作は10分。残りは手順を読む時間と、最後の動作確認） |
| 前提 | ① **[T03 CI の雛形](T03-ci-workflow.md) がマージ済み**（そうしないと選ぶチェック項目が出てきません）<br>② **[T05 Git の練習](T05-git-practice.md) を全員が済ませていること** ← **ここを先にやらないと、保護した瞬間に全員が何もできなくなります** |
| 作るもの | GitHub 上の設定（ファイルは増えません） |
| 仕様の出どころ | [計画書 §8-1](../plan.md#s8-1) ／ [D-22](../decisions.md#d-22) |

---

> **先に読むもの**：特にありません。**画面の操作だけです。**
> `ブランチ保護`・`squash merge`・`PR` の意味は [用語集](../glossary.md) にあります。

## なぜやるのか

**いま `main` に直接 push できてしまいます。** [HowToPush.md](../../HowToPush.md) に書いてある `git push origin main` がそのまま通る状態です。

これを止める理由は2つ：

1. **レビューなしで壊れたコードが入るのを防ぐ**
2. **PR の履歴が残る。** 就活で見せるときに「どう議論して決めたか」が読める形で残ります（[計画書 §8-3](../plan.md#s8-3)）

> ⚠️ **設定した瞬間から `git push origin main` は失敗します。** これは正常です。**全員に事前に伝えてください**（[Discuss.md](../../Discuss.md) に1行）。以後は必ずブランチ → PR です。やり方は [T05 Git の練習](T05-git-practice.md) にあります。

---

## ステップ1：設定画面を開く

1. GitHub でリポジトリを開く
2. 上部の **`Settings`**（歯車）
3. 左メニューの **`Rules` → `Rulesets`**（古い画面では **`Branches`**）
4. **`New ruleset` → `New branch ruleset`**（古い画面では `Add branch protection rule`）

---

## ステップ2：設定する

### Ruleset の画面の場合

| 項目 | 設定する値 |
|---|---|
| **Ruleset Name** | `protect-main` |
| **Enforcement status** | **`Active`** ← ここを忘れると設定が効きません |
| **Target branches** | `Add target` → `Include default branch`（＝ `main`） |

**Rules のチェックボックス**：

| チェックする | 意味 |
|---|---|
| ✅ **Restrict deletions** | `main` を消せなくする |
| ✅ **Block force pushes** | 履歴の改変（`push --force`）を禁止する |
| ✅ **Require a pull request before merging** | **直 push を禁止する。これが本命** |
| ↳ **Required approvals** | **いまは `0`。W03 から `1` に上げる**（[計画書 §8-1](../plan.md#s8-1)。全員が Git に慣れるまでは approve 必須にしない） |
| ✅ **Require status checks to pass** | CI が緑でないとマージできなくする |
| ↳ `Add checks` で選ぶもの | **`pytest (ubuntu-latest)`** と **`pytest (windows-latest)`** の2つ |

**`Create` を押して保存。**

> **`Required approvals` を `0` にしても「PR は必須」は効きます。** 「PR を出す」という手続きだけ強制して、承認は後から必須化する形です。

### 古い `Branches` 画面の場合

`Branch name pattern` に `main` と入れて、下記にチェック：

- `Require a pull request before merging`（`Required approvals` は `0`）
- `Require status checks to pass before merging` → 検索欄で `pytest` と打って2つとも選ぶ
- `Do not allow bypassing the above settings` は**外したまま**（管理者が緊急時に通せる余地を残す）

> ⚠️ **これを外しておくと、リポジトリの管理者は直 push できてしまいます**（それが「バイパスの余地を残す」の意味です）。
> **つまり、この設定をした本人が下の完了判定をやっても push が拒否されません。** 壊れているわけではありません。
> **確かめ方は2つ**：管理者でないメンバーに試してもらうか、**確認の間だけ `Do not allow bypassing` にチェックを入れて、終わったら外す**。

---

## ステップ3：マージ方法を squash に統一する

**別の画面です。**

1. `Settings` → **`General`**
2. 下にスクロールして **`Pull Requests`** の枠
3. **`Allow squash merging` だけチェックを残し、`Allow merge commits` と `Allow rebase merging` のチェックを外す**

**理由**：1つの PR が `main` 上で1コミットになり、履歴が読めるものになります（[計画書 §8-1](../plan.md#s8-1)）。public 化後に読まれる前提です。

---

## 完了判定

**実際に破れないことを確かめます。**

> ⚠️ **最初に必ず `git status` を見てください。**
> 後で `git reset --hard` を使います。これは**未コミットの変更を問答無用で消します。**
> **`nothing to commit, working tree clean` と出ていないときは、この確認をやってはいけません。**
> 先に自分の作業を commit するか、`git switch -c wip/待避` で別のブランチに逃がしてから戻ってきてください。

```bash
git switch main
git pull origin main
git status                       # ← 「nothing to commit, working tree clean」を確認してから次へ
```

**確認できたら、使い捨てのファイルを1つだけ作って push を試します**（既存のファイルは触りません）。

```bash
echo "branch protection test" > protection-test.txt
git add protection-test.txt      # このファイルだけを対象にする（-a は使わない）
git commit -m "test: ブランチ保護の確認（これは push に失敗するのが正常）"
git push origin main
```

- [ ] **push が拒否される**（`protected branch hook declined` のようなメッセージが出る）

確認できたら**きれいに戻します**：

```bash
git reset --hard origin/main     # いま作ったテスト commit を取り消す
rm -f protection-test.txt        # 残っていたら消す
git status
```

- [ ] `git status` が `nothing to commit, working tree clean` になる
- [ ] `protection-test.txt` が残っていない
- [ ] リポジトリの `Settings` → `Rules` に `protect-main` が **`Active`** で並んでいる
- [ ] `Settings` → `General` → `Pull Requests` で **`Allow squash merging` だけ**が有効

---

## つまずいたら

| 症状 | 対処 |
|---|---|
| `Add checks` に `pytest` が出てこない | **[T03](T03-ci-workflow.md) がまだマージされていないか、1度も CI が走っていません。** 一度 CI を走らせると候補に出てきます |
| push が拒否されない | `Enforcement status` が `Disabled` のままの可能性。`Active` にしてください |
| **自分（管理者）だけ通ってしまう** | Ruleset なら `Bypass list` に自分が入っていないか確認。**旧 `Branches` 画面なら `Do not allow bypassing the above settings` が外れているのが原因**で、これは仕様どおりです（上の注記） |
| **間違えて `git reset --hard` した／作業が消えた** | **commit 済みなら `git reflog` で戻せます。** `git reflog` で戻りたい行の番号を見て `git reset --hard HEAD@{数字}`。**一度も commit していない変更は戻せません**（だから上で `git status` を確認させています）。落ち着いて相談してください |

---

## 終わったら

> ⚠️ **ここから先は `git push origin main` が使えません。** いま自分で禁止したところです。
> **下の文書の修正は、必ずブランチを切って PR で入れてください。** 手順が不安なら [T05](T05-git-practice.md) を見ながらで構いません。

**まず告知します**（これだけは急ぎなので、先に）。

1. **[Discuss.md](../../Discuss.md) に1行**：「`main` への直 push を禁止しました。**今後はブランチ → PR です。** やり方は `docs/tasks/T05-git-practice.md`」

**次に、古くなる記述を PR で直します。**

```bash
git switch main
git pull origin main
git switch -c docs/t04-followup
```

2. **[HowToPush.md](../../HowToPush.md)** の `git push origin main` の記述 — 直すか、[T05](T05-git-practice.md) へのリンクを足す
3. **[進捗ログ](../progress.md)** の今週の表に **G7 の行**を1行
4. **[次にやること](../next.md)** の T04 の状態を `✅ 完了` に

```bash
git add -A
git commit -m "docs: main のブランチ保護に伴う記述の更新"
git push -u origin docs/t04-followup
```

**GitHub で PR を作り、`Squash and merge` でマージ。** これが**保護後の最初の PR** になります。

> 💡 **1・2 を Discuss.md でやるのも PR になります。** 告知が遅れて困るようなら、**先に口頭かチャットで伝えてから** PR を出してください。
