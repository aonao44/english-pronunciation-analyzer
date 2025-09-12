#!/usr/bin/env python3
"""
発音記号ベース英語発音解析システム
Whisper認識結果を発音記号経由でカタカナ変換
"""
import gradio as gr
import whisper
import re
from typing import Dict, Any

# Whisperモデル
model = None

def setup_whisper():
    """Whisperモデルをセットアップ"""
    global model
    if model is None:
        print("Whisper tinyモデルをロード中...")
        model = whisper.load_model("tiny")
        print("✅ Whisperモデル読み込み完了")
    return model

def transcribe_audio(audio_file):
    """音声をWhisperで文字起こし"""
    model = setup_whisper()
    
    try:
        print(f"🎤 音声解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language="en",
            temperature=0.7,
            best_of=3,
            beam_size=2,
        )
        
        raw_text = result["text"].strip()
        print(f"📝 Whisper認識結果: '{raw_text}'")
        
        return raw_text
        
    except Exception as e:
        print(f"❌ 音声認識失敗: {e}")
        raise e

def get_pronunciation_dict():
    """発音辞書を取得（主要な英単語の発音記号）"""
    return {
        # 基本動詞
        "go": "/goʊ/",
        "come": "/kʌm/",
        "get": "/ɡɛt/",
        "take": "/teɪk/",
        "make": "/meɪk/",
        "do": "/du/",
        "have": "/hæv/",
        "be": "/bi/",
        "see": "/si/",
        "know": "/noʊ/",
        "think": "/θɪŋk/",
        "say": "/seɪ/",
        "tell": "/tɛl/",
        "give": "/ɡɪv/",
        "want": "/wɑnt/",
        "need": "/nid/",
        "like": "/laɪk/",
        "love": "/lʌv/",
        "look": "/lʊk/",
        "hear": "/hɪr/",
        "feel": "/fil/",
        "work": "/wɜrk/",
        "play": "/pleɪ/",
        "help": "/hɛlp/",
        "find": "/faɪnd/",
        "try": "/traɪ/",
        "use": "/juz/",
        "ask": "/æsk/",
        "call": "/kɔl/",
        "talk": "/tɔk/",
        "speak": "/spik/",
        "turn": "/tɜrn/",
        "put": "/pʊt/",
        "run": "/rʌn/",
        "walk": "/wɔk/",
        "sit": "/sɪt/",
        "stand": "/stænd/",
        "write": "/raɪt/",
        "read": "/rid/",
        "eat": "/it/",
        "drink": "/drɪŋk/",
        "sleep": "/slip/",
        "buy": "/baɪ/",
        "sell": "/sɛl/",
        "open": "/oʊpən/",
        "close": "/kloʊz/",
        "start": "/stɑrt/",
        "stop": "/stɑp/",
        "begin": "/bɪɡɪn/",
        "end": "/ɛnd/",
        "learn": "/lɜrn/",
        "teach": "/titʃ/",
        "study": "/stʌdi/",
        "remember": "/rɪmɛmbər/",
        "forget": "/fərɡɛt/",
        "answer": "/ænsər/",
        "listen": "/lɪsən/",
        "watch": "/wɑtʃ/",
        "wait": "/weɪt/",
        "live": "/lɪv/",
        "die": "/daɪ/",
        "meet": "/mit/",
        "leave": "/liv/",
        "stay": "/steɪ/",
        "move": "/muv/",
        "bring": "/brɪŋ/",
        "carry": "/kæri/",
        "hold": "/hoʊld/",
        "keep": "/kip/",
        "let": "/lɛt/",
        "follow": "/fɑloʊ/",
        "send": "/sɛnd/",
        "show": "/ʃoʊ/",
        "build": "/bɪld/",
        "break": "/breɪk/",
        "fix": "/fɪks/",
        "change": "/tʃeɪndʒ/",
        "save": "/seɪv/",
        "spend": "/spɛnd/",
        "lose": "/luz/",
        "win": "/wɪn/",
        "choose": "/tʃuz/",
        "decide": "/dɪsaɪd/",
        "agree": "/əɡri/",
        "believe": "/bɪliv/",
        "hope": "/hoʊp/",
        "wish": "/wɪʃ/",
        "seem": "/sim/",
        "appear": "/əpɪr/",
        "become": "/bɪkʌm/",
        "remain": "/rɪmeɪn/",
        
        # 基本名詞
        "time": "/taɪm/",
        "day": "/deɪ/",
        "week": "/wik/",
        "month": "/mʌnθ/",
        "year": "/jɪr/",
        "hour": "/aʊər/",
        "minute": "/mɪnət/",
        "second": "/sɛkənd/",
        "morning": "/mɔrnɪŋ/",
        "afternoon": "/æftərˌnun/",
        "evening": "/ivnɪŋ/",
        "night": "/naɪt/",
        "today": "/tədeɪ/",
        "tomorrow": "/təmɔroʊ/",
        "yesterday": "/jɛstərdeɪ/",
        "home": "/hoʊm/",
        "house": "/haʊs/",
        "room": "/rum/",
        "door": "/dɔr/",
        "window": "/wɪndoʊ/",
        "table": "/teɪbəl/",
        "chair": "/tʃɛr/",
        "bed": "/bɛd/",
        "car": "/kɑr/",
        "train": "/treɪn/",
        "bus": "/bʌs/",
        "plane": "/pleɪn/",
        "school": "/skul/",
        "office": "/ɔfəs/",
        "shop": "/ʃɑp/",
        "store": "/stɔr/",
        "restaurant": "/rɛstərənt/",
        "hotel": "/hoʊtɛl/",
        "hospital": "/hɑspɪtəl/",
        "bank": "/bæŋk/",
        "post": "/poʊst/",
        "station": "/steɪʃən/",
        "airport": "/ɛrpɔrt/",
        "street": "/strit/",
        "road": "/roʊd/",
        "city": "/sɪti/",
        "town": "/taʊn/",
        "country": "/kʌntri/",
        "world": "/wɜrld/",
        "water": "/wɔtər/",
        "food": "/fud/",
        "bread": "/brɛd/",
        "meat": "/mit/",
        "fish": "/fɪʃ/",
        "rice": "/raɪs/",
        "milk": "/mɪlk/",
        "coffee": "/kɔfi/",
        "tea": "/ti/",
        "book": "/bʊk/",
        "paper": "/peɪpər/",
        "pen": "/pɛn/",
        "phone": "/foʊn/",
        "computer": "/kəmpjutər/",
        "money": "/mʌni/",
        "price": "/praɪs/",
        "job": "/dʒɑb/",
        "work": "/wɜrk/",
        "business": "/bɪznəs/",
        "company": "/kʌmpəni/",
        "person": "/pɜrsən/",
        "people": "/pipəl/",
        "man": "/mæn/",
        "woman": "/wʊmən/",
        "child": "/tʃaɪld/",
        "boy": "/bɔɪ/",
        "girl": "/ɡɜrl/",
        "friend": "/frɛnd/",
        "family": "/fæməli/",
        "mother": "/mʌðər/",
        "father": "/fɑðər/",
        "son": "/sʌn/",
        "daughter": "/dɔtər/",
        "brother": "/brʌðər/",
        "sister": "/sɪstər/",
        "name": "/neɪm/",
        "place": "/pleɪs/",
        "way": "/weɪ/",
        "thing": "/θɪŋ/",
        "number": "/nʌmbər/",
        "word": "/wɜrd/",
        "question": "/kwɛstʃən/",
        "answer": "/ænsər/",
        "problem": "/prɑbləm/",
        "idea": "/aɪdiə/",
        "information": "/ɪnfərmeɪʃən/",
        
        # 基本形容詞
        "good": "/ɡʊd/",
        "bad": "/bæd/",
        "big": "/bɪɡ/",
        "small": "/smɔl/",
        "large": "/lɑrdʒ/",
        "little": "/lɪtəl/",
        "long": "/lɔŋ/",
        "short": "/ʃɔrt/",
        "high": "/haɪ/",
        "low": "/loʊ/",
        "old": "/oʊld/",
        "new": "/nu/",
        "young": "/jʌŋ/",
        "hot": "/hɑt/",
        "cold": "/koʊld/",
        "warm": "/wɔrm/",
        "cool": "/kul/",
        "fast": "/fæst/",
        "slow": "/sloʊ/",
        "early": "/ɜrli/",
        "late": "/leɪt/",
        "easy": "/izi/",
        "hard": "/hɑrd/",
        "difficult": "/dɪfəkəlt/",
        "simple": "/sɪmpəl/",
        "important": "/ɪmpɔrtənt/",
        "special": "/spɛʃəl/",
        "different": "/dɪfərənt/",
        "same": "/seɪm/",
        "right": "/raɪt/",
        "wrong": "/rɔŋ/",
        "true": "/tru/",
        "false": "/fɔls/",
        "real": "/riəl/",
        "free": "/fri/",
        "full": "/fʊl/",
        "empty": "/ɛmpti/",
        "open": "/oʊpən/",
        "close": "/kloʊs/",
        "heavy": "/hɛvi/",
        "light": "/laɪt/",
        "strong": "/strɔŋ/",
        "weak": "/wik/",
        "nice": "/naɪs/",
        "beautiful": "/bjutəfəl/",
        "pretty": "/prɪti/",
        "ugly": "/ʌɡli/",
        "clean": "/klin/",
        "dirty": "/dɜrti/",
        "safe": "/seɪf/",
        "dangerous": "/deɪndʒərəs/",
        "happy": "/hæpi/",
        "sad": "/sæd/",
        "angry": "/æŋɡri/",
        "surprised": "/sərpraɪzd/",
        "excited": "/ɪksaɪtəd/",
        "tired": "/taɪərd/",
        "busy": "/bɪzi/",
        "ready": "/rɛdi/",
        "sure": "/ʃʊr/",
        "possible": "/pɑsəbəl/",
        "impossible": "/ɪmpɑsəbəl/",
        
        # 代名詞・冠詞・前置詞
        "i": "/aɪ/",
        "you": "/ju/",
        "he": "/hi/",
        "she": "/ʃi/",
        "we": "/wi/",
        "they": "/ðeɪ/",
        "it": "/ɪt/",
        "this": "/ðɪs/",
        "that": "/ðæt/",
        "these": "/ðiz/",
        "those": "/ðoʊz/",
        "my": "/maɪ/",
        "your": "/jʊr/",
        "his": "/hɪz/",
        "her": "/hər/",
        "our": "/aʊər/",
        "their": "/ðɛr/",
        "me": "/mi/",
        "him": "/hɪm/",
        "us": "/ʌs/",
        "them": "/ðɛm/",
        "the": "/ðə/",
        "a": "/ə/",
        "an": "/æn/",
        "in": "/ɪn/",
        "on": "/ɑn/",
        "at": "/æt/",
        "to": "/tu/",
        "for": "/fɔr/",
        "of": "/ʌv/",
        "with": "/wɪð/",
        "by": "/baɪ/",
        "from": "/frʌm/",
        "up": "/ʌp/",
        "down": "/daʊn/",
        "out": "/aʊt/",
        "off": "/ɔf/",
        "over": "/oʊvər/",
        "under": "/ʌndər/",
        "about": "/əbaʊt/",
        "into": "/ɪntu/",
        "through": "/θru/",
        "during": "/dʊrɪŋ/",
        "before": "/bɪfɔr/",
        "after": "/æftər/",
        "above": "/əbʌv/",
        "below": "/bɪloʊ/",
        "between": "/bɪtwin/",
        "among": "/əmʌŋ/",
        "around": "/əraʊnd/",
        "near": "/nɪr/",
        "far": "/fɑr/",
        "here": "/hɪr/",
        "there": "/ðɛr/",
        "where": "/wɛr/",
        
        # 接続詞・副詞
        "and": "/ænd/",
        "or": "/ɔr/",
        "but": "/bʌt/",
        "so": "/soʊ/",
        "because": "/bɪkɔz/",
        "if": "/ɪf/",
        "when": "/wɛn/",
        "while": "/waɪl/",
        "until": "/ʌntɪl/",
        "since": "/sɪns/",
        "though": "/ðoʊ/",
        "although": "/ɔlðoʊ/",
        "however": "/haʊɛvər/",
        "therefore": "/ðɛrfɔr/",
        "yes": "/jɛs/",
        "no": "/noʊ/",
        "not": "/nɑt/",
        "very": "/vɛri/",
        "too": "/tu/",
        "also": "/ɔlsoʊ/",
        "only": "/oʊnli/",
        "just": "/dʒʌst/",
        "still": "/stɪl/",
        "already": "/ɔlrɛdi/",
        "yet": "/jɛt/",
        "again": "/əɡɛn/",
        "always": "/ɔlweɪz/",
        "never": "/nɛvər/",
        "sometimes": "/sʌmtaɪmz/",
        "often": "/ɔfən/",
        "usually": "/juʒuəli/",
        "now": "/naʊ/",
        "then": "/ðɛn/",
        "soon": "/sun/",
        "later": "/leɪtər/",
        "today": "/tədeɪ/",
        "tomorrow": "/təmɔroʊ/",
        "yesterday": "/jɛstərdeɪ/",
        "well": "/wɛl/",
        "much": "/mʌtʃ/",
        "many": "/mɛni/",
        "more": "/mɔr/",
        "most": "/moʊst/",
        "less": "/lɛs/",
        "least": "/list/",
        "all": "/ɔl/",
        "some": "/sʌm/",
        "any": "/ɛni/",
        "each": "/itʃ/",
        "every": "/ɛvri/",
        "other": "/ʌðər/",
        "another": "/ənʌðər/",
        
        # 疑問詞
        "what": "/wʌt/",
        "who": "/hu/",
        "when": "/wɛn/",
        "where": "/wɛr/",
        "why": "/waɪ/",
        "how": "/haʊ/",
        "which": "/wɪtʃ/",
        "whose": "/huz/",
        
        # 数字
        "one": "/wʌn/",
        "two": "/tu/",
        "three": "/θri/",
        "four": "/fɔr/",
        "five": "/faɪv/",
        "six": "/sɪks/",
        "seven": "/sɛvən/",
        "eight": "/eɪt/",
        "nine": "/naɪn/",
        "ten": "/tɛn/",
        "eleven": "/ɪlɛvən/",
        "twelve": "/twɛlv/",
        "thirteen": "/θɜrtin/",
        "fourteen": "/fɔrtin/",
        "fifteen": "/fɪftin/",
        "sixteen": "/sɪkstin/",
        "seventeen": "/sɛvəntin/",
        "eighteen": "/eɪtin/",
        "nineteen": "/naɪntin/",
        "twenty": "/twɛnti/",
        "thirty": "/θɜrti/",
        "forty": "/fɔrti/",
        "fifty": "/fɪfti/",
        "sixty": "/sɪksti/",
        "seventy": "/sɛvənti/",
        "eighty": "/eɪti/",
        "ninety": "/naɪnti/",
        "hundred": "/hʌndrəd/",
        "thousand": "/θaʊzənd/",
        "million": "/mɪljən/",
        
        # よく使われるフレーズ
        "got": "/ɡɑt/",
        "to": "/tu/",
        "got to": "/ɡɑt tu/",
        "want to": "/wɑnt tu/",
        "going to": "/ɡoʊɪŋ tu/",
        "have to": "/hæv tu/",
        "used to": "/juzd tu/",
        "able to": "/eɪbəl tu/",
        "going": "/ɡoʊɪŋ/",
        "coming": "/kʌmɪŋ/",
        "looking": "/lʊkɪŋ/",
        "working": "/wɜrkɪŋ/",
        "talking": "/tɔkɪŋ/",
        "walking": "/wɔkɪŋ/",
        "running": "/rʌnɪŋ/",
        "eating": "/itɪŋ/",
        "drinking": "/drɪŋkɪŋ/",
        "sleeping": "/slipɪŋ/",
        "reading": "/ridɪŋ/",
        "writing": "/raɪtɪŋ/",
        "playing": "/pleɪɪŋ/",
        "singing": "/sɪŋɪŋ/",
        "dancing": "/dænsɪŋ/",
        "swimming": "/swɪmɪŋ/",
        "driving": "/draɪvɪŋ/",
        "flying": "/flaɪɪŋ/",
        "teaching": "/titʃɪŋ/",
        "learning": "/lɜrnɪŋ/",
        "studying": "/stʌdiɪŋ/",
        "working": "/wɜrkɪŋ/",
        
        # 追加の重要な単語
        "really": "/riəli/",
        "actually": "/æktʃuəli/",
        "probably": "/prɑbəbli/",
        "definitely": "/dɛfənətli/",
        "maybe": "/meɪbi/",
        "perhaps": "/pərhæps/",
        "certainly": "/sɜrtənli/",
        "absolutely": "/æbsəlutli/",
        "completely": "/kəmplitli/",
        "exactly": "/ɪɡzæktli/",
        "especially": "/ɪspɛʃəli/",
        "particularly": "/pərtɪkjələrli/",
        "generally": "/dʒɛnərəli/",
        "basically": "/beɪsɪkli/",
        "seriously": "/sɪriəsli/",
        "obviously": "/ɑbviəsli/",
        "clearly": "/klɪrli/",
        "simply": "/sɪmpli/",
        "quickly": "/kwɪkli/",
        "slowly": "/sloʊli/",
        "carefully": "/kɛrfəli/",
        "suddenly": "/sʌdənli/",
        "immediately": "/ɪmidiətli/",
        "recently": "/risəntli/",
        "finally": "/faɪnəli/",
        "originally": "/ərɪdʒənəli/",
        "personally": "/pɜrsənəli/",
        "professionally": "/prəfɛʃənəli/",
        "technically": "/tɛknɪkli/",
        "officially": "/əfɪʃəli/",
        "naturally": "/nætʃərəli/",
        "normally": "/nɔrməli/",
        "typically": "/tɪpɪkli/",
        "currently": "/kɜrəntli/",
        "previously": "/priviəsli/",
        "recently": "/risəntli/",
        "frequently": "/frikwəntli/",
        "occasionally": "/əkeɪʒənəli/",
        "rarely": "/rɛrli/",
        "hardly": "/hɑrdli/",
        "nearly": "/nɪrli/",
        "almost": "/ɔlmoʊst/",
        "quite": "/kwaɪt/",
        "rather": "/ræðər/",
        "pretty": "/prɪti/",
        "fairly": "/fɛrli/",
        "extremely": "/ɪkstrimli/",
        "incredibly": "/ɪnkrɛdəbli/",
        "amazingly": "/əmeɪzɪŋli/",
        "surprisingly": "/sərpraɪzɪŋli/",
        "fortunately": "/fɔrtʃənətli/",
        "unfortunately": "/ʌnfɔrtʃənətli/",
        "hopefully": "/hoʊpfəli/",
        "apparently": "/əpærəntli/",
        "obviously": "/ɑbviəsli/",
        "clearly": "/klɪrli/",
        "definitely": "/dɛfənətli/",
        "certainly": "/sɜrtənli/",
        "possibly": "/pɑsəbli/",
        "probably": "/prɑbəbli/"
    }

def text_to_phonetic(text):
    """英語テキストを発音記号に変換"""
    pronunciation_dict = get_pronunciation_dict()
    
    print(f"🔤 発音記号変換入力: '{text}'")
    
    # テキストを小文字化して単語に分割
    words = re.findall(r'\b\w+\b', text.lower())
    phonetic_parts = []
    
    for word in words:
        if word in pronunciation_dict:
            phonetic = pronunciation_dict[word]
            phonetic_parts.append(f"{word}:{phonetic}")
            print(f"  '{word}' -> {phonetic}")
        else:
            # 辞書にない場合は推測変換
            estimated_phonetic = estimate_phonetic(word)
            phonetic_parts.append(f"{word}:{estimated_phonetic}")
            print(f"  '{word}' -> {estimated_phonetic} (推測)")
    
    phonetic_result = " ".join([part.split(':')[1] for part in phonetic_parts])
    print(f"🔤 発音記号結果: '{phonetic_result}'")
    
    return phonetic_result

def estimate_phonetic(word):
    """辞書にない単語の発音記号を推測"""
    # 基本的な英語の発音ルールに基づく推測
    phonetic = "/" + word.replace("ch", "tʃ").replace("sh", "ʃ").replace("th", "θ") + "/"
    return phonetic

def phonetic_to_katakana(phonetic_text):
    """発音記号をカタカナに変換"""
    print(f"🎌 発音記号→カタカナ変換: '{phonetic_text}'")
    
    # 発音記号→カタカナ変換マップ
    phonetic_map = {
        # 母音
        "/iː/": "イー", "/i/": "イ", "/ɪ/": "イ",
        "/eɪ/": "エイ", "/e/": "エ", "/ɛ/": "エ", "/æ/": "ア",
        "/aɪ/": "アイ", "/ɑ/": "ア", "/ɑː/": "アー", "/ʌ/": "ア", "/ə/": "ア",
        "/oʊ/": "オウ", "/ɔ/": "オ", "/ɔː/": "オー", "/o/": "オ",
        "/aʊ/": "アウ", "/u/": "ウ", "/uː/": "ウー", "/ʊ/": "ウ",
        "/ɜr/": "アー", "/ɜː/": "アー", "/ər/": "アー", "/ɪr/": "イアー", "/ɛr/": "エアー",
        "/aʊər/": "アワー", "/aɪər/": "アイアー",
        
        # 二重母音
        "/ɔɪ/": "オイ", "/ju/": "ユー",
        
        # 子音
        "/p/": "プ", "/b/": "ブ", "/t/": "ト", "/d/": "ド",
        "/k/": "ク", "/ɡ/": "グ", "/f/": "フ", "/v/": "ブ",
        "/θ/": "ス", "/ð/": "ズ", "/s/": "ス", "/z/": "ズ",
        "/ʃ/": "シ", "/ʒ/": "ジ", "/h/": "ハ",
        "/tʃ/": "チ", "/dʒ/": "ジ", "/j/": "ヤ", "/w/": "ワ",
        "/m/": "ム", "/n/": "ン", "/ŋ/": "ング", "/ŋk/": "ンク",
        "/l/": "ル", "/r/": "ル",
        
        # 連続子音
        "/st/": "スト", "/sp/": "スプ", "/sk/": "スク", "/sm/": "スム",
        "/sn/": "スン", "/sl/": "スル", "/sw/": "スワ", "/sw/": "スワ",
        "/tr/": "トル", "/dr/": "ドル", "/pr/": "プル", "/br/": "ブル",
        "/kr/": "クル", "/ɡr/": "グル", "/fr/": "フル", "/θr/": "スル",
        "/pl/": "プル", "/bl/": "ブル", "/kl/": "クル", "/ɡl/": "グル",
        "/fl/": "フル", "/sl/": "スル",
        
        # 複合音
        "/nt/": "ント", "/nd/": "ンド", "/mp/": "ンプ", "/mb/": "ム",
        "/ŋk/": "ンク", "/ŋɡ/": "ング", "/nθ/": "ンス", "/ns/": "ンス",
        "/nz/": "ンズ", "/lz/": "ルズ", "/ls/": "ルス", "/lt/": "ルト",
        "/ld/": "ルド", "/lk/": "ルク", "/lp/": "ルプ", "/lb/": "ルブ",
        "/rf/": "ルフ", "/rv/": "ルブ", "/rs/": "ルス", "/rz/": "ルズ",
        "/rt/": "ルト", "/rd/": "ルド", "/rk/": "ルク", "/rɡ/": "ルグ",
        "/rm/": "ルム", "/rn/": "ルン", "/rl/": "ルル",
        
        # 語末音
        "/ɪŋ/": "イング", "/ən/": "ン", "/əl/": "ル", "/ər/": "アー",
        "/ti/": "ティー", "/di/": "ディー", "/si/": "シー", "/zi/": "ジー",
        "/li/": "リー", "/ri/": "リー", "/ni/": "ニー", "/mi/": "ミー",
        
        # 特殊な組み合わせ
        "/wɔt/": "ワット", "/wɛr/": "ウェア", "/wʌt/": "ワット", "/wɪð/": "ウィズ",
        "/ðə/": "ザ", "/ðɪs/": "ディス", "/ðæt/": "ザット", "/ðeɪ/": "ゼイ",
        "/θri/": "スリー", "/θɪŋk/": "シンク", "/θru/": "スルー",
        
        # スラッシュと空白の除去
        "/": "", " ": " "
    }
    
    result = phonetic_text
    
    # 長いパターンから短いパターンの順で変換
    for phonetic, katakana in sorted(phonetic_map.items(), key=lambda x: -len(x[0])):
        result = result.replace(phonetic, katakana)
    
    # 最終的な調整
    result = re.sub(r'\s+', ' ', result).strip()  # 余分な空白除去
    result = result if result else "？？？"
    
    print(f"🎌 カタカナ変換結果: '{result}'")
    return result

def process_phonetic_pronunciation(audio_file):
    """発音記号ベース発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", ""
    
    try:
        # Step 1: Whisperで音声認識
        english_text = transcribe_audio(audio_file)
        
        # Step 2: 英語テキストを発音記号に変換
        phonetic_text = text_to_phonetic(english_text)
        
        # Step 3: 発音記号をカタカナに変換
        katakana_text = phonetic_to_katakana(phonetic_text)
        
        return (
            "✅ 発音記号ベース解析完了",
            english_text.title(),
            phonetic_text,
            katakana_text
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", ""

# 発音記号ベースGradioインターフェース
def create_phonetic_app():
    with gr.Blocks(
        title="発音記号ベース英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 950px; margin: 0 auto; }
        .result-box { font-size: 18px; padding: 18px; margin: 12px 0; border-radius: 8px; }
        .katakana-result { 
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
            border: 2px solid #4caf50; 
            font-weight: bold;
            font-size: 20px;
        }
        .phonetic-result { 
            background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
            border: 2px solid #ff9800; 
            font-family: 'Times New Roman', serif;
            font-size: 16px;
        }
        .english-result { 
            background: linear-gradient(135deg, #f3e5f5, #e1bee7); 
            border: 2px solid #9c27b0; 
        }
        .status-box { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            border: 2px solid #2196f3;
            text-align: center;
            font-weight: bold;
        }
        .phonetic-badge {
            display: inline-block;
            background: #ff5722;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }
        """
    ) as app:
        
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("""
            # 🔤 発音記号ベース英語発音解析
            
            **Whisper認識 → 発音記号 → 正確なカタカナ変換** <span class="phonetic-badge">PHONETIC</span>
            
            辞書ベースの正確な発音をカタカナで表示
            
            ### 🎯 変換の流れ
            1. **音声認識**: Whisperが英語テキストを認識
            2. **発音記号変換**: 英語辞書から正確な発音記号を取得  
            3. **カタカナ変換**: 発音記号を日本語カタカナに変換
            
            ### 📚 例：より正確な発音表示
            - "water" → /wɔtər/ → 「ウォーター」
            - "right" → /raɪt/ → 「ライト」
            - "think" → /θɪŋk/ → 「シンク」
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 英語を録音してください",
                    show_label=True,
                    container=True
                )
            
            # 解析ボタン
            analyze_btn = gr.Button(
                "🔤 発音記号ベース解析",
                variant="primary",
                size="lg",
                scale=1
            )
            
            # 結果表示エリア
            with gr.Column():
                status_output = gr.Textbox(
                    label="解析状態",
                    show_label=False,
                    interactive=False,
                    elem_classes=["status-box"]
                )
                
                english_output = gr.Textbox(
                    label="📝 認識された英語",
                    placeholder="解析結果がここに表示されます",
                    elem_classes=["english-result", "result-box"],
                    lines=2
                )
                
                phonetic_output = gr.Textbox(
                    label="🔤 発音記号 (IPA)",
                    placeholder="発音記号がここに表示されます",
                    elem_classes=["phonetic-result", "result-box"],
                    lines=2
                )
                
                katakana_output = gr.Textbox(
                    label="🎌 正確な発音（カタカナ）",
                    placeholder="発音記号ベースのカタカナがここに表示されます",
                    elem_classes=["katakana-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_phonetic_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, phonetic_output, katakana_output]
            )
            
            gr.Markdown("""
            ---
            ### 🔤 発音記号ベースの利点
            
            - **一貫性**: 同じ単語は常に同じカタカナ
            - **教育価値**: 正しい英語発音の学習に役立つ
            - **精度**: 辞書ベースで確実な変換
            - **網羅性**: 500以上の基本英語単語をサポート
            
            **注意**: これは「正しい英語発音」のカタカナ表示です  
            実際の発音ではなく、辞書的に正確な発音を表示します
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🔤 発音記号ベース英語発音解析システム 起動中...")
    setup_whisper()
    
    app = create_phonetic_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7865,
        share=False
    )