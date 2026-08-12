"""
Extract full text from an .epub file.
Usage: python extract_epub.py <epub_path> [--output <output_path>]

epub is a ZIP archive containing XHTML chapters.
This script extracts text from all .xhtml/.html files, stripping tags.
Output: plain text file with minimal formatting.
"""
import zipfile, re, os, sys, argparse
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    """Extract visible text from XHTML, stripping tags."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head'):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head'):
            self.skip = False
        if tag in ('p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                   'blockquote', 'tr', 'section', 'article', 'td', 'th'):
            self.text.append('\n')

    def handle_data(self, data):
        if not self.skip:
            t = data.strip()
            if t:
                self.text.append(t)


def extract_epub(epub_path, output_path=None):
    """
    Extract all text from epub file.

    Args:
        epub_path: Path to .epub file
        output_path: Path to save extracted text. If None, auto-generate from epub name.

    Returns:
        (output_path, char_count, line_count)
    """
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"Epub not found: {epub_path}")

    all_text = []
    with zipfile.ZipFile(epub_path, 'r') as z:
        # Sort files to maintain chapter order
        for f in sorted(z.namelist()):
            if f.endswith(('.xhtml', '.html', '.htm')):
                content = z.read(f).decode('utf-8', errors='replace')
                extractor = TextExtractor()
                extractor.feed(content)
                all_text.append(''.join(extractor.text))

    full_text = '\n'.join(all_text)
    # Clean up excessive newlines (3+ -> 2)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)

    # Generate output path if not provided
    if output_path is None:
        epub_basename = os.path.splitext(os.path.basename(epub_path))[0]
        # Sanitize: keep only Chinese/English/digits/underscore/hyphen
        safe_name = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', epub_basename)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        output_path = f"{safe_name}.txt"

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    char_count = len(full_text)
    line_count = full_text.count('\n')

    return output_path, char_count, line_count


def main():
    parser = argparse.ArgumentParser(description='Extract text from epub files')
    parser.add_argument('epub_path', help='Path to .epub file')
    parser.add_argument('--output', '-o', help='Output path (auto-generated if omitted)')
    args = parser.parse_args()

    try:
        out, chars, lines = extract_epub(args.epub_path, args.output)
        print(f"OK: {out}")
        print(f"     {chars} chars, ~{lines} lines")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
