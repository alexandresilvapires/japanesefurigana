import json
import pykakasi
import re
import urllib.request
import zipfile
import os

# CONFIG
MC_VERSION  = "26.2"
PACK_FORMAT = 88
MIN_FORMAT  = 15

# ----------------------------

KANJI_RE = re.compile(r'[\u4e00-\u9FFF]')
LANG_URL  = f"https://assets.mcasset.cloud/{MC_VERSION}/assets/minecraft/lang/ja_jp.json"
PACK_DIR  = "Furigana For Japanese"
LANG_DIR  = os.path.join(PACK_DIR, "assets", "minecraft", "lang")
ZIP_NAME  = "Furigana For Japanese.zip"

# download
print(f"- Downloading ja_jp.json for MC {MC_VERSION}...")
urllib.request.urlretrieve(LANG_URL, "ja_jp.json")

# translate
print("- Translating")
with open("ja_jp.json") as f:
    data = json.load(f)
    data_word = data.copy()

kks = pykakasi.kakasi()

for item in data:
    original_text = data[item]
    result = kks.convert(original_text)

    sentenceHasKanji = False
    furigana_text = original_text
    furigana = ""
    replacements = []

    for token in result:
        orig = token["orig"]
        hira = token["hira"]
        if KANJI_RE.search(orig):
            sentenceHasKanji = True
            replacements.append((orig, f"{orig}({hira})"))
            furigana += hira + "|"

    for orig, annotated in replacements:
        furigana_text = furigana_text.replace(orig, annotated, 1)

    if sentenceHasKanji:
        data_word[item] = furigana_text
        data[item] = f"{original_text} ({furigana.rstrip('|')})"

# write lang files in pack
os.makedirs(LANG_DIR, exist_ok=True)

with open(os.path.join(LANG_DIR, "ja_fw.json"), "w") as f:
    json.dump(data_word, f, indent=4, ensure_ascii=False)

with open(os.path.join(LANG_DIR, "ja_fe.json"), "w") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("- Language files written")

# 4. Update pack.mcmeta
mcmeta = {
    "pack": {
        "pack_format": PACK_FORMAT,
        "supported_formats": [MIN_FORMAT, PACK_FORMAT],
        "min_format": MIN_FORMAT,
        "max_format": PACK_FORMAT,
        "description": "Alex's Japanese Furigana Language"
    },
    "language": {
        "ja_fw": {
            "name": "日本語（ふりがな）- Word",
            "region": "日本",
            "bidirectional": False
        },
        "ja_fe": {
            "name": "日本語（ふりがな）- End",
            "region": "日本",
            "bidirectional": False
        }
    }
}

with open(os.path.join(PACK_DIR, "pack.mcmeta"), "w") as f:
    json.dump(mcmeta, f, indent=2, ensure_ascii=False)

print("- Pack.mcmeta updated.")

# 5. Zip (files sit at root of zip, not inside a subfolder)
print(f"- Creating {ZIP_NAME}...")
with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PACK_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, PACK_DIR)
            zf.write(file_path, arcname)

print(f"Done! Pack written in {ZIP_NAME}")