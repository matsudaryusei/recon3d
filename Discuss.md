#連絡場所

---

## 動機(※この節は削除されます)

Discordでチャンネルを作成して、話し合う事が良いですが、gitを見た人にはそのやりとりは伝わりません。
対面ではない場合で連絡をする場合はこちらを利用してください。

また、話し合いで決まった事や変更が行われたことは[開発ログ](doc/3d-reconstruction-progress-log.md)の方で言及する予定です。

次にこの連絡を介して不備があった場合はClaudeが返信するように組んであります。定期的に確認してください

---

### 08/17

from 関口 to 全員
logファイルを清書するときは詰まった点や工夫した点など誓しの振り返りを書くように事細かく冗長に書こうと思っています。
思い返せるように、個人が作成した範囲でメモを残しておいえてください

---

### 08/17

from Claude to 松田

`.gitattributes` と `pyproject.toml` / `uv.lock` を確認しました。Python 3.11 の固定（`>=3.11,<3.12`）は計画書 §7-2 のとおりで、`uv.lock` もコミットされています。ここは問題ありません。

**1点、`.gitattributes` が計画書 §7-3 の指定より短くなっています。**

いま:

```text
* text=auto
```

指定:

```text
* text=auto eol=lf
*.png binary
*.jpg binary
*.ply binary
*.obj binary
*.blend binary
```

`text=auto` だけでも改行の正規化は効きますが、`.blend` や `.ply` を置き始めたときに Git がテキストと誤判定して中身を壊す可能性が残ります。**実データを扱う前（W02 の合成データ生成より前）に追記しておいてください。**

**もう1点、次の作業への申し送りです。** `src/recon3d/` を作る前に、**`import recon3d` が通る設定を決めておく必要があります。** いまの `pyproject.toml` には `[build-system]` が無く、`uv.lock` が `source = { virtual = "." }` になっているため、ディレクトリを作っただけではテストから import できません。`[build-system]` を足すか、pytest 側に `pythonpath = ["src"]` を張るかの二択です。どちらでも構いませんが、**骨格を作るのと同じPRの中で決めてください。**
