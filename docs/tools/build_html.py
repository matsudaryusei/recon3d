#!/usr/bin/env python3
"""md ドキュメント一式を HTML 版（site/）に変換する。

    python3 docs/tools/build_html.py

- 出力はリポジトリ直下の `site/`。ディレクトリ構成を元のまま写すので、
  md 同士の相対リンク（`../plan.md#s12` など）はそのまま `.html` として通る。
- 入力は `docs/**/*.md` と、docs から参照されているルート直下の md。
"""

from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mdparse import Renderer  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "site"
ROOT_MD = ["README.md", "HowToPush.md"]

# トップページの並び順と説明。ここに無い md は「その他」に自動で入る。
INDEX: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("入口", "まずここから", [
        ("README.md", "プロジェクトの概要（公開用）"),
        ("docs/README.md", "道順・現在地・各文書の役割"),
        ("docs/next.md", "次にやること（タスク表）"),
    ]),
    ("引くための文書", "必要になったときだけ開く", [
        ("docs/plan.md", "計画書（仕様・手順・日程）"),
        ("docs/decisions.md", "決定記録（なぜそう決めたか）"),
        ("docs/glossary.md", "用語集"),
        ("docs/learning.md", "学びの入口（資料）"),
    ]),
    ("作業", "手を動かすとき", [
        ("docs/tasks/README.md", "タスク一覧"),
        ("HowToPush.md", "push の手順"),
    ]),
]


def sources() -> list[Path]:
    files = sorted((REPO / "docs").rglob("*.md"))
    files += [REPO / name for name in ROOT_MD if (REPO / name).exists()]
    return [f for f in files if ".venv" not in f.parts]


def rewrite_link(url: str, src: Path) -> str | None:
    """md 間リンクを html 間リンクに読み替える。外部 URL とアンカーは触らない。"""
    if url.startswith(("http://", "https://", "mailto:", "#")):
        return url
    path, _, frag = url.partition("#")
    if path.endswith("/"):  # `notes/` のようなディレクトリ指定
        path += "README.md"
    if path.endswith(".md"):
        path = path[:-3] + ".html"
    elif path:  # `.py` など site/ に出ないファイルはリンクにしない
        return None
    return path + (f"#{frag}" if frag else "")


def breadcrumb(rel: Path, depth: int) -> str:
    """上部バーのパンくず。同じ階層に README があるときだけ親をリンクにする。"""
    up = "../" * depth
    parts = [f'<a href="{up}index.html">ドキュメント</a>']
    if len(rel.parts) > 2:
        parent = html.escape(rel.parts[-2])
        has_readme = (REPO / rel.parent / "README.md").exists() and rel.name != "README.md"
        parts.append(
            f'<a href="README.html">{parent}/</a>' if has_readme else f"<span>{parent}/</span>"
        )
    return '<span class="sep">/</span>'.join(parts)


def toc(headings) -> str:
    if len(headings) < 3:
        return ""
    # 大見出しだけで十分な数がある長い文書は、小見出しを畳んで一覧性を優先する
    if sum(1 for h in headings if h.level == 2) >= 12:
        headings = [h for h in headings if h.level == 2]
    items = "".join(
        f'<li class="lv{h.level}"><a href="#{h.anchor}">{html.escape(h.text)}</a></li>'
        for h in headings
    )
    # 画面が狭いときは本文の上に来るので、折りたたみにして見出しを埋めないようにする
    return (
        '<details class="toc"><summary class="toc-title">目次</summary>'
        f"<ul>{items}</ul></details>"
    )


PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <nav class="crumbs">{crumbs}</nav>
    <span class="src">{src}</span>
  </div>
</header>
<div class="layout">
  {toc}
  <main class="page">
{body}
  </main>
</div>
<footer class="foot">
  <p>このページは <code>{src}</code> から自動生成しています。編集は md 側で。</p>
</footer>
</body>
</html>
"""

INDEX_PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>3D復元プロジェクト — ドキュメント</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="layout layout--index">
  <main class="page">
    <h1 class="index-title">3D復元プロジェクト<span>ドキュメント</span></h1>
    <p class="lead">md 版と同じ内容の HTML 版です。迷ったら
      <a href="docs/README.html">README</a> に戻ってください。</p>
{sections}
  </main>
</div>
<footer class="foot">
  <p><code>python3 docs/tools/build_html.py</code> で再生成します。</p>
</footer>
</body>
</html>
"""


def build_index(pages: dict[str, str]) -> str:
    listed: set[str] = set()
    blocks = []
    for name, note, entries in INDEX:
        cards = []
        for src, desc in entries:
            if src not in pages:
                continue
            listed.add(src)
            p = Path(src)
            # `tasks/README` と `notes/README` が同じ名前で並ばないようにする
            name = f"{p.parent.name}/" if p.stem == "README" and p.parent.name != "docs" else p.stem
            cards.append(
                f'<a class="card" href="{pages[src]}">'
                f'<span class="card-title">{html.escape(name)}</span>'
                f'<span class="card-desc">{html.escape(desc)}</span></a>'
            )
        if cards:
            blocks.append(
                f'<section class="group"><h2>{name}'
                f'<span class="group-note">{note}</span></h2>'
                f'<div class="cards">{"".join(cards)}</div></section>'
            )

    rest = sorted(src for src in pages if src not in listed)
    if rest:
        links = "".join(
            f'<li><a href="{pages[src]}">'
            f'{html.escape(src.removeprefix("docs/").removesuffix(".md"))}</a></li>'
            for src in rest
        )
        blocks.append(
            '<section class="group"><h2>その他<span class="group-note">'
            f'個別タスク・内部資料</span></h2><ul class="plain">{links}</ul></section>'
        )
    return "\n".join(blocks)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(Path(__file__).parent / "style.css", OUT / "assets" / "style.css")

    pages: dict[str, str] = {}
    for src in sources():
        rel = src.relative_to(REPO)
        dest = OUT / rel.with_suffix(".html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        depth = len(rel.parts) - 1

        renderer = Renderer(link_rewriter=lambda url, s=src: rewrite_link(url, s))
        doc = renderer.render(src.read_text(encoding="utf-8"))
        title = doc.title or rel.stem

        dest.write_text(
            PAGE.format(
                title=html.escape(title),
                up="../" * depth,
                crumbs=breadcrumb(rel, depth),
                src=html.escape(rel.as_posix()),
                toc=toc(doc.headings),
                body=doc.html,
            ),
            encoding="utf-8",
            newline="\n",
        )
        pages[rel.as_posix()] = rel.with_suffix(".html").as_posix()

    (OUT / "index.html").write_text(
        INDEX_PAGE.format(sections=build_index(pages)), encoding="utf-8", newline="\n"
    )
    print(f"{len(pages)} 件を {OUT.relative_to(REPO)}/ に出力しました。")
    print(f"開く: file://{OUT}/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
