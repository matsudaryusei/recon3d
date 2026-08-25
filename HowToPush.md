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


> ⚠️ **この手順は、[T04（`main` ブランチの保護）](docs/tasks/T04-branch-protection.md) を入れた時点で使えなくなります。**
> 以降は **ブランチ → PR → レビュー → merge** に変わります。手順は **[T05 Git の練習](docs/tasks/T05-git-practice.md)** にあります。
> **用語（ブランチ・PR・squash merge・conflict）は [用語集](docs/glossary.md) に1行ずつ。**

## gitへの反映方法
もし自分が編集する場合は、
```
git add .
git commit -m "更新内容(変更者の名前)"
git push origin main
```

リアルタイム同期ではないの、誰かが編集したら最新版を取得する必要がある
```
git pull origin main
```
で呼べるよ！