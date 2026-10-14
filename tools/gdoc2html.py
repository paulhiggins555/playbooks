import json, sys, html

def find_tab(tabs, tid):
    for t in tabs:
        if t['tabProperties']['tabId'] == tid: return t
        r = find_tab(t.get('childTabs', []), tid)
        if r: return r

def run_html(el):
    tr = el.get('textRun')
    if not tr: return ''
    txt = tr['content'].replace('\n', '').replace('\u000b', '\n')
    if not txt: return ''
    s = tr.get('textStyle', {})
    t = html.escape(txt).replace('\n', '<br>')
    if not t.strip(): return t
    if s.get('bold'): t = f'<strong>{t}</strong>'
    if s.get('italic'): t = f'<em>{t}</em>'
    link = s.get('link', {}).get('url')
    if link: t = f'<a href="{html.escape(link)}">{t}</a>'
    return t

def para_html(p):
    return ''.join(run_html(e) for e in p.get('elements', [])).strip()

HEAD = {'TITLE': 'h1', 'HEADING_1': 'h2', 'HEADING_2': 'h3', 'HEADING_3': 'h4', 'HEADING_4': 'h5', 'HEADING_5': 'h6', 'HEADING_6': 'h6', 'SUBTITLE': 'p class="subtitle"'}

def convert(content, lists):
    out = []
    stack = []  # list of (tag) open lists
    def close_to(n):
        while len(stack) > n:
            out.append(f'</li></{stack.pop()}>')
    for el in content:
        if 'paragraph' in el:
            p = el['paragraph']
            inner = para_html(p)
            b = p.get('bullet')
            if b:
                lvl = b.get('nestingLevel', 0)
                props = lists.get(b['listId'], {}).get('listProperties', {}).get('nestingLevels', [{}])
                lp = props[min(lvl, len(props)-1)] if props else {}
                ordered = 'glyphType' in lp and lp.get('glyphType') not in ('GLYPH_TYPE_UNSPECIFIED', 'NONE') 
                tag = 'ol' if ordered else 'ul'
                if len(stack) > lvl + 1: close_to(lvl + 1)
                if len(stack) == lvl + 1:
                    out.append('</li><li>' + inner)
                else:
                    while len(stack) < lvl + 1:
                        out.append(f'<{tag}><li>')
                        stack.append(tag)
                    out[-1] += inner
                continue
            close_to(0)
            if not inner: continue
            st = p.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
            tag = HEAD.get(st, 'p')
            if tag.startswith('h'):
                inner = inner.replace('<strong>', '').replace('</strong>', '')
            out.append(f'<{tag}>{inner}</{tag.split()[0]}>')
        elif 'table' in el:
            close_to(0)
            rows = el['table']['tableRows']
            out.append('<div class="table-wrap"><table>')
            for i, r in enumerate(rows):
                out.append('<tr>')
                for c in r['tableCells']:
                    cell = convert(c.get('content', []), lists)
                    t = 'th' if i == 0 else 'td'
                    out.append(f'<{t}>{cell}</{t}>')
                out.append('</tr>')
            out.append('</table></div>')
        elif 'sectionBreak' in el or 'tableOfContents' in el:
            close_to(0)
    close_to(0)
    return '\n'.join(out)

if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); c = d.get('content', d)
    tab = find_tab(c['tabs'], sys.argv[2])
    dt = tab['documentTab']
    print(convert(dt['body']['content'], dt.get('lists', {})))
