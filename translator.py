import json
import pykakasi

# Input json file
file = "ja_jp"
#file = "test"

with open(file+".json") as f:
    data = json.load(f)
    data_word = data.copy()

kks = pykakasi.kakasi()

print(kks.convert("カタカナ")[0]["hira"])

for item in data:

    # For each word in the sentence, we collect all kana
    result = kks.convert(data[item])
    furigana = ""
    new_data_word = ""


    sentenceHasKanji = False

    for i in range(0,len(result)):
        wordHasKanji = False

        new_data_word += result[i]["orig"]

        if(result[i]["orig"] != result[i]['hira'] and result[i]["orig"] != result[i]['kana'] and result[i]["orig"] != result[i]['hepburn']):
            wordHasKanji = True
            sentenceHasKanji = True

        if wordHasKanji:
            new_data_word += "("+result[i]['hira']+")"

            if(i == len(result)-1): 
                furigana += result[i]['hira']
            else:
                furigana += result[i]['hira'] + "|"

    if sentenceHasKanji:
        data_word[item] = new_data_word
        
        data[item] = data[item] + " (" + furigana + ")"

with open(file+"_translated_word.json", 'w') as f:
    json.dump(data_word, f, indent=4, ensure_ascii=False)

with open(file+"_translated_end.json", 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)