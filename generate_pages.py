import pandas as pd
import os
import json
import re

# ── CONFIG ──
CSV_FILE     = 'Data_corrected.csv'
TEMPLATE_FILE = 'template.html'
OUTPUT_DIR   = 'generated_pages'

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)
template = open(TEMPLATE_FILE, encoding='utf-8').read()

def make_faq_schema(faq_text):
    """Convert faq text to JSON-LD schema format"""
    entities = []
    lines = faq_text.split('\n')
    current_q = None
    current_a = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith('?'):
            if current_q and current_a:
                entities.append({
                    "@type": "Question",
                    "name": current_q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": ' '.join(current_a).strip()
                    }
                })
            current_q = line
            current_a = []
        elif current_q:
            current_a.append(line)
    if current_q and current_a:
        entities.append({
            "@type": "Question",
            "name": current_q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": ' '.join(current_a).strip()
            }
        })
    return json.dumps(entities, ensure_ascii=False, indent=2)

def safe(val):
    """Convert NaN to empty string and escape backticks for JS template literals"""
    if pd.isna(val):
        return ''
    return str(val).replace('`', "'").replace('\\', '\\\\')

count = 0
for _, row in df.iterrows():
    html = template

    # Replace all {{placeholders}}
    for col in df.columns:
        val = safe(row[col])
        html = html.replace('{{' + col + '}}', val)

    # Add FAQ schema
    faq_schema = make_faq_schema(safe(row['faq']))
    html = html.replace('{{faq_schema}}', faq_schema)

    # Output file
    slug = safe(row['slug'])
    out_path = os.path.join(OUTPUT_DIR, f'{slug}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    count += 1
    print(f'✓  {slug}.html')

print(f'\n✅ {count} pages generated in /{OUTPUT_DIR}/')
