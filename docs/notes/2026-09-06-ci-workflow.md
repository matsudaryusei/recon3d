# CI（GitHub Actions）の雛形を置いた（2026-09-06・PR #6）

**きっかけ**: [T03 手順書](../tasks/T03-ci-workflow.md)。3台（mac / Windows / Ubuntu）で手動で `uv run pytest` を回していたのを、GitHub Actions に肩代わりさせる。

## やったこと

- `feat/ci-workflow` を切って `.github/workflows/ci.yml` を1本追加しただけ。中身は手順書のコピペそのまま。
- PR を出す → PR ページ下部に `pytest (ubuntu-latest)` と `pytest (windows-latest)` の2チェックが出る → 2〜3分で両方緑 → `Squash and merge` でマージ。

## 分かったこと

- **`astral-sh/setup-uv@v5` はそのまま通った。** 手順書が警告していた「見つからなければ `@v3` に下げる」は不要だった。降格していないので PR への理由書きも不要。
- **`setup-uv` は Python を入れない。** 次の `uv sync` が `.python-version`（3.11.13）を見て自動で用意する。ログの `uv run python -V` で `Python 3.11.13` が出ることを確認した。
- **`fail-fast: false` が効いて、片方が落ちてももう片方は最後まで回る。** どっちの OS で落ちたか分かるので必須。今回は両方緑だったが、その挙動は PR の実行結果で確認できた。
- **`enable-cache: true` で2回目以降が速い。** 初回 PR は約32秒、マージ後の main への push は約36秒（キャッシュヒット）。Windows ランナーは消費が2倍で数えられるが、この規模なら Free 枠で問題にならない。
- テスト数は現状 `10 passed`（[T01](../tasks/T01-pairpro1-io.md) の `tests/test_conventions.py` が入っているため）。手順書の「1 passed」は T01 前の想定。
- **Blender 依存テスト（`tools/blender_*.py`）は CI から外している。** GitHub の実行環境に Blender が無いため。手元確認とする（[D-24](../decisions.md#d-24)）。

## つまずいた点

特になし。手順書どおりで一発で通った。改行コード（`.gitattributes`）まわりの Windows 差分も出なかった。

## 次に活かすこと

- **これで [T04 ブランチ保護](../tasks/T04-branch-protection.md) の前提の片方が済んだ。** 残りは [T05 Git 練習](../tasks/T05-git-practice.md) を全員が1周すること。T04 で `main` を保護すると `git push origin main` が使えなくなるので、PR 手順を知らないまま保護しないこと。
- 今後テストが増えたら CI の実行時間も伸びる。遅くなってきたら `uv sync` のキャッシュキーや対象 OS を見直す。
- **CI バッジはまだ付けていない。** [D-24](../decisions.md#d-24) は「バッジ付きリポジトリは印象が違う」としているが、貼り先のトップ README がまだ無い。public 化（[T10](../tasks/T10-read-scope.md) 後）にあわせて README を用意するときに一緒に貼る。

## 参考

- [T03 手順書](../tasks/T03-ci-workflow.md) ／ [計画書 §9-2](../plan.md#s9-2) ／ [D-24](../decisions.md#d-24)
- 実行結果: リポジトリの Actions タブ（`CI` ワークフロー、run #34047751329 が初回 PR、#34048303042 が main への push）
