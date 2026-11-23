"""Stamp every local script and stylesheet a page loads with ?v=<hash of that file>.

Pages on GitHub Pages are cached for 10 minutes. A page that loads a shared file under a URL that changes whenever
the file changes always gets the current version, and nobody has to remember to bump a number.

    py tools/stamp_assets.py          # rewrite stamps where a file changed (the pre-commit hook runs this)
    py tools/stamp_assets.py --check  # exit 1 if any stamp is stale
"""
import glob, hashlib, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, '*', 'index.html'))
REF = re.compile(r'''(?P<attr>src|href)="(?P<path>(?!https?:|//|data:|#)[^"?#]+\.(?:js|css))(?:\?v=[^"]*)?"''')

def digest(path):
    data = open(path, 'rb').read().replace(b'\r\n', b'\n')
    return hashlib.sha1(data).hexdigest()[:8]

def stamp(check=False):
    stale = []
    for page in PAGES:
        raw = open(page, encoding='utf8', newline='').read()
        def sub(m):
            target = os.path.normpath(os.path.join(os.path.dirname(page), m['path']))
            if not os.path.exists(target): return m[0]
            return f'{m["attr"]}="{m["path"]}?v={digest(target)}"'
        new = REF.sub(sub, raw)
        if new != raw:
            stale.append(os.path.relpath(page, ROOT))
            if not check: open(page, 'w', encoding='utf8', newline='').write(new)
    return stale

if __name__ == '__main__':
    check = '--check' in sys.argv
    stale = stamp(check)
    if stale: print(('stale stamps: ' if check else 'stamped: ') + ', '.join(stale))
    sys.exit(1 if check and stale else 0)
