#!/usr/bin/env python3 -I
"""Make one self-contained HTML file from a prerendered SvelteKit page: inline its CSS, drop its JS.
usage: inline-html.py <build-dir> <page.html> <out.html>"""
import re, sys, os
build, page, out = sys.argv[1:4]
html = open(page).read()
css = []
for m in re.finditer(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>', html):
    css.append(open(os.path.join(build, m.group(1).lstrip('/'))).read())
html = re.sub(r'<link[^>]+rel="stylesheet"[^>]*>', '', html)
html = re.sub(r'<link[^>]+rel="modulepreload"[^>]*>', '', html)
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
html = html.replace('</head>', '<style>' + '\n'.join(css) + '</style></head>', 1)
open(out, 'w').write(html)
print('wrote', out, len(html), 'bytes')
