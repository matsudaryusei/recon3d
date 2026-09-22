"""Markdown → HTML 変換器（依存ライブラリなし）。

このプロジェクトの md で実際に使われている記法だけを対象にしている:
見出し / 表 / 箇条書き（ネスト・チェックボックス） / 番号付き / 引用 /
コードブロック / 水平線 / 強調・打ち消し・インラインコード / リンク /
`<a id="...">` アンカーと `<br>`。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- インライン

CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]\[]*)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)
STRIKE_RE = re.compile(r"~~(.+?)~~", re.S)
ITALIC_RE = re.compile(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)")
ANCHOR_RE = re.compile(r"<a id=\"([^\"]+)\"></a>")
BR_RE = re.compile(r"<br\s*/?>")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Inline:
    """インライン記法を HTML にする。link_rewriter で URL を差し替える。"""

    def __init__(self, link_rewriter=None):
        self.rewrite = link_rewriter or (lambda url: url)

    def __call__(self, text: str) -> str:
        slots: list[str] = []

        def stash(html: str) -> str:
            slots.append(html)
            return f"\x00{len(slots) - 1}\x00"

        # 先に「中身を触ってはいけないもの」を退避する
        text = CODE_RE.sub(lambda m: stash(f"<code>{esc(m.group(1))}</code>"), text)
        text = ANCHOR_RE.sub(lambda m: stash(f'<a id="{m.group(1)}"></a>'), text)
        text = BR_RE.sub(lambda m: stash("<br>"), text)

        text = esc(text)
        text = LINK_RE.sub(self._link, text)
        text = BOLD_RE.sub(r"<strong>\1</strong>", text)
        text = STRIKE_RE.sub(r"<del>\1</del>", text)
        text = ITALIC_RE.sub(r"<em>\1</em>", text)

        return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m.group(1))], text)

    def _link(self, m: re.Match) -> str:
        label, url = m.group(1), self.rewrite(m.group(2))
        if url is None:  # site/ に出力されないファイルへのリンクは文字だけ残す
            return label
        external = url.startswith(("http://", "https://"))
        attrs = ' target="_blank" rel="noopener"' if external else ""
        cls = ' class="ext"' if external else ""
        return f'<a href="{url}"{cls}{attrs}>{label}</a>'


# ------------------------------------------------------------------ ブロック

FENCE_RE = re.compile(r"^```(\w*)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HR_RE = re.compile(r"^\s{0,3}(-{3,}|\*{3,}|_{3,})\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TASK_RE = re.compile(r"^\[([ xX])\]\s+(.*)$")
ANCHOR_LINE_RE = re.compile(r"^<a id=\"([^\"]+)\"></a>\s*$")
TABLE_DELIM_RE = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")


@dataclass
class Heading:
    level: int
    text: str
    anchor: str


@dataclass
class Document:
    html: str
    title: str
    headings: list[Heading] = field(default_factory=list)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*~\[\]()#|]", "", text).strip().lower()
    text = re.sub(r"[\s/]+", "-", text)
    return re.sub(r"[^\w-]", "", text, flags=re.UNICODE) or "section"


class Renderer:
    def __init__(self, link_rewriter=None):
        self.inline = Inline(link_rewriter)
        self.headings: list[Heading] = []
        self.title = ""
        self.used_ids: set[str] = set()

    # -- 公開 API ---------------------------------------------------------
    def render(self, markdown: str) -> Document:
        lines = markdown.replace("\r\n", "\n").split("\n")
        html = self._blocks(lines)
        return Document(html=html, title=self.title, headings=self.headings)

    # -- 本体 -------------------------------------------------------------
    def _blocks(self, lines: list[str]) -> str:
        out: list[str] = []
        i = 0
        pending_anchor: str | None = None

        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            m = ANCHOR_LINE_RE.match(line.strip())
            if m:
                pending_anchor = m.group(1)
                i += 1
                continue

            m = FENCE_RE.match(line.strip())
            if m:
                lang, body, i = m.group(1), [], i + 1
                while i < len(lines) and not FENCE_RE.match(lines[i].strip()):
                    body.append(lines[i])
                    i += 1
                i += 1
                cls = f' class="lang-{lang}"' if lang else ""
                out.append(f"<pre><code{cls}>{esc(chr(10).join(body))}</code></pre>")
                continue

            m = HEADING_RE.match(line)
            if m:
                out.append(self._heading(m, pending_anchor))
                pending_anchor = None
                i += 1
                continue

            if HR_RE.match(line):
                out.append("<hr>")
                i += 1
                continue

            if line.lstrip().startswith(">"):
                block, i = self._collect(lines, i, lambda s: s.lstrip().startswith(">"))
                inner = [re.sub(r"^\s*>\s?", "", s) for s in block]
                out.append(f"<blockquote>{self._sub(inner)}</blockquote>")
                continue

            if line.startswith("|") and i + 1 < len(lines) and TABLE_DELIM_RE.match(lines[i + 1]):
                html, i = self._table(lines, i)
                out.append(html)
                continue

            if LIST_RE.match(line):
                html, i = self._list(lines, i)
                out.append(html)
                continue

            block, i = self._collect(lines, i, self._is_paragraph_line)
            text = "\n".join(s.strip() for s in block)
            out.append(f"<p>{self.inline(text)}</p>")

        return "\n".join(out)

    def _sub(self, lines: list[str]) -> str:
        """引用の中身など、入れ子のブロックを描画する（見出し収集は共有）。"""
        return self._blocks(lines)

    @staticmethod
    def _collect(lines, i, keep):
        block = []
        while i < len(lines) and lines[i].strip() and keep(lines[i]):
            block.append(lines[i])
            i += 1
        return block, i

    @staticmethod
    def _is_paragraph_line(line: str) -> bool:
        s = line.strip()
        return not (
            s.startswith(("|", ">", "```"))
            or HEADING_RE.match(line)
            or HR_RE.match(line)
            or LIST_RE.match(line)
            or ANCHOR_LINE_RE.match(s)
        )

    def _heading(self, m: re.Match, pending_anchor: str | None) -> str:
        level, raw = len(m.group(1)), m.group(2).strip()
        inner_anchor = ANCHOR_RE.search(raw)
        anchor = pending_anchor or (inner_anchor.group(1) if inner_anchor else slugify(raw))
        if anchor in self.used_ids:
            n = 2
            while f"{anchor}-{n}" in self.used_ids:
                n += 1
            anchor = f"{anchor}-{n}"
        self.used_ids.add(anchor)

        html = self.inline(ANCHOR_RE.sub("", raw))
        if level == 1 and not self.title:
            self.title = re.sub(r"<[^>]+>", "", html)
        if 2 <= level <= 3:
            self.headings.append(Heading(level, re.sub(r"<[^>]+>", "", html), anchor))

        link = f'<a class="hash" href="#{anchor}" aria-label="このセクションへのリンク">#</a>'
        return f'<h{level} id="{anchor}">{html}{link}</h{level}>'

    def _table(self, lines, i):
        def cells(row: str) -> list[str]:
            row = row.strip()
            if row.startswith("|"):
                row = row[1:]
            if row.endswith("|"):
                row = row[:-1]
            return [c.strip() for c in row.split("|")]

        header = cells(lines[i])
        aligns = []
        for spec in cells(lines[i + 1]):
            left, right = spec.startswith(":"), spec.endswith(":")
            aligns.append("center" if left and right else "right" if right else "left")
        i += 2

        body = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            body.append(cells(lines[i]))
            i += 1

        def cell(tag: str, text: str, idx: int) -> str:
            align = aligns[idx] if idx < len(aligns) else "left"
            style = f' style="text-align:{align}"' if align != "left" else ""
            return f"<{tag}{style}>{self.inline(text)}</{tag}>"

        head = "".join(cell("th", c, n) for n, c in enumerate(header))
        rows = "".join(
            "<tr>" + "".join(cell("td", c, n) for n, c in enumerate(r)) + "</tr>" for r in body
        )
        empty = " table--headless" if not any(c.strip() for c in header) else ""
        return (
            f'<div class="table-wrap"><table class="md{empty}">'
            f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>",
            i,
        )

    def _list(self, lines, i):
        items = []  # (indent, ordered, [content lines])
        while i < len(lines):
            m = LIST_RE.match(lines[i])
            if m:
                indent = len(m.group(1).expandtabs(4))
                ordered = not m.group(2)[0] in "-*+"
                items.append([indent, ordered, [m.group(3)]])
                i += 1
                continue
            if items and lines[i].strip() and not HEADING_RE.match(lines[i]) and lines[i][:1] in " \t":
                items[-1][2].append(lines[i].strip())  # 継続行
                i += 1
                continue
            break
        html, _ = self._render_items(items, 0)
        return html, i

    def _render_items(self, items, pos, indent=None):
        """同じ階層の項目を並べ、深い項目は再帰でネストする。"""
        if indent is None:
            indent = items[pos][0]
        ordered = items[pos][1]
        html = []
        while pos < len(items) and items[pos][0] >= indent:
            if items[pos][0] > indent:
                nested, pos = self._render_items(items, pos, items[pos][0])
                html[-1] += nested
                continue
            text = " ".join(items[pos][2])
            task = TASK_RE.match(text)
            cls, prefix = "", ""
            if task:
                checked = " checked" if task.group(1).lower() == "x" else ""
                cls = ' class="task"'
                prefix = f'<input type="checkbox" disabled{checked}> '
                text = task.group(2)
            html.append(f"<li{cls}>{prefix}{self.inline(text)}")
            pos += 1
        tag = "ol" if ordered else "ul"
        return f"<{tag}>" + "".join(f"{h}</li>" for h in html) + f"</{tag}>", pos
