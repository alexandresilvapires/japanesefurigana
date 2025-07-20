import json
import pykakasi
import re

# Input json file
file = "ja_jp"

KANJI_RE = re.compile(r'[\u4e00-\u9FFF]')

with open(file + ".json") as f:
    data = json.load(f)
    data_word = data.copy()

kks = pykakasi.kakasi()

for item in data:
    original_text = data[item]
    result = kks.convert(original_text)
    
    sentenceHasKanji = False
    furigana_text = original_text  # Start with original untouched text
    furigana = ""

    # We'll build a list of (kanji, hira) pairs to substitute
    replacements = []

    for token in result:
        orig = token["orig"]
        hira = token["hira"]

        if KANJI_RE.search(orig):
            sentenceHasKanji = True
            replacements.append((orig, f"{orig}({hira})"))
            furigana += hira + "|"

    # Avoid over-replacing if word appears multiple times
    for orig, annotated in replacements:
        furigana_text = furigana_text.replace(orig, annotated, 1)

    if sentenceHasKanji:
        data_word[item] = furigana_text
        data[item] = f"{original_text} ({furigana.rstrip('|')})"

with open(file + "_translated_word.json", 'w') as f:
    json.dump(data_word, f, indent=4, ensure_ascii=False)

with open(file + "_translated_end.json", 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)