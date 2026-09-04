# T03 — CI（GitHub Actions）の雛形を置く

[← 次にやること一覧に戻る](../next.md)

| | |
|---|---|
| ジャンル | **G7 テスト・CI**（[計画書 §3-3](../plan.md#s3-3)） |
| 目安時間 | 1時間 |
| 前提 | なし（G6 の骨格が push 済みであること。→ 済） |
| 作るもの | `.github/workflows/ci.yml` |
| 仕様の出どころ | [計画書 §9-2](../plan.md#s9-2) ／ [D-24](../decisions.md#d-24) |

---

> **先に読むもの**：特にありません。**下の手順をそのまま打てば通ります。**
> 設定ファイルの文法まで知りたくなったら → [学びの入口 G9](../learning.md) の GitHub Actions。**用語は [用語集](../glossary.md)。**

## なぜやるのか

**「自分の PC では動くのに、相手の PC では落ちる」を自動で見つけるためです。**

いまは3台（mac / Windows / Ubuntu）で手で `uv run pytest` を流して確認しました（8/24）。**これを毎回手でやるのは続きません。** GitHub Actions に肩代わりさせます。

**Windows と Ubuntu の2つで回します**（[D-24](../decisions.md#d-24)）。mac を入れないのは、**改行コードとパス区切りの事故は Windows で出る**からで、mac 固有の事故は今のところ想定していないためです。

> **Blender を使うテスト（`tools/blender_*.py`）は CI から外します。** GitHub の実行環境に Blender が無いためで、これは手元での確認とします。

---

## ステップ1：ブランチを切る

```bash
git switch main
git pull origin main
git switch -c feat/ci-workflow
```

---

## ステップ2：ファイルを作る

```bash
mkdir -p .github/workflows
```

`.github/workflows/ci.yml` を作り、**下をそのまま貼ってください。**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    name: pytest (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      - name: uv をインストール
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: 依存をインストール
        run: uv sync

      - name: Python のバージョンを表示（3.11.13 のはず）
        run: uv run python -V

      - name: テストを実行
        run: uv run pytest -v
```

### 各行が何をしているか

| 行 | 意味 |
|---|---|
| `on: push: branches: [main]` | `main` に入ったときに回す |
| `on: pull_request` | **PR を出したときに回す。** これが本命（マージ前に落ちてくれる） |
| `fail-fast: false` | **片方が落ちても、もう片方を最後まで回す。** どっちのOSで落ちたかを知りたいので必須 |
| `matrix: os: [...]` | Ubuntu と Windows で同じことを2回やる |
| `astral-sh/setup-uv@v5` | **`uv` を入れるだけ**の公式アクション。**Python はここでは入りません**（次の `uv sync` が `.python-version` を見て 3.11.13 を自動で用意します） |
| `enable-cache: true` | 依存のダウンロードをキャッシュする。2回目以降が速くなる |
| `uv sync` | `uv.lock` のとおりに環境を作る。**プロジェクト自身も editable install される**（[計画書 §6-3](../plan.md#s6-3)） |
| `uv run pytest -v` | テストを実行。`-v` はどのテストが通ったか一覧で出す |

> ⚠️ **`astral-sh/setup-uv@v5` が「見つからない」と言われたら、`@v3` に下げてください。** [計画書 §9-2](../plan.md#s9-2) の骨子は `@v3` で書かれています。新しい方から試して、駄目なら下げるだけです。**下げた場合は理由を PR に1行書いてください。**

---

## ステップ3：push して動くか見る

```bash
git add .github/workflows/ci.yml
git commit -m "ci: GitHub Actions で Ubuntu と Windows の pytest を回す"
git push -u origin feat/ci-workflow
```

GitHub 上で **PR を作成**します。作った直後に **PR の下の方に CI の実行状況が出ます。**

- **`Details` を押すとログが読めます。** どのステップで落ちたかが行単位で分かります
- 2〜3分で終わります

---

## 完了判定

- [ ] PR のページに **`pytest (ubuntu-latest)` と `pytest (windows-latest)` の2つ**が出ている
- [ ] **両方が緑（✅）になっている**
- [ ] ログの `uv run python -V` が **`Python 3.11.13`** と出ている
- [ ] ログの最後が **`1 passed`**（[T01](T01-pairpro1-io.md) が先に入っていればもっと多い）

**緑になったらマージしてください。**

> ⚠️ **マージボタンの右のプルダウンから `Squash and merge` を選んでください。**
> squash 以外を無効にするのは [T04 のステップ3](T04-branch-protection.md) で、**まだ済んでいません。**
> いまボタンをそのまま押すと、既定の `Create a merge commit` になります（[計画書 §8-1](../plan.md#s8-1) は squash に統一と決めています）。

---

## つまずいたら

| 症状 | 原因と対処 |
|---|---|
| Windows だけ落ちる／改行に関する差分が出る | `.gitattributes` が効いていない可能性。`git add --renormalize .` を1回流して差分を見る（[計画書 §7-3](../plan.md#s7-3)） |
| `error: Failed to build ...` / `Failed to prepare distributions` | `pyproject.toml` の `packages = ["src/recon3d"]` が消えていないか確認（[計画書 §6-3](../plan.md#s6-3)） |
| `no tests ran` / exit code 5 | `tests/` が push されていない。`git ls-files tests` で確認 |
| Actions のタブに何も出ない | リポジトリの **Settings → Actions → General** で Actions が無効になっていないか確認 |
| 課金が心配 | **public リポジトリは無料。** private でも Free プランに月2000分の枠があります。⚠️ **Windows ランナーは消費が2倍で数えられる**ので、1回あたり「Ubuntu 3分 + Windows 3分×2 = 約9分」の計算になります。それでも週に何十回も回さない限り枠内です |

---

## 終わったら

1. **詰まった点・学んだことを [`memo/`](../memo/) に1本残す**
2. [次にやること](../next.md) の T03 の状態を `✅ 完了` に書き換える
3. **次は [T04 `main` ブランチの保護](T04-branch-protection.md) ですが、その前に [T05 Git の練習](T05-git-practice.md) を全員が済ませてください。**
   T04 で `main` を保護すると `git push origin main` が使えなくなります。**PR の手順を知らないまま保護すると、全員が何もできなくなります**
