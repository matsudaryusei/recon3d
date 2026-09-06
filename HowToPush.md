# 4bitcom

## 概要
これは
@Hinatori8
@matsudaryusei
の共同プロジェクトです。H & M はイニシャルであり、実在する、人物 地名 団体とは一切関係ありません。

## 各ファイルの立ち位置と見方

**[docs/README.md](docs/README.md) にまとめてあります。** 迷ったらそこへ。

| 知りたいこと | 開くもの |
|---|---|
| 次に何をするか | [docs/next.md](docs/next.md) |
| 言葉の意味 | [docs/glossary.md](docs/glossary.md) |
| 仕様・日程 | [docs/plan.md](docs/plan.md) |
| なぜそう決めたか | [docs/decisions.md](docs/decisions.md) |


> ⚠️ **[T04（`main` ブランチの保護）](docs/tasks/T04-branch-protection.md) により、`main` への直接 `git push` は 2026-09-07 から禁止されています。**
> 以降は **ブランチ → PR → レビュー → merge** です。手順は **[T05 Git の練習](docs/tasks/T05-git-practice.md)** にあります。
> **用語（ブランチ・PR・squash merge・conflict）は [用語集](docs/glossary.md) に1行ずつ。**

## gitへの反映方法
`main` は保護されているため、直接 `git push origin main` はできません。自分が編集する場合は、ブランチを切って PR を出してください。

```bash
git switch main
git pull origin main
git switch -c feat/<何をするか>

# 編集する

git add .
git commit -m "更新内容(変更者の名前)"
git push -u origin feat/<何をするか>
```

GitHub で PR を作成し、レビュー後に **`Squash and merge`** でマージしてください。詳しい手順は [T05 Git の練習](docs/tasks/T05-git-practice.md) を参照。

リアルタイム同期ではないので、誰かが編集したら最新版を取得する必要がある
```
git pull origin main
```
で呼べるよ！