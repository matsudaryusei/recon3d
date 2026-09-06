# main ブランチを保護した（2026-09-07）

**きっかけ**: [T04 手順書](../tasks/T04-branch-protection.md)。[T03](../tasks/T03-ci-workflow.md) の CI 導入が済んだので、`main` への直 push を止めて PR 必須にする。

## やったこと

- GitHub の `Settings → Rules → Rulesets` で `protect-main` という Ruleset を作成し、`Enforcement status` を `Active` に設定。対象は default branch（`main`）。
- チェックした項目：Restrict deletions／Block force pushes／Require a pull request before merging（Required approvals は `0`）／Require status checks to pass（`pytest (ubuntu-latest)` と `pytest (windows-latest)` の2つを選択）。
- `Settings → General → Pull Requests` で `Allow squash merging` のみ有効にし、`Allow merge commits` と `Allow rebase merging` を無効化。
- 完了判定として `protection-test.txt` を1つ作って `git push origin main` を試し、拒否されることを確認してから `git reset --hard origin/main` で作業ツリーを戻した。

## 分かったこと

- 手順書どおりに進めるだけで一発で完了した。
- push を拒否されると `protected branch hook declined` のようなメッセージが実際に出ることを確認できた。
- `Required approvals` を `0` のままにしても「PR を必須にする」効果はそのまま効く。承認必須化（`1` への引き上げ）は全員が Git に慣れてから（W03 以降）に行う予定（[計画書 §8-1](../plan.md#s8-1)）。

## つまずいた点

特になし。手順書通りで完了した。

## 次に活かすこと

- **これで `main` への直接 push はできなくなった。** 以後の変更は必ずブランチ → PR で行うこと（[T05 Git の練習](../tasks/T05-git-practice.md)）。
- [Discuss.md](../../Discuss.md) で告知済み。[HowToPush.md](../../HowToPush.md) の手順も PR フローに合わせて更新した。
- `Required approvals` を `1` に上げるタイミングは、[計画書 §8-1](../plan.md#s8-1) を見て判断する。

## 参考

- [T04 手順書](../tasks/T04-branch-protection.md) ／ [計画書 §8-1](../plan.md#s8-1) ／ [D-22](../decisions.md#d-22)
