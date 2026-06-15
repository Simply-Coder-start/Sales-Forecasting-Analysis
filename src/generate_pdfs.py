import os
import glob
from markdown_it import MarkdownIt

def generate_print_ready_html():
    base_dir = r"d:\30 Python Projects\Sales Forecasting Analysis"
    docs_dir = os.path.join(base_dir, "docs", "archive")
    out_dir = os.path.join(base_dir, "reports", "pdfs")
    os.makedirs(out_dir, exist_ok=True)
    
    md_files = [
        "viva_prep_guide.md",
        "viva_presentation_slides.md",
        "final_academic_report.md",
        "evaluator_review.md"
    ]
    
    md = MarkdownIt('commonmark').enable('table')
    
    css = """
    @page {
        size: A4;
        margin: 1in;
    }
    body {
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 12pt;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 2em;
        background-color: #fff;
    }
    h1, h2, h3, h4 {
        font-family: "Arial", sans-serif;
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    h1 { font-size: 24pt; border-bottom: 2px solid #2c3e50; padding-bottom: 0.2em; }
    h2 { font-size: 18pt; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
    h3 { font-size: 14pt; }
    p { margin-bottom: 1em; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1.5em;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background-color: #f8f9fa;
        font-weight: bold;
    }
    code {
        font-family: "Courier New", Courier, monospace;
        background-color: #f4f4f4;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    pre {
        background-color: #f4f4f4;
        padding: 1em;
        border-radius: 4px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    blockquote {
        border-left: 4px solid #ccc;
        margin: 0;
        padding-left: 1em;
        color: #666;
        font-style: italic;
    }
    .page-break {
        page-break-before: always;
    }
    
    @media screen {
        body {
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-top: 2em;
            margin-bottom: 2em;
        }
    }
    """

    for filename in md_files:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found.")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        html_body = md.render(content)
        
        # Add page breaks before h1 and h2 for presentation slides
        if "slides" in filename:
            html_body = html_body.replace("<h2>", "<h2 class='page-break'>")
            
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{filename.replace('.md', '')}</title>
    <style>{css}</style>
</head>
<body>
    {html_body}
    <script>
        // Auto-print prompt when opened (optional, disabled for now)
        // window.onload = function() {{ window.print(); }}
    </script>
</body>
</html>"""
        
        out_name = filename.replace(".md", ".html")
        out_path = os.path.join(out_dir, out_name)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_print_ready_html()
