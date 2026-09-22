# recon3d — 多視点画像とシルエットを統合した3D形状復元

[![CI](https://github.com/matsudaryusei/recon3d/actions/workflows/ci.yml/badge.svg)](https://github.com/matsudaryusei/recon3d/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

静止画20枚から物体の3D形状を復元し、**その精度を数値で測る**2人の共同開発プロジェクトです。

2つの復元手法を組み合わせて、片方の弱点をもう片方で埋めます。

| 手法 | 苦手な条件 |
|---|---|
| ① 多視点復元（特徴点 → 三角測量 → バンドル調整） | **無地でテクスチャのない面**。特徴点が取れず、点群に穴が空く |
| ④ シルエット復元（Visual Hull・ボクセル彫刻） | **凹んだ形状**。外から見えない窪みは削れない |

**反復解法・最適化・幾何アルゴリズムは自作します**（ここがプロジェクトの芯です）。行列積・I/O・画像前処理はライブラリに任せます。リアルタイム描画やゲームエンジンとの連携は扱いません（→ [計画書 §3-8](docs/plan.md#s3-8)）。

## 現在の状態

**開発中です（全18週・2026-08 着工）。** 着工前の準備（座標系・`cameras.json` の仕様・CI・運用ルール・合成データの元モデルの選定）が終わり、Phase 0（OpenCV で一直線に通す／Blender で合成データを作る）に入ったところです。

- 何ができたら完成とするか：[計画書 §12 撤退ライン](docs/plan.md#s12)（目標は L3：統合パイプラインと比較実験 E1〜E7）
- 評価実験の設計：[計画書 §11](docs/plan.md#s11)

## セットアップ

[uv](https://docs.astral.sh/uv/) を使います。Python は 3.11 に固定しています（→ [計画書 §7-2](docs/plan.md#s7-2)）。

```bash
git clone https://github.com/matsudaryusei/recon3d.git
cd recon3d
uv sync
uv run pytest
```

Blender 側のスクリプト（`tools/blender_*.py`）は Blender 5.0.x に同梱の Python で動かし、`bpy` と `numpy` だけに依存させています（→ [計画書 §7-4](docs/plan.md#s7-4)）。

```bash
blender -b -P tools/hello_bpy.py
```

## ディレクトリ

```
src/recon3d/      本体（io / geometry / solvers / vision / fusion / mesh / viz）
tests/            pytest（Ubuntu と Windows の CI で実行）
tools/            Blender スクリプトなどの補助ツール
docs/             計画書・決定記録・手順書・メモ
site/             docs の HTML 版（docs/tools/build_html.py で生成）
```

## ドキュメント

| 知りたいこと | 開くもの |
|---|---|
| 全体の現在地と道順 | [docs/README.md](docs/README.md) |
| 仕様・日程 | [docs/plan.md](docs/plan.md)（計画書） |
| なぜそう決めたか | [docs/decisions.md](docs/decisions.md)（決定記録） |
| 次にやること | [docs/next.md](docs/next.md) |
| 用語 | [docs/glossary.md](docs/glossary.md) |
| 開発への参加手順（ブランチ → PR） | [HowToPush.md](HowToPush.md) |

## 使用している3Dモデル

合成データの元モデルは、どれも [Poly Haven](https://polyhaven.com/) の CC0 モデルです（選定の経緯は [docs/notes/model-candidates.md](docs/notes/model-candidates.md)）。モデル本体はリポジトリに含めません。

- 主データ：[Ceramic Pot](https://polyhaven.com/a/ceramic_pot)（Aron Łyczek, CC0）
- 副データ：[Food Lychee 01](https://polyhaven.com/a/food_lychee_01)（Oliver Harries, CC0）

## 作者

[@Hinatori8](https://github.com/Hinatori8) ・ [@matsudaryusei](https://github.com/matsudaryusei)

## ライセンス

[MIT](LICENSE)
