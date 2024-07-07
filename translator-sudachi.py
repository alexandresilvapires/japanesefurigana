import json
import pykakasi
from sudachipy import tokenizer
from sudachipy import dictionary
import string
import regex as re

# Used for hiragana detection
def char_is_hiragana(c) -> bool:
    return u'\u3040' <= c <= u'\u309F'
def string_is_hiragana(s: str) -> bool:
    return all(char_is_hiragana(c) for c in s)
def string_is_hiragana_or_whitespace(s: str) -> bool:
    return all(c in string.whitespace or char_is_hiragana(c) for c in s)

# Input json file
file = "test"
#file = "test"

with open(file+".json") as f:
    data = json.load(f)
    data_word = data.copy()

kks = pykakasi.kakasi()

mode = tokenizer.Tokenizer.SplitMode.A
tokenizer_obj = dictionary.Dictionary().create()

pattern = re.compile(r'([\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}]+)', re.UNICODE)

for item in data:

    # For each word in the sentence, we collect all words
    result = [m for m in tokenizer_obj.tokenize(data[item], mode)]
    furigana = ""
    new_data_word = ""

    sentenceHasKanji = False

    # For each word, we check if it has kanji, if it does, we form the new data for the json
    for i in range(0,len(result)):
        wordHasKanji = False

        new_data_word += result[i].surface()

        japaneseHighlight = pattern.sub(r'(\1)', result[i].surface())

        if(result[i].surface() != result[i].reading_form() and not string_is_hiragana_or_whitespace(result[i].surface()) and japaneseHighlight != result[i].surface()):
            wordHasKanji = True
            sentenceHasKanji = True

        if wordHasKanji:
            kata_to_hira = kks.convert(result[i].reading_form())[0]["hira"]

            new_data_word += "("+kata_to_hira+")"

            if(i == len(result)-1): 
                furigana += kata_to_hira
            else:
                furigana += kata_to_hira + "|"

    if sentenceHasKanji:
        data_word[item] = new_data_word
        
        data[item] = data[item] + " (" + furigana + ")"

with open(file+"_translated_word.json", 'w') as f:
    json.dump(data_word, f, indent=4, ensure_ascii=False)

with open(file+"_translated_end.json", 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)