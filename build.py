import json
import os
import re
import urllib.request
import zipfile

import jaconv
from sudachipy import dictionary, tokenizer

# CONFIG
MC_VERSION = "26.3"
PACK_FORMAT = 121
MIN_FORMAT = 15

KANJI_RE = re.compile(r"[\u4E00-\u9FFF々]")
JAPANESE_RUN_RE = re.compile(r"[\u3040-\u309F\u4E00-\u9FFF々]+")
LANG_URL = f"https://assets.mcasset.cloud/{MC_VERSION}/assets/minecraft/lang/ja_jp.json"

PACK_DIR = "Furigana For Japanese"
LANG_DIR = os.path.join(PACK_DIR, "assets", "minecraft", "lang")
ZIP_NAME = "Furigana For Japanese.zip"

sudachi = dictionary.Dictionary(dict="full").create()
SPLIT_MODE = tokenizer.Tokenizer.SplitMode.A


# ---------------------------------------------------------------------------
# Exact phrase overrides
#
# Each value is [(visible surface, hiragana reading), ...].
# Longer matching phrases take priority automatically.
# ---------------------------------------------------------------------------

READING_OVERRIDES = {
    # Counters and contextual readings
    "体のエンティティ": [("体", "たい")],
    "体います": [("体", "たい")],
    "体以下": [("体", "たい")],
    "5体のMob": [("5体", "たい")],
    "2体のファントム": [("2体", "たい")],
    "が入っ": [("入っ", "はいっ")],
    "ひびが入る": [("入る", "はいる")],
    "種を植え": [("種", "たね")],
    "種だらけ": [("種", "たね")],
    "金でピグリン": [("金", "きん")],
    "シュルカーの弾": [("弾", "たま")],
    "サンプリング数": [("数", "すう")],
    "アップグレード済み": [("済み", "ずみ")],
    "トライアル版": [("版", "はん")],
    "ベース型": [("型", "がた")],
    "現在無効": [("現在", "げんざい"), ("無効", "むこう")],
    "最低一回以上": [("最低", "さいてい"), ("一回", "いっかい"), ("以上", "いじょう")],
    "50ブロック以上浮遊": [("以上", "いじょう"), ("浮遊", "ふゆう")],
    "複数体指定": [("複数", "ふくすう"), ("体", "たい"), ("指定", "してい")],

    # Names and UI words
    "サーバー名": [("名", "めい")],
    "エンティティ名": [("名", "めい")],
    "ワールド名": [("名", "めい")],
    "ユーザー名": [("名", "めい")],
    "ホスト名": [("名", "めい")],
    "テンプレート名": [("名", "めい")],
    "単体": [("単体", "たんたい")],
    "当分の間村": [("間", "かん"), ("村", "むら")],
    "音声読み上げ": [("音声読み上げ", "おんせいよみあげ")],
    "自動作業台": [("自動作業台", "じどうさぎょうだい")],
    "心臓移植者": [("心臓移植", "しんぞういしょく"), ("者", "しゃ")],
    "毎回確認": [("毎回確認", "まいかいかくにん")],
    "常時実行": [("常時実行", "じょうじじっこう")],
    "無条件": [("無条件", "むじょうけん")],
    "敵対的": [("敵対的", "てきたいてき")],
    "望遠鏡": [("望遠鏡", "ぼうえんきょう")],
    "黒曜石": [("黒曜石", "こくようせき")],
    "安山岩": [("安山岩", "あんざんがん")],
    "感圧板": [("感圧板", "かんあつばん")],
    "鍛冶型": [("鍛冶", "かじ"), ("型", "がた")],
    "鍛冶": [("鍛冶", "かじ")],

    # Item, block, biome, and effect readings
    "瓶": [("瓶", "びん")],
    "羽音": [("羽音", "はおと")],
    "鎮まる": [("鎮まる", "しずまる")],
    "焦らす": [("焦らす", "じらす")],
    "放つ": [("放つ", "はなつ")],
    "手に入れる": [("手に入れ", "てにいれ")],
    "一石二鳥": [("一石二鳥", "いっせきにちょう")],
    "危機一髪": [("危機一髪", "ききいっぱつ")],
    "熱帯魚": [("熱帯魚", "ねったいぎょ")],
    "蓄風": [("蓄風", "ちくふう")],
    "巣張り": [("巣", "す"), ("張り", "はり")],
    "樽": [("樽", "たる")],
    "カカオの実": [("実", "み")],
    "気泡柱": [("気泡柱", "きほうちゅう")],
    "召雷": [("召雷", "しょうらい")],
    "旋風": [("旋風", "せんぷう")],
    "荒野": [("荒野", "こうや")],
    "高原": [("高原", "こうげん")],
    "山形波": [("山形", "やまがた"), ("波", "なみ")],
    "実が": [("実", "み")],
    "正しく": [("正しく", "ただしく")],
    "日本語用": [("日本語用", "にほんごよう")],
    "ゲーム内": [("ゲーム内", "ない")],

    # Colour policy
    "赤色": [("赤色", "あかいろ")],
    "黒色": [("黒色", "くろいろ")],
    "黄緑色": [("黄緑色", "きみどりいろ")],
    "白色": [("白色", "しろいろ")],

    # Armour trim terminology
    "風の装飾": [("風", "ふう")],
    "鼻風": [("鼻風", "はなふう")],
    "尖塔風": [("尖塔風", "せんとうふう")],
    "監獄風": [("監獄風", "かんごくふう")],
    "潮流風": [("潮流風", "ちょうりゅうふう")],
    "先駆者風": [("先駆者風", "せんくしゃふう")],
    "ヴェックス風": [("風", "ふう")],

    # Common technical compounds
    "互換性": [("互換性", "ごかんせい")],
    "有効化": [("有効化", "ゆうこうか")],
    "無効化": [("無効化", "むこうか")],
    "不可能": [("不可能", "ふかのう")],
    "一時的": [("一時的", "いちじてき")],
    "自動的": [("自動的", "じどうてき")],
    "異方性": [("異方性", "いほうせい")],
    "非表示": [("非表示", "ひひょうじ")],
    "最適化": [("最適化", "さいてきか")],
    "再起動": [("再起動", "さいきどう")],
    "再試行": [("再試行", "さいしこう")],
    "再生成": [("再生成", "さいせいせい")],
    "初期化": [("初期化", "しょきか")],
    "利用規約": [("利用規約", "りようきやく")],
    "管理者": [("管理者", "かんりしゃ")],
    "所有者": [("所有者", "しょゆうしゃ")],
    "保護者": [("保護者", "ほごしゃ")],
    "作成者": [("作成者", "さくせいしゃ")],
    "製作者": [("製作者", "せいさくしゃ")],
    "有効期限": [("有効期限", "ゆうこうきげん")],
    "期限切れ": [("期限切れ", "きげんぎれ")],

    # Calendar and duration words
    "開始日": [("開始日", "かいしび")],
    "日間": [("日間", "にちかん")],
    "日前": [("日前", "にちまえ")],
    "分前": [("分前", "ふんまえ")],
    "ヶ月": [("ヶ月", "かげつ")],
    "か月": [("か月", "かげつ")],

    # Empty UI contexts only; do not globally override 空.
    "空です": [("空", "から")],
    "空にする": [("空", "から")],
    "現在空": [("現在", "げんざい"), ("空", "から")],

        # Remaining lexical corrections
    "その他": [("その他", "ほか")],

    # Empty-state UI readings
    "空です": [("空", "から")],
    "空になる": [("空", "から")],

    # Progress-state 中: ちゅう, not なか
    "ログイン中": [("中", "ちゅう")],
    "ダウンロード中": [("中", "ちゅう")],
    "アップグレード中": [("中", "ちゅう")],
    "最適化中": [("中", "ちゅう")],
    "切り替え中": [("中", "ちゅう")],
    "作成中": [("中", "ちゅう")],
    "保存中": [("中", "ちゅう")],
    "準備中": [("中", "ちゅう")],
    "読み込み中": [("中", "ちゅう")],
    "接続中": [("中", "ちゅう")],
    "処理中": [("中", "ちゅう")],
    "実行中": [("中", "ちゅう")],
    "待機中": [("中", "ちゅう")],
    "保留中": [("中", "ちゅう")],
    "選択中": [("中", "ちゅう")],
    "再構成中": [("中", "ちゅう")],
    "構成中": [("中", "ちゅう")],
    "移動中": [("中", "ちゅう")],
    "開始中": [("中", "ちゅう")],
    "終了中": [("中", "ちゅう")],
    "検証中": [("中", "ちゅう")],
    "送信中": [("中", "ちゅう")],
    "受信中": [("中", "ちゅう")],
    "編集中": [("中", "ちゅう")],
    "生成中": [("中", "ちゅう")],
    "発生中": [("中", "ちゅう")],
    "作動中": [("中", "ちゅう")],
    "適用中": [("中", "ちゅう")],
    "設定中": [("中", "ちゅう")],
    "表示中": [("中", "ちゅう")],
    "参加中": [("中", "ちゅう")],
    "使用中": [("中", "ちゅう")],
    "更新中": [("中", "ちゅう")],
    "充電中": [("中", "ちゅう")],
}

OVERRIDE_PATTERN = re.compile(
    "|".join(
        re.escape(text)
        for text in sorted(READING_OVERRIDES, key=len, reverse=True)
    )
)


# ---------------------------------------------------------------------------
# Key-specific overrides
#
# When a string needs a reading that would be unsafe globally.
# ---------------------------------------------------------------------------

KEY_READING_OVERRIDES = {
    "mco.configure.world.subscription.day": "日(にち)",
    "mco.configure.world.subscription.days": "日(にち)",
    "mco.configure.world.subscription.remaining.days": "%1$s日(にち)",
    "mco.configure.world.subscription.remaining.months.days": "%1$sヶ月(かげつ)%2$s日(にち)",
    "mco.selectServer.expires.day": "あと1日(にち)で期限(きげん)が切れます(きれます)",
    "mco.selectServer.expires.days": "あと%s日(にち)で期限(きげん)が切れます(きれます)",
    "mco.activity.noactivity": "過去(かこ)%s日間(にちかん)のアクティビティはありません",
    "mco.time.daysAgo": "%1$s日前(にちまえ)",
    "mco.time.minutesAgo": "%1$s分前(ふんまえ)",
    "item.minecraft.bundle.empty": "空(から)",
    "mco.configure.world.slot.empty": "空(から)",
    "connect.authorizing": "ログイン中(ちゅう)…",
    "mco.connect.authorizing": "ログイン中(ちゅう)…",
    "mco.download.downloading": "ダウンロード中(ちゅう)",
    "mco.minigame.world.slot.screen.title": "ワールドを切り替え(きりかえ)中(ちゅう)…",
    "optimizeWorld.stage.upgrading": "すべてのチャンクをアップグレード中(ちゅう)…",
    "optimizeWorld.stage.upgrading.chunks": "すべてのチャンクをアップグレード中(ちゅう)…",
    "optimizeWorld.stage.upgrading.entities": "すべてのエンティティをアップグレード中(ちゅう)…",
    "optimizeWorld.stage.upgrading.poi": "すべての関心地点(かんしんちてん)をアップグレード中(ちゅう)…",
    "optimizeWorld.title": "ワールド「%s」を最適化(さいてきか)中(ちゅう)",
    "resourcepack.downloading": "リソースパックをダウンロード中(ちゅう)",
    "resourcepack.progress": "ファイルをダウンロード中(ちゅう)（%sMB）…",
    "upgradeWorld.info.scanning": "ファイルをスキャン中(ちゅう)…",
    "upgradeWorld.progress.type.legacy_structures": "旧型式(きゅうけいしき)の構造(こうぞう)物(ぶつ)をアップグレード中(ちゅう)",
    "upgradeWorld.progress.type.region": "リージョンをアップグレード中(ちゅう)",
    "upgradeWorld.title": "ワールドをアップグレード中(ちゅう)",
    "gui.socialInteractions.status_blocked": "ブロック中(ちゅう)",
    "gui.socialInteractions.status_blocked_offline": "ブロック中(ちゅう) - オフライン",
    "gui.socialInteractions.status_hidden": "非表示(ひひょうじ)中(ちゅう)",
    "gui.socialInteractions.status_hidden_offline": "非表示(ひひょうじ)中(ちゅう) - オフライン",
    "gui.socialInteractions.tab_blocked": "ブロック中(ちゅう)",
    "gui.socialInteractions.tab_hidden": "非表示(ひひょうじ)中(ちゅう)",
    "item.minecraft.lingering_potion.effect.water": (
        "水入り(みずいり)残留(ざんりゅう)瓶(びん)"
    ),
    "mco.snapshot.description": (
        "作成(さくせい)したRealmは%sが有効(ゆうこう)な限り(かぎり)"
        "利用(りよう)できます"
    ),
    "commands.scoreboard.objectives.display.alreadyEmpty": (
        "その表示(ひょうじ)スロットは既に(すでに)空(から)のため、"
        "変更(へんこう)されませんでした"
    ),
    "commands.datapack.create.success": (
        "新しい(あたらしい)空(から)のパックを、名前(なまえ)「%s」として"
        "作成(さくせい)しました"
    ),
    "options.language.empty_or_missing_translation": (
        "翻訳(ほんやく)ファイルにおける%sの翻訳(ほんやく)が空(から)か、"
        "もしくは存在(そんざい)しません。ゲームとランチャーを"
        "再起動(さいきどう)してもう一度(いちど)お試しください(ためしください)。"
    ),
    "snbt.parser.empty_key": "キーは空(から)にできません",
    "test.error.expected_empty_container": "コンテナは空(から)である必要(ひつよう)があります",
}


# ---------------------------------------------------------------------------
# Contextual numeric counters
#
# Handles 10人, %s人, %1$s体, 30日, and similar patterns.
# ---------------------------------------------------------------------------

COUNTER_RE = re.compile(
    r"(?P<prefix>%[0-9$]*s|[0-9０-９]+)(?P<counter>体|人|日)"
)

COUNTER_READINGS = {
    "体": "たい",
    "人": "にん",
    "日": "にち",
}


def get_reading(morpheme):
    value = morpheme.reading_form()

    if not value or value == "*":
        return morpheme.surface()

    return jaconv.kata2hira(value)


def group_morphemes(morphemes):
    """Join noun compounds and one verb's inflection chain only."""
    groups = []
    current = []

    for morpheme in morphemes:
        major = morpheme.part_of_speech()[0]
        surface = morpheme.surface()
        merge = False

        if current:
            previous_major = current[-1].part_of_speech()[0]
            previous_surface = current[-1].surface()

            # Kanji-only compound nouns, avoiding kana-word swallowing.
            if (
                major == "名詞"
                and previous_major == "名詞"
                and KANJI_RE.search(previous_surface)
                and KANJI_RE.search(surface)
            ):
                merge = True

            # Compound verbs such as 読み込む and 考え直す.
            elif major == "動詞" and previous_major == "動詞":
                merge = True

            # Continue a verb's auxiliary chain: ませんでした.
            elif (
                major == "助動詞"
                and any(
                    item.part_of_speech()[0] == "動詞"
                    for item in current
                )
            ):
                merge = True

            # Include て / で in the verb group.
            elif (
                major == "助詞"
                and previous_major in {"動詞", "助動詞"}
                and surface in {"て", "で"}
            ):
                merge = True

        if merge:
            current.append(morpheme)
        else:
            if current:
                groups.append(current)
            current = [morpheme]

    if current:
        groups.append(current)

    return groups


def convert_japanese_run(text):
    parts = []
    readings = []
    has_kanji = False

    for group in group_morphemes(sudachi.tokenize(text, SPLIT_MODE)):
        surface = "".join(morpheme.surface() for morpheme in group)
        reading = "".join(get_reading(morpheme) for morpheme in group)

        if KANJI_RE.search(surface):
            parts.append(f"{surface}({reading})")
            readings.append(reading)
            has_kanji = True
        else:
            parts.append(surface)

    return "".join(parts), readings, has_kanji


def convert_automatic(text):
    """Annotate kanji/hiragana runs; keep Latin, katakana, digits, etc. literal."""
    parts = []
    readings = []
    has_kanji = False
    position = 0

    for match in JAPANESE_RUN_RE.finditer(text):
        parts.append(text[position:match.start()])

        converted, local_readings, local_has_kanji = convert_japanese_run(
            match.group()
        )

        parts.append(converted)
        readings.extend(local_readings)
        has_kanji = has_kanji or local_has_kanji
        position = match.end()

    parts.append(text[position:])

    return "".join(parts), readings, has_kanji


def convert_counters(text):
    """Apply numeric counter readings before ordinary morphological conversion."""
    parts = []
    readings = []
    has_kanji = False
    position = 0

    for match in COUNTER_RE.finditer(text):
        before = text[position:match.start()]

        if before:
            converted, local_readings, local_has_kanji = convert_automatic(before)
            parts.append(converted)
            readings.extend(local_readings)
            has_kanji = has_kanji or local_has_kanji

        prefix = match.group("prefix")
        counter = match.group("counter")
        reading = COUNTER_READINGS[counter]

        parts.append(f"{prefix}{counter}({reading})")
        readings.append(reading)
        has_kanji = True
        position = match.end()

    after = text[position:]

    if after:
        converted, local_readings, local_has_kanji = convert_automatic(after)
        parts.append(converted)
        readings.extend(local_readings)
        has_kanji = has_kanji or local_has_kanji

    return "".join(parts), readings, has_kanji


def convert_override_phrase(phrase, annotations):
    """Apply a phrase override while still converting its remaining text."""
    ordered = sorted(annotations, key=lambda item: len(item[0]), reverse=True)
    pattern = re.compile(
        "|".join(re.escape(surface) for surface, _ in ordered)
    )
    lookup = dict(ordered)

    parts = []
    readings = []
    has_kanji = False
    position = 0

    for match in pattern.finditer(phrase):
        before = phrase[position:match.start()]

        if before:
            converted, local_readings, local_has_kanji = convert_counters(before)
            parts.append(converted)
            readings.extend(local_readings)
            has_kanji = has_kanji or local_has_kanji

        surface = match.group()
        reading = lookup[surface]

        parts.append(f"{surface}({reading})")

        if KANJI_RE.search(surface):
            readings.append(reading)
            has_kanji = True

        position = match.end()

    after = phrase[position:]

    if after:
        converted, local_readings, local_has_kanji = convert_counters(after)
        parts.append(converted)
        readings.extend(local_readings)
        has_kanji = has_kanji or local_has_kanji

    return "".join(parts), readings, has_kanji


def convert_with_overrides(text):
    parts = []
    readings = []
    has_kanji = False
    position = 0

    for match in OVERRIDE_PATTERN.finditer(text):
        before = text[position:match.start()]

        if before:
            converted, local_readings, local_has_kanji = convert_counters(before)
            parts.append(converted)
            readings.extend(local_readings)
            has_kanji = has_kanji or local_has_kanji

        phrase = match.group()

        converted, local_readings, local_has_kanji = convert_override_phrase(
            phrase,
            READING_OVERRIDES[phrase],
        )

        parts.append(converted)
        readings.extend(local_readings)
        has_kanji = has_kanji or local_has_kanji
        position = match.end()

    after = text[position:]

    if after:
        converted, local_readings, local_has_kanji = convert_counters(after)
        parts.append(converted)
        readings.extend(local_readings)
        has_kanji = has_kanji or local_has_kanji

    return "".join(parts), readings, has_kanji



# Make pack

print(f"- Downloading ja_jp.json for MC {MC_VERSION}...")
urllib.request.urlretrieve(LANG_URL, "ja_jp.json")

print("- Translating")

with open("ja_jp.json", encoding="utf-8") as file:
    data = json.load(file)

data_word = data.copy()

for key, source in data.items():
    converted, readings, has_kanji = convert_with_overrides(source)

    if key in KEY_READING_OVERRIDES:
        converted = KEY_READING_OVERRIDES[key]
        has_kanji = True

    if has_kanji:
        data_word[key] = converted
        data[key] = f"{source} ({'|'.join(readings)})"

os.makedirs(LANG_DIR, exist_ok=True)

with open(os.path.join(LANG_DIR, "ja_fw.json"), "w", encoding="utf-8") as file:
    json.dump(data_word, file, indent=4, ensure_ascii=False)

with open(os.path.join(LANG_DIR, "ja_fe.json"), "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print("- Language files written")

mcmeta = {
    "pack": {
        "pack_format": PACK_FORMAT,
        "supported_formats": [MIN_FORMAT, PACK_FORMAT],
        "min_format": MIN_FORMAT,
        "max_format": PACK_FORMAT,
        "description": "Alex's Japanese Furigana Language",
    },
    "language": {
        "ja_fw": {
            "name": "日本語（ふりがな）- Word",
            "region": "日本",
            "bidirectional": False,
        },
        "ja_fe": {
            "name": "日本語（ふりがな）- End",
            "region": "日本",
            "bidirectional": False,
        },
    },
}

with open(os.path.join(PACK_DIR, "pack.mcmeta"), "w", encoding="utf-8") as file:
    json.dump(mcmeta, file, indent=2, ensure_ascii=False)

print("- Pack.mcmeta updated.")

print(f"- Creating {ZIP_NAME}...")

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as archive:
    for root, _, files in os.walk(PACK_DIR):
        for filename in files:
            path = os.path.join(root, filename)
            archive.write(path, os.path.relpath(path, PACK_DIR))

print(f"Done! Pack written in {ZIP_NAME}")