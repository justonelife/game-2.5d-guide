#!/usr/bin/env python3
"""Render the game-2.5d-guide markdown docs into a mobile-first static HTML site.

Source markdown is never modified. Output goes to <repo>/docs/.
"""

import html
import os
import re
import sys

SRC = "/Users/hys/webdev/game-2.5d-guide"
OUT = os.path.join(SRC, "docs")

FOOTER_NOTE = (
    "Viết theo Godot 4.3–4.5 — kiểm tra lại trên bản bạn dùng"
)

# --------------------------------------------------------------------------
# inline
# --------------------------------------------------------------------------

RE_CODESPAN = re.compile(r"(`+)([\s\S]+?)\1")
RE_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
RE_BOLD = re.compile(r"\*\*([\s\S]+?)\*\*")
RE_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
RE_AUTOLINK = re.compile(r"(?<![\"'=(\w])(https?://[^\s<>)\]]+[^\s<>)\].,;:!?])")


def md_link_target(url):
    """Rewrite sibling markdown links to their generated html counterparts."""
    m = re.match(r"^([0-9A-Za-z._-]+)\.md(#.*)?$", url)
    if m:
        base = m.group(1)
        if base.upper() == "README":
            base = "index"
        return base + ".html" + (m.group(2) or "")
    return url


def inline(text):
    vault = []

    def stash(s):
        vault.append(s)
        return "\x00%d\x00" % (len(vault) - 1)

    # 1. code spans first: nothing inside them is markdown
    def _code(m):
        return stash("<code>%s</code>" % html.escape(m.group(2).strip(), quote=False))

    text = RE_CODESPAN.sub(_code, text)

    # 2. the single hand-written inline tag used by the sources
    text = text.replace("<br>", stash("<br>"))

    # 3. escape everything else
    text = html.escape(text, quote=False)

    # 4. links (href stashed so emphasis rules cannot touch a URL)
    def _link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        href = html.escape(md_link_target(url), quote=True)
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return stash('<a href="%s"%s>' % (href, ext)) + label + stash("</a>")

    text = RE_LINK.sub(_link, text)
    text = RE_AUTOLINK.sub(
        lambda m: stash('<a href="%s" target="_blank" rel="noopener">' % html.escape(m.group(1), quote=True))
        + m.group(1)
        + stash("</a>"),
        text,
    )

    # 5. emphasis
    text = RE_BOLD.sub(lambda m: "<strong>%s</strong>" % m.group(1), text)
    text = RE_ITALIC.sub(lambda m: "<em>%s</em>" % m.group(1), text)

    # 6. put the protected bits back (innermost stashes may nest, so loop)
    for _ in range(4):
        if "\x00" not in text:
            break
        text = re.sub(r"\x00(\d+)\x00", lambda m: vault[int(m.group(1))], text)
    return text


def plain(text):
    """Heading text with markup stripped, for TOC labels and <title>."""
    text = RE_CODESPAN.sub(lambda m: m.group(2).strip(), text)
    text = RE_LINK.sub(lambda m: m.group(1), text)
    text = text.replace("**", "").replace("<br>", " ")
    text = RE_ITALIC.sub(lambda m: m.group(1), text)
    return text.strip()


def slugify(text, seen):
    s = plain(text).lower()
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    s = s or "muc"
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else "%s-%d" % (s, n + 1)


# --------------------------------------------------------------------------
# block parser
# --------------------------------------------------------------------------

RE_FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`~]*)\s*$")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RE_HR = re.compile(r"^\s{0,3}(?:-\s*-\s*-[-\s]*|\*\s*\*\s*\*[\*\s]*|_\s*_\s*_[_\s]*)$")
RE_ULI = re.compile(r"^(\s*)([-*+])\s+(.*)$")
RE_OLI = re.compile(r"^(\s*)(\d{1,9})[.)]\s+(.*)$")
RE_TASK = re.compile(r"^\[([ xX])\]\s+(.*)$")
RE_ROW = re.compile(r"^\s*\|.*$")
RE_DELIM = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")

LANG_LABEL = {
    "gdscript": "GDScript",
    "bash": "Shell",
    "sh": "Shell",
    "json": "JSON",
    "markdown": "Markdown",
    "gitignore": ".gitignore",
    "": "Text",
}


class Renderer:
    def __init__(self, collect_toc=False):
        self.out = []
        self.toc = []  # (level, slug, label)
        self.slugs = {}
        self.collect_toc = collect_toc
        self.h1 = None
        self.code_n = 0

    # -- public ----------------------------------------------------------
    def render(self, lines):
        self.blocks(lines, top=True)
        return "".join(self.out)

    # -- helpers ---------------------------------------------------------
    def emit(self, s):
        self.out.append(s)

    def code_block(self, lang, body):
        self.code_n += 1
        label = LANG_LABEL.get(lang.lower(), lang)
        cls = re.sub(r"[^a-z0-9]+", "", lang.lower()) or "text"
        return (
            '<figure class="code" data-lang="%s">'
            '<figcaption><span class="code__lang">%s</span>'
            '<button class="code__copy" type="button" aria-label="Sao chép đoạn code">'
            '<span class="code__copy-txt">Copy</span></button></figcaption>'
            '<pre><code class="lang-%s">%s</code></pre></figure>'
            % (cls, html.escape(label, quote=True), cls, html.escape(body, quote=False))
        )

    # -- block loop ------------------------------------------------------
    def blocks(self, lines, top=False):
        i, n = 0, len(lines)
        while i < n:
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            # fenced code -------------------------------------------------
            m = RE_FENCE.match(line)
            if m:
                indent, fence, lang = m.group(1), m.group(2), m.group(3)
                ch, need = fence[0], len(fence)
                body, i = [], i + 1
                while i < n:
                    cm = re.match(r"^\s*(%s{%d,})\s*$" % (re.escape(ch), need), lines[i])
                    if cm:
                        i += 1
                        break
                    row = lines[i]
                    if indent and row.startswith(indent):
                        row = row[len(indent):]
                    body.append(row)
                    i += 1
                self.emit(self.code_block(lang, "\n".join(body)))
                continue

            # heading -----------------------------------------------------
            m = RE_HEADING.match(line)
            if m:
                lvl, raw = len(m.group(1)), m.group(2)
                if lvl == 1 and self.h1 is None and top:
                    self.h1 = plain(raw)
                    i += 1
                    continue  # page <h1> is rendered by the page shell
                slug = slugify(raw, self.slugs)
                if self.collect_toc and lvl in (2, 3):
                    self.toc.append((lvl, slug, plain(raw)))
                anchor = (
                    '<a class="anchor" href="#%s" aria-label="Liên kết tới mục này">#</a>' % slug
                )
                self.emit(
                    '<h%d id="%s" class="h h--%d">%s%s</h%d>'
                    % (lvl, slug, lvl, inline(raw), anchor, lvl)
                )
                i += 1
                continue

            # thematic break ---------------------------------------------
            if RE_HR.match(line):
                self.emit('<hr class="rule">')
                i += 1
                continue

            # blockquote --------------------------------------------------
            if re.match(r"^\s{0,3}>", line):
                buf = []
                while i < n and (re.match(r"^\s{0,3}>", lines[i]) or (buf and lines[i].strip())):
                    buf.append(re.sub(r"^\s{0,3}>\s?", "", lines[i]))
                    i += 1
                sub = Renderer()
                self.emit('<blockquote class="note">%s</blockquote>' % sub.render(buf))
                continue

            # table -------------------------------------------------------
            if RE_ROW.match(line) and i + 1 < n and RE_DELIM.match(lines[i + 1]):
                head = self.split_row(line)
                aligns = self.aligns(lines[i + 1], len(head))
                i += 2
                body = []
                while i < n and RE_ROW.match(lines[i]):
                    body.append(self.split_row(lines[i]))
                    i += 1
                self.emit(self.table(head, aligns, body))
                continue

            # lists -------------------------------------------------------
            if RE_ULI.match(line) or RE_OLI.match(line):
                i = self.list_block(lines, i)
                continue

            # paragraph ---------------------------------------------------
            buf = []
            while i < n and lines[i].strip():
                if (
                    RE_FENCE.match(lines[i])
                    or RE_HEADING.match(lines[i])
                    or RE_HR.match(lines[i])
                    or re.match(r"^\s{0,3}>", lines[i])
                    or RE_ULI.match(lines[i])
                    or RE_OLI.match(lines[i])
                    or RE_ROW.match(lines[i])
                ):
                    break
                buf.append(lines[i].strip())
                i += 1
            if buf:
                self.emit("<p>%s</p>" % inline(" ".join(buf)))
            elif i < n and not buf:
                i += 1

    # -- tables ----------------------------------------------------------
    @staticmethod
    def split_row(line):
        parts = re.split(r"(?<!\\)\|", line.strip())
        if parts and not parts[0].strip():
            parts.pop(0)
        if parts and not parts[-1].strip():
            parts.pop()
        return [p.strip().replace("\\|", "|") for p in parts]

    @staticmethod
    def aligns(delim, ncols):
        parts = [p.strip() for p in delim.strip().strip("|").split("|")]
        out = []
        for p in parts:
            if p.startswith(":") and p.endswith(":"):
                out.append("center")
            elif p.endswith(":"):
                out.append("right")
            else:
                out.append("")
        while len(out) < ncols:
            out.append("")
        return out

    def table(self, head, aligns, body):
        def cell(tag, txt, al):
            a = ' class="ta-%s"' % al if al else ""
            return "<%s%s>%s</%s>" % (tag, a, inline(txt), tag)

        rows = ["<thead><tr>"]
        rows += [cell("th", h, aligns[j] if j < len(aligns) else "") for j, h in enumerate(head)]
        rows.append("</tr></thead><tbody>")
        for r in body:
            rows.append("<tr>")
            for j in range(len(head)):
                txt = r[j] if j < len(r) else ""
                rows.append(cell("td", txt, aligns[j] if j < len(aligns) else ""))
            rows.append("</tr>")
        rows.append("</tbody>")
        return (
            '<div class="table-wrap" tabindex="0" role="region" aria-label="Bảng, có thể cuộn ngang">'
            "<table>%s</table></div>" % "".join(rows)
        )

    # -- lists -----------------------------------------------------------
    def list_block(self, lines, i):
        """Parse one list (with nesting) starting at lines[i]; return next index."""
        items, n = [], len(lines)
        base_indent = len(RE_ULI.match(lines[i]).group(1)) if RE_ULI.match(lines[i]) else len(
            RE_OLI.match(lines[i]).group(1)
        )
        ordered = RE_OLI.match(lines[i]) is not None
        start = RE_OLI.match(lines[i]).group(2) if ordered else None

        while i < n:
            line = lines[i]
            if not line.strip():
                # blank line: keep going only if the list continues after it
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                if j < n:
                    mm = RE_ULI.match(lines[j]) or RE_OLI.match(lines[j])
                    if mm and len(mm.group(1)) >= base_indent:
                        i = j
                        continue
                    if lines[j].startswith(" " * (base_indent + 2)) and items:
                        items[-1].append("")
                        i = j
                        continue
                break

            m = RE_ULI.match(line) or RE_OLI.match(line)
            if m and len(m.group(1)) == base_indent:
                if (RE_OLI.match(line) is not None) != ordered:
                    break
                items.append([m.group(3)])
                i += 1
                continue
            if m and len(m.group(1)) > base_indent:
                items[-1].append(line[base_indent:])
                i += 1
                continue
            if m and len(m.group(1)) < base_indent:
                break
            # lazy continuation / indented child block
            if line.startswith(" " * (base_indent + 2)) or not (
                RE_HEADING.match(line) or RE_HR.match(line) or RE_FENCE.match(line) or RE_ROW.match(line)
            ):
                if not items:
                    break
                items[-1].append(line[base_indent:] if line.startswith(" " * base_indent) else line.strip())
                i += 1
                continue
            break

        has_task = any(RE_TASK.match(it[0].strip()) for it in items)
        tag = "ol" if ordered else "ul"
        attrs = ' class="list list--task"' if has_task else ' class="list"'
        if ordered and start and start != "1":
            attrs += ' start="%s"' % html.escape(start, quote=True)
        parts = ["<%s%s>" % (tag, attrs)]
        for it in items:
            parts.append(self.list_item(it))
        parts.append("</%s>" % tag)
        self.emit("".join(parts))
        return i

    def list_item(self, item_lines):
        first = item_lines[0]
        rest = item_lines[1:]
        tm = RE_TASK.match(first.strip())
        cls, box = "", ""
        if tm:
            done = tm.group(1).lower() == "x"
            first = tm.group(2)
            cls = ' class="task%s"' % (" task--done" if done else "")
            box = (
                '<span class="checkbox%s" aria-hidden="true"></span>'
                % (" checkbox--on" if done else "")
            )

        # does the item contain block-level children?
        block_child = any(
            RE_FENCE.match(l) or RE_ROW.match(l) or RE_ULI.match(l) or RE_OLI.match(l) or l.strip() == ""
            for l in rest
        )
        if rest and block_child:
            sub = Renderer()
            inner = sub.render([first] + rest)
            return "<li%s>%s%s</li>" % (cls, box, inner)
        text = " ".join([first.strip()] + [l.strip() for l in rest]).strip()
        return "<li%s>%s%s</li>" % (cls, box, inline(text))


# --------------------------------------------------------------------------
# page shells
# --------------------------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#12101a">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' fill='%2312101a'/%3E%3Crect x='6' y='2' width='4' height='3' fill='%23ffc857'/%3E%3Crect x='5' y='5' width='6' height='2' fill='%23ffe3a0'/%3E%3Crect x='6' y='7' width='4' height='6' fill='%235ad1e6'/%3E%3Crect x='4' y='13' width='8' height='2' fill='%23474063'/%3E%3C/svg%3E">
<!--BOOT-->
</head>
<body class="{bodyclass}">
"""

BOOT = (
    '<script>/* set the saved theme before first paint so there is no flash */'
    '(function(){try{var t=localStorage.getItem("g25d-theme");'
    'if(t==="light"||t==="dark")'
    'document.documentElement.setAttribute("data-theme",t);}catch(e){}})();'
    "</script>"
)


def head(title, desc, bodyclass):
    return HEAD.format(title=title, desc=desc, bodyclass=bodyclass).replace("<!--BOOT-->", BOOT)


FOOT = """<script src="app.js" defer></script>
</body>
</html>
"""


def chapter_page(meta, body_html, toc, prev_meta, next_meta):
    num = meta["num"]
    title = meta["title"]
    toc_items = []
    for lvl, slug, label in toc:
        toc_items.append(
            '<li class="toc__item toc__item--h%d"><a href="#%s">%s</a></li>'
            % (lvl, slug, html.escape(label, quote=False))
        )
    toc_html = "".join(toc_items)

    nav = []
    if prev_meta:
        nav.append(
            '<a class="pager__link pager__link--prev" href="%s.html">'
            '<span class="pager__dir">← Chương %s</span>'
            '<span class="pager__title">%s</span></a>'
            % (prev_meta["slug"], prev_meta["num"], html.escape(prev_meta["title"], quote=False))
        )
    if next_meta:
        nav.append(
            '<a class="pager__link pager__link--next" href="%s.html">'
            '<span class="pager__dir">Chương %s →</span>'
            '<span class="pager__title">%s</span></a>'
            % (next_meta["slug"], next_meta["num"], html.escape(next_meta["title"], quote=False))
        )

    return (
        head(
            "%s %s · Godot 4 2.5D" % (num, html.escape(title, quote=True)),
            html.escape(plain(meta["desc"]), quote=True),
            "page page--chapter",
        )
        + """<div class="progress" aria-hidden="true"><span class="progress__bar" id="progressBar"></span></div>

<header class="topbar">
  <a class="topbar__back" href="index.html"><span aria-hidden="true">←</span> Mục lục</a>
  <span class="topbar__num">{num}</span>
  <button class="iconbtn themebtn" type="button" data-theme-toggle aria-pressed="false" aria-label="Đổi nền sáng/tối">
    <span class="themebtn__txt">Sáng</span>
  </button>
  <button class="iconbtn topbar__toc" id="tocToggle" type="button" aria-expanded="false" aria-controls="tocPanel">
    <span class="topbar__toc-icon" aria-hidden="true"></span><span>Mục</span>
  </button>
</header>

<div class="shell">
  <nav class="toc" id="tocPanel" aria-label="Mục lục chương">
    <p class="toc__title">Trong chương này</p>
    <ol class="toc__list">{toc}</ol>
  </nav>

  <main class="main" id="main">
    <article class="prose">
      <p class="eyebrow">Chương {num} · {lines} dòng</p>
      <h1 class="title">{title}</h1>
      <p class="lede">{desc}</p>
      <hr class="rule rule--tight">
      {body}
    </article>

    <nav class="pager" aria-label="Chuyển chương">{nav}</nav>

    <footer class="foot">
      <p class="foot__note">{note}</p>
      <p class="foot__links"><a href="index.html">← Về mục lục</a> · <a href="#main">↑ Đầu trang</a></p>
    </footer>
  </main>
</div>

<button class="totop" id="toTop" type="button" aria-label="Lên đầu trang">↑</button>
<div class="scrim" id="scrim" hidden></div>
""".format(
            num=num,
            title=html.escape(title, quote=False),
            desc=inline(meta["desc"]),
            lines=meta["lines"],
            toc=toc_html,
            body=body_html,
            nav="".join(nav),
            note=html.escape(FOOTER_NOTE, quote=False),
        )
        + FOOT
    )


def index_page(chapters, readme_html):
    cards = []
    for c in chapters:
        cards.append(
            """    <a class="card" href="{slug}.html">
      <span class="card__num">{num}</span>
      <span class="card__body">
        <span class="card__title">{title}</span>
        <span class="card__desc">{desc}</span>
        <span class="card__meta"><span class="chip">{when}</span><span class="card__lines">{lines} dòng</span></span>
      </span>
      <span class="card__go" aria-hidden="true">→</span>
    </a>""".format(
                slug=c["slug"],
                num=c["num"],
                title=html.escape(c["title"], quote=False),
                desc=inline(c["desc"]),
                when=html.escape(c["when"], quote=False),
                lines=c["lines"],
            )
        )

    total = sum(c["lines"] for c in chapters)
    return (
        head(
            "Làm game phiêu lưu 2.5D 8-bit bằng Godot 4",
            "Bộ tài liệu tiếng Việt: dựng game phiêu lưu 2.5D pixel art 8-bit bằng Godot 4, có định hướng workflow AI.",
            "page page--index",
        )
        + """<header class="hero">
  <div class="hero__tools">
    <button class="iconbtn themebtn" type="button" data-theme-toggle aria-pressed="false" aria-label="Đổi nền sáng/tối">
      <span class="themebtn__txt">Sáng</span>
    </button>
  </div>
  <p class="hero__kicker">Tài liệu tiếng Việt · Godot 4.3–4.5</p>
  <h1 class="hero__title"><span class="hero__title-line">Làm game phiêu lưu</span><span class="hero__title-line hero__title-line--accent">2.5D 8-bit</span><span class="hero__title-line">bằng Godot 4</span></h1>
  <p class="hero__lede">Pixel art 2D đặt trong không gian 3D thật — kiểu HD-2D. Từ cài Godot tới export lên itch.io, kèm cách dùng AI như một thành viên trong team.</p>
  <dl class="stats">
    <div class="stat"><dt>Chương</dt><dd>{nchap}</dd></div>
    <div class="stat"><dt>Dòng</dt><dd>{total}</dd></div>
    <div class="stat"><dt>Engine</dt><dd>Godot 4</dd></div>
  </dl>
  <a class="btn btn--primary" href="00-to-doc.html">Bắt đầu từ chương 00 <span aria-hidden="true">→</span></a>
</header>

<main class="shell shell--index" id="main">
  <section class="section" aria-labelledby="h-style">
    <h2 class="section__title" id="h-style">Phong cách chốt sẵn</h2>
    <div class="prose prose--intro">{readme}</div>
  </section>

  <section class="section" aria-labelledby="h-toc">
    <h2 class="section__title" id="h-toc">Mục lục</h2>
    <div class="grid">
{cards}
    </div>
  </section>

  <section class="section" aria-labelledby="h-how">
    <h2 class="section__title" id="h-how">Đọc theo thứ tự nào</h2>
    <ol class="steps">
      <li><strong>00</strong> để biết mình sẽ build cái gì.</li>
      <li><strong>01 → 02 → 04</strong> để có nhân vật chạy được trong world 3D. Mốc “game bắt đầu có hồn”.</li>
      <li><strong>09</strong> đọc <em>sớm</em>, không để cuối — bạn sẽ dùng AI ở mọi chương sau đó.</li>
      <li><strong>06</strong> nặng nhất về code. Chia nhỏ: dialog → inventory → flags → save.</li>
      <li><strong>07</strong> đọc bất cứ lúc nào bí ý tưởng.</li>
    </ol>
  </section>

  <footer class="foot">
    <p class="foot__note">{note}</p>
  </footer>
</main>
""".format(
            nchap=len(chapters),
            total=total,
            readme=readme_html,
            cards="\n".join(cards),
            note=html.escape(FOOTER_NOTE, quote=False),
        )
        + FOOT
    )


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read().replace("\r\n", "\n").split("\n")


def readme_meta():
    """Pull (num, file, desc, when) out of the README mục lục table."""
    rows = []
    for line in read(os.path.join(SRC, "README.md")):
        if not line.startswith("|"):
            continue
        cells = Renderer.split_row(line)
        if len(cells) != 4:
            continue
        if re.match(r"^\d{2}$", cells[0].strip()):
            m = RE_LINK.search(cells[1])
            fname = m.group(2) if m else cells[1]
            rows.append(
                {
                    "num": cells[0].strip(),
                    "file": fname,
                    "desc": cells[2].strip(),
                    "when": cells[3].strip(),
                }
            )
    return rows


def readme_intro_html():
    """Everything in the README between the style heading and the mục lục."""
    lines = read(os.path.join(SRC, "README.md"))
    start = end = None
    for idx, l in enumerate(lines):
        if l.startswith("## Phong cách chốt sẵn"):
            start = idx + 1
        elif l.startswith("## Mục lục"):
            end = idx
            break
    body = lines[start:end] if start is not None and end is not None else []
    while body and (not body[0].strip() or RE_HR.match(body[0])):
        body.pop(0)
    while body and (not body[-1].strip() or RE_HR.match(body[-1])):
        body.pop()
    return Renderer().render(body)


def main():
    os.makedirs(OUT, exist_ok=True)
    metas = readme_meta()
    if len(metas) != 11:
        print("WARN: expected 11 chapters from README, got %d" % len(metas), file=sys.stderr)

    chapters = []
    for m in metas:
        path = os.path.join(SRC, m["file"])
        lines = read(path)
        r = Renderer(collect_toc=True)
        body = r.render(lines)
        title = r.h1 or m["file"]
        title = re.sub(r"^\d{2}\s*[—–-]\s*", "", title)
        # README descriptions often restate the chapter title ("Nhân vật điều
        # khiển: CharacterBody3D, ..."). Drop the restatement on the cards.
        desc = m["desc"]
        if desc.lower().startswith(title.lower() + ":"):
            desc = desc[len(title) + 1:].strip()
        chapters.append(
            {
                "slug": m["file"][:-3],
                "num": m["num"],
                "title": title,
                "desc": desc,
                "when": m["when"],
                "lines": len([l for l in lines if True]) - (1 if lines and lines[-1] == "" else 0),
                "body": body,
                "toc": r.toc,
            }
        )

    for k, c in enumerate(chapters):
        prev_c = chapters[k - 1] if k > 0 else None
        next_c = chapters[k + 1] if k + 1 < len(chapters) else None
        with open(os.path.join(OUT, c["slug"] + ".html"), "w", encoding="utf-8") as fh:
            fh.write(chapter_page(c, c["body"], c["toc"], prev_c, next_c))
        print("  %-28s %5d dòng  %3d mục TOC" % (c["slug"] + ".html", c["lines"], len(c["toc"])))

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(index_page(chapters, readme_intro_html()))
    print("  index.html")


if __name__ == "__main__":
    main()
