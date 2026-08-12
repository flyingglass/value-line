"""Extract epub text content to raw/ directory."""
import zipfile, re, os, sys
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','head'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script','style','head'):
            self.skip = False
        if tag in ('p','div','br','li','h1','h2','h3','h4','h5','h6','blockquote','tr','section','article'):
            self.text.append('\n')
    def handle_data(self, data):
        if not self.skip:
            t = data.strip()
            if t:
                self.text.append(t)

epub_path = r'C:\Users\fly\Downloads\盲眼钟表匠  生命自然选择的秘密 = The Blind Watchmaker Why the Evidence of Evolution Reveals a Universe without Design ([英] 理查德・道金斯 (Richard Dawkins) 著  王道还 译) (z-library.sk, 1lib.sk, z-lib.sk).epub'

all_text = []
with zipfile.ZipFile(epub_path, 'r') as z:
    for f in sorted(z.namelist()):
        if f.endswith('.xhtml') and 'part' in f:
            content = z.read(f).decode('utf-8', errors='replace')
            extractor = TextExtractor()
            extractor.feed(content)
            all_text.append(''.join(extractor.text))

full_text = '\n'.join(all_text)
full_text = re.sub(r'\n{3,}', '\n\n', full_text)

os.makedirs('research-wiki/raw/research/articles', exist_ok=True)
out_path = 'research-wiki/raw/research/articles/道金斯_1986_盲眼钟表匠.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f'OK: {len(full_text)} chars, ~{full_text.count(chr(10))} lines')
sys.stdout.flush()
