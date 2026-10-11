"""Export the existing semantic HTML source to readable Markdown (stdlib only).

This is intentionally one-way. Unknown tags fail rather than silently lose text.
The generated Markdown is a reading artifact; content/*.html remains the source.
"""
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit
import re


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


class Tree(HTMLParser):
    VOID = {'br', 'img', 'input'}
    SUPPORTED = set('a p br code strong em div span h2 h3 h4 ul ol li table thead tbody tr th td details summary figure img figcaption pre section form label input aside'.split())

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(source)
        self.close()
        if len(self.stack) != 1:
            raise ValueError('Unclosed HTML source tag: ' + self.stack[-1].tag)

    def handle_starttag(self, tag, attrs):
        if tag not in self.SUPPORTED:
            raise ValueError('Unsupported Markdown export tag: ' + tag)
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.stack[-1].tag != tag:
            raise ValueError('Mismatched HTML source tag: ' + tag)
        self.stack.pop()

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def text_of(node):
    return node if isinstance(node, str) else ''.join(text_of(c) for c in node.children)


class Exporter:
    def __init__(self, slug, entries, migrations):
        self.slug = slug
        self.pages = {p['slug'] + '.html' for p in entries}
        self.migrations = migrations

    def url(self, value):
        u = urlsplit(value)
        if u.scheme or value.startswith('//'):
            return value
        key = (u.path or self.slug + '.html') + ('#' + u.fragment if u.fragment else '')
        # Resolve old aliases to real content, including aliases on retained pages.
        target = self.migrations.get(key, value)
        u = urlsplit(target)
        if u.path in self.pages:
            path = str(PurePosixPath(u.path).with_suffix('.md'))
        elif u.path:
            path = '../' + u.path
        else:
            path = ''
        return urlunsplit(('', '', path, u.query, u.fragment))

    def anchor(self, n):
        return f'<a id="{escape(n.attrs["id"], quote=True)}"></a>\n\n' if 'id' in n.attrs else ''

    def inline(self, n):
        if isinstance(n, str):
            # Escape Markdown syntax and literal angle brackets; keep readable prose.
            s = re.sub(r'\s+', ' ', n)
            s = re.sub(r'([\\`*\[\]_])', r'\\\1', s)
            return s.replace('<', '&lt;').replace('>', '&gt;')
        content = ''.join(self.inline(c) for c in n.children)
        if n.tag == 'a':
            ident = f'<a id="{escape(n.attrs["id"], quote=True)}"></a>' if 'id' in n.attrs else ''
            return ident + (f'[{content}]({self.url(n.attrs["href"])})' if 'href' in n.attrs else content)
        if n.tag == 'code':
            raw = text_of(n)
            fence = '`' * (max([len(x) for x in re.findall(r'`+', raw)] + [0]) + 1)
            padding = ' ' if raw.startswith(('`', ' ')) or raw.endswith(('`', ' ')) else ''
            return fence + padding + raw + padding + fence
        if n.tag in ('strong', 'em'):
            marker = '**' if n.tag == 'strong' else '*'
            return marker + content.strip() + marker
        if n.tag == 'br':
            return '<br>'
        if n.tag == 'img':
            alt = n.attrs.get('alt', '').replace('[', r'\[').replace(']', r'\]')
            return f'![{alt}]({self.url(n.attrs["src"])})'
        if n.tag == 'input':
            if 'value' in n.attrs:
                return f'（初值 `{n.attrs["value"]}`）'
            return '（交互筛选见 HTML 版）'
        return content

    def raw_html(self, n):
        if isinstance(n, str):
            return escape(n)
        attrs = {k: self.url(v) if k in ('href', 'src') else v for k, v in n.attrs.items()}
        start = '<' + n.tag + ''.join(f' {k}="{escape(v or "", quote=True)}"' for k, v in attrs.items()) + '>'
        return start if n.tag in Tree.VOID else start + ''.join(self.raw_html(c) for c in n.children) + '</' + n.tag + '>'

    def block(self, n):
        if isinstance(n, str):
            return self.inline(n) if n.strip() else ''
        tag = n.tag
        anchor = self.anchor(n)
        if tag in ('h2', 'h3', 'h4'):
            return anchor + '#' * int(tag[1]) + ' ' + self.inline(n).strip() + '\n\n'
        if tag == 'pre':
            raw = text_of(n).strip('\n')
            fence = '`' * max(3, max([len(x) + 1 for x in re.findall(r'`+', raw)] + [3]))
            return anchor + fence + '\n' + raw + '\n' + fence + '\n\n'
        if tag in ('ul', 'ol'):
            items = [c for c in n.children if isinstance(c, Node) and c.tag == 'li']
            lines = []
            for i, item in enumerate(items, int(n.attrs.get('start', 1))):
                prefix = f'{i}. ' if tag == 'ol' else '- '
                body = ''.join('\n' + self.block(c) if isinstance(c, Node) and c.tag in ('p', 'ol', 'ul', 'pre') else self.inline(c) for c in item.children).strip()
                lines.append(prefix + body.replace('\n', '\n' + ' ' * len(prefix)))
            return anchor + '\n'.join(lines) + '\n\n'
        if tag == 'table':
            def descendants(node, target):
                for c in node.children:
                    if isinstance(c, Node):
                        if c.tag == target:
                            yield c
                        else:
                            yield from descendants(c, target)
            rows = list(descendants(n, 'tr'))
            cells = [[c for c in row.children if isinstance(c, Node) and c.tag in ('td', 'th')] for row in rows]
            # GFM cannot represent merged cells; retain that table as semantic HTML.
            if any('colspan' in c.attrs or 'rowspan' in c.attrs or any(isinstance(x, Node) and x.tag in ('p','pre','div','ol','ul','table') for x in c.children) for row in cells for c in row):
                return self.raw_html(n) + '\n\n'
            if not cells:
                return ''
            width = max(map(len, cells))
            data = [[self.inline(c).strip().replace('|', r'\|') for c in row] for row in cells]
            if not any(c.tag == 'th' for c in cells[0]):
                data.insert(0, [''] * width)
            data.insert(1, ['---'] * width)
            return anchor + '\n'.join('| ' + ' | '.join(row + [''] * (width - len(row))) + ' |' for row in data) + '\n\n'
        if tag == 'summary':
            return '**' + self.inline(n).strip() + '**\n\n'
        if tag in ('p', 'figcaption', 'label'):
            return anchor + self.inline(n).strip() + '\n\n'
        if tag == 'a':
            return self.inline(n) + '\n\n'
        if tag in ('strong', 'em', 'code'):
            return anchor + self.inline(n) + '\n\n'
        if tag in ('img', 'input', 'span'):
            return anchor + self.inline(n) + ('\n\n' if tag == 'img' else '')
        if tag == 'form':
            return anchor + '交互计算见本章 HTML 版；以下保留输入与默认值。\n\n' + ''.join(self.block(c) for c in n.children)
        return anchor + ''.join(self.block(c) for c in n.children)


def render_markdown(entry, body, entries, migrations):
    slug = entry['slug']
    exporter = Exporter(slug, entries, migrations)
    tree = Tree(body)
    title = (f'{entry["number"]:02d} · ' if entry['kind'] == 'chapter' else '') + entry['title']
    header = f'# {title}\n\n{entry["subtitle"]}\n\n'
    header += f'> 自动生成的 Markdown 阅读版；正文只维护 [HTML 内容源](../content/{slug}.html)，导航维护 [pages.json](../scripts/pages.json)。[本章 HTML](../{slug}.html) · [阅读路线](index.md)\n\n'
    toc = []
    def collect(node):
        for n in node.children:
            if isinstance(n, Node):
                if n.tag in ('h2', 'h3'):
                    toc.append(('  ' if n.tag == 'h3' else '') + f'- [{text_of(n)}](#{n.attrs["id"]})')
                collect(n)
    collect(tree.root)
    header += '\n'.join(toc) + '\n\n'
    result = header + exporter.block(tree.root).strip() + '\n'
    index = entries.index(entry)
    adjacent = []
    for i, label in ((index - 1, '上一页'), (index + 1, '下一页')):
        if 0 <= i < len(entries):
            p = entries[i]
            adjacent.append(f'[{label}：{p["title"]}]({p["slug"]}.md)')
    result += '\n---\n\n' + ' · '.join(adjacent) + '\n'
    return result
