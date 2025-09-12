#!/usr/bin/env python3
"""
発音記号表示版英語発音解析システム
カタカナ変換に加えて、IPA発音記号でも表示
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

def get_word_to_phonetic_dict():
    """単語→IPA発音記号辞書"""
    return {
        # 基本動詞
        "go": "/ɡoʊ/", "come": "/kʌm/", "get": "/ɡɛt/", "take": "/teɪk/", "make": "/meɪk/",
        "do": "/duː/", "have": "/hæv/", "be": "/biː/", "see": "/siː/", "know": "/noʊ/",
        "think": "/θɪŋk/", "say": "/seɪ/", "tell": "/tɛl/", "give": "/ɡɪv/", "want": "/wɑnt/",
        "need": "/niːd/", "like": "/laɪk/", "love": "/lʌv/", "look": "/lʊk/", "hear": "/hɪr/",
        "feel": "/fiːl/", "work": "/wɜrk/", "play": "/pleɪ/", "help": "/hɛlp/", "find": "/faɪnd/",
        "try": "/traɪ/", "use": "/juːz/", "ask": "/æsk/", "call": "/kɔl/", "talk": "/tɔk/",
        "speak": "/spiːk/", "turn": "/tɜrn/", "put": "/pʊt/", "run": "/rʌn/", "walk": "/wɔk/",
        "sit": "/sɪt/", "stand": "/stænd/", "write": "/raɪt/", "read": "/riːd/", "eat": "/iːt/",
        "drink": "/drɪŋk/", "sleep": "/sliːp/", "buy": "/baɪ/", "sell": "/sɛl/", "open": "/oʊpən/",
        "close": "/kloʊz/", "start": "/stɑrt/", "stop": "/stɑp/", "begin": "/bɪɡɪn/", "end": "/ɛnd/",
        
        # 基本名詞
        "time": "/taɪm/", "day": "/deɪ/", "week": "/wiːk/", "month": "/mʌnθ/", "year": "/jɪr/",
        "hour": "/aʊr/", "minute": "/mɪnɪt/", "second": "/sɛkənd/", "morning": "/mɔrnɪŋ/",
        "afternoon": "/æftərˈnuːn/", "evening": "/iːvnɪŋ/", "night": "/naɪt/",
        "today": "/təˈdeɪ/", "tomorrow": "/təˈmɔroʊ/", "yesterday": "/jɛstərdeɪ/",
        "home": "/hoʊm/", "house": "/haʊs/", "room": "/ruːm/", "door": "/dɔr/", "window": "/wɪndoʊ/",
        "water": "/wɔtər/", "food": "/fuːd/", "money": "/mʌni/", "time": "/taɪm/",
        
        # 基本形容詞
        "good": "/ɡʊd/", "bad": "/bæd/", "big": "/bɪɡ/", "small": "/smɔl/", "large": "/lɑrdʒ/",
        "little": "/lɪtəl/", "long": "/lɔŋ/", "short": "/ʃɔrt/", "high": "/haɪ/", "low": "/loʊ/",
        "old": "/oʊld/", "new": "/nuː/", "young": "/jʌŋ/", "hot": "/hɑt/", "cold": "/koʊld/",
        "fast": "/fæst/", "slow": "/sloʊ/", "easy": "/iːzi/", "hard": "/hɑrd/",
        "nice": "/naɪs/", "happy": "/hæpi/", "sad": "/sæd/", "angry": "/æŋɡri/",
        
        # 代名詞・基本語
        "i": "/aɪ/", "you": "/juː/", "he": "/hiː/", "she": "/ʃiː/", "we": "/wiː/", "they": "/ðeɪ/",
        "it": "/ɪt/", "this": "/ðɪs/", "that": "/ðæt/", "my": "/maɪ/", "your": "/jʊr/",
        "the": "/ðə/", "a": "/eɪ/", "an": "/æn/", "and": "/ænd/", "or": "/ɔr/", "but": "/bʌt/",
        "so": "/soʊ/", "because": "/bɪkɔz/", "if": "/ɪf/", "when": "/wɛn/", "where": "/wɛr/",
        "what": "/wʌt/", "who": "/huː/", "why": "/waɪ/", "how": "/haʊ/",
        "yes": "/jɛs/", "no": "/noʊ/", "not": "/nɑt/", "very": "/vɛri/",
        
        # 数字
        "one": "/wʌn/", "two": "/tuː/", "three": "/θriː/", "four": "/fɔr/", "five": "/faɪv/",
        "six": "/sɪks/", "seven": "/sɛvən/", "eight": "/eɪt/", "nine": "/naɪn/", "ten": "/tɛn/",
        
        # よく間違える単語
        "got": "/ɡɑt/", "to": "/tuː/", "going": "/ɡoʊɪŋ/", "gonna": "/ɡʌnə/",
        "want": "/wɑnt/", "wanna": "/wænə/", "gotta": "/ɡɑtə/",
        "really": "/riːəli/", "actually": "/æktʃuəli/", "probably": "/prɑbəbli/",
    }

def get_word_to_katakana_dict():
    """単語→カタカナ辞書（実際の発音重視）"""
    return {
        # 基本動詞
        "go": "ゴウ", "come": "カム", "get": "ゲット", "take": "テイク", "make": "メイク",
        "do": "ドゥー", "have": "ハブ", "be": "ビー", "see": "シー", "know": "ノウ",
        "think": "シンク", "say": "セイ", "tell": "テル", "give": "ギブ", "want": "ワント",
        "need": "ニード", "like": "ライク", "love": "ラブ", "look": "ルック", "hear": "ヒア",
        "feel": "フィール", "work": "ワーク", "play": "プレイ", "help": "ヘルプ", "find": "ファインド",
        "try": "トライ", "use": "ユーズ", "ask": "アスク", "call": "コール", "talk": "トーク",
        "speak": "スピーク", "turn": "ターン", "put": "プット", "run": "ラン", "walk": "ウォーク",
        "sit": "シット", "stand": "スタンド", "write": "ライト", "read": "リード", "eat": "イート",
        "drink": "ドリンク", "sleep": "スリープ", "buy": "バイ", "sell": "セル", "open": "オープン",
        "close": "クロウズ", "start": "スタート", "stop": "ストップ", "begin": "ビギン", "end": "エンド",
        
        # 基本名詞
        "time": "タイム", "day": "デイ", "week": "ウィーク", "month": "マンス", "year": "イヤー",
        "hour": "アワー", "minute": "ミニット", "second": "セカンド", "morning": "モーニング",
        "afternoon": "アフタヌーン", "evening": "イーブニング", "night": "ナイト",
        "today": "トゥデイ", "tomorrow": "トゥモロウ", "yesterday": "イエスタデイ",
        "home": "ホウム", "house": "ハウス", "room": "ルーム", "door": "ドアー", "window": "ウィンドウ",
        "water": "ウォーター", "food": "フード", "money": "マニー",
        
        # 基本形容詞
        "good": "グッド", "bad": "バッド", "big": "ビッグ", "small": "スモール", "large": "ラージ",
        "little": "リトル", "long": "ロング", "short": "ショート", "high": "ハイ", "low": "ロウ",
        "old": "オウルド", "new": "ニュー", "young": "ヤング", "hot": "ハット", "cold": "コウルド",
        "fast": "ファスト", "slow": "スロウ", "easy": "イージー", "hard": "ハード",
        "nice": "ナイス", "happy": "ハッピー", "sad": "サッド", "angry": "アングリー",
        
        # 代名詞・基本語
        "i": "アイ", "you": "ユー", "he": "ヒー", "she": "シー", "we": "ウィー", "they": "ゼイ",
        "it": "イット", "this": "ディス", "that": "ザット", "my": "マイ", "your": "ヨア",
        "the": "ザ", "a": "ア", "an": "アン", "and": "アンド", "or": "オア", "but": "バット",
        "so": "ソウ", "because": "ビコーズ", "if": "イフ", "when": "ウェン", "where": "ウェア",
        "what": "ワット", "who": "フー", "why": "ワイ", "how": "ハウ",
        "yes": "イエス", "no": "ノウ", "not": "ナット", "very": "ベリー",
        
        # 数字
        "one": "ワン", "two": "トゥー", "three": "スリー", "four": "フォー", "five": "ファイブ",
        "six": "シックス", "seven": "セブン", "eight": "エイト", "nine": "ナイン", "ten": "テン",
        
        # 実際の発音重視（縮約形など）
        "got": "ガット", "to": "トゥー", "going": "ゴウイング", "gonna": "ガナ",
        "want": "ワント", "wanna": "ワナ", "gotta": "ガタ",
        "really": "リアリー", "actually": "アクチュアリー", "probably": "プロバブリー",
        
        # 特殊フレーズ用
        "got to": "ガタ", "want to": "ワナ", "going to": "ガナ",
        "what are": "ワラ", "what are you": "ワラユ", "don't know": "ドンノ",
        "i don't": "アイドン", "you know": "ユノ", "kind of": "カイナ",
        "sort of": "ソータ", "a lot of": "アロタ", "out of": "アウタ"
    }

def convert_to_phonetic_symbols(text: str) -> str:
    """英語テキストをIPA発音記号に変換"""
    if not text:
        return "？？？"
    
    print(f"🔤 発音記号変換: '{text}'")
    
    # 辞書を取得
    phonetic_dict = get_word_to_phonetic_dict()
    
    # テキストを小文字化して単語に分割
    words = re.findall(r'\b\w+\b', text.lower())
    phonetic_parts = []
    
    for word in words:
        if word in phonetic_dict:
            ipa = phonetic_dict[word]
            phonetic_parts.append(f"{word}→{ipa}")
            print(f"  '{word}' -> '{ipa}' (IPA辞書)")
        else:
            # 辞書にない場合は推測
            phonetic_parts.append(f"{word}→/推測/")
            print(f"  '{word}' -> /推測/ (辞書なし)")
    
    result = " ".join(phonetic_parts) if phonetic_parts else "？？？"
    print(f"🔤 IPA変換結果: '{result}'")
    return result

def convert_to_katakana(text: str) -> str:
    """英語テキストをカタカナに変換"""
    if not text:
        return "？？？"
    
    print(f"🎌 カタカナ変換: '{text}'")
    
    # まずフレーズレベルで処理
    text_lower = text.lower()
    phrase_conversions = {
        "got to": "ガタ",
        "want to": "ワナ", 
        "going to": "ガナ",
        "what are you": "ワラユ",
        "don't know": "ドンノ",
        "i don't": "アイドン",
        "you know": "ユノ",
        "kind of": "カイナ",
        "sort of": "ソータ",
        "a lot of": "アロタ",
        "out of": "アウタ"
    }
    
    # フレーズ変換
    converted_text = text_lower
    for phrase, katakana in phrase_conversions.items():
        if phrase in converted_text:
            converted_text = converted_text.replace(phrase, katakana)
    
    # 単語レベルの変換
    katakana_dict = get_word_to_katakana_dict()
    words = re.findall(r'\b\w+\b', converted_text)
    katakana_words = []
    
    for word in words:
        # カタカナかどうかチェック
        if re.match(r'^[ァ-ヶー・]+$', word):
            katakana_words.append(word)
        elif word in katakana_dict:
            katakana = katakana_dict[word]
            katakana_words.append(katakana)
            print(f"  '{word}' -> '{katakana}' (カタカナ辞書)")
        else:
            # 辞書にない場合は基本変換
            katakana = basic_phonetic_conversion(word)
            katakana_words.append(katakana)
            print(f"  '{word}' -> '{katakana}' (基本変換)")
    
    result = " ".join(katakana_words) if katakana_words else "？？？"
    print(f"🎌 カタカナ最終結果: '{result}'")
    return result

def basic_phonetic_conversion(word: str) -> str:
    """基本的な音韻変換（辞書にない単語用）"""
    if not word:
        return "？"
    
    # 基本的な英語音素→カタカナ変換
    result = word.lower()
    
    # 子音クラスター（順序重要：長いものから）
    conversions = [
        ("tion", "ション"), ("sion", "ション"), ("ght", "ト"), 
        ("ough", "アフ"), ("aught", "オート"), ("ought", "オート"), ("ight", "アイト"),
        ("th", "ス"), ("sh", "シ"), ("ch", "チ"), ("ph", "フ"), ("wh", "ウ"),
        ("oo", "ウー"), ("ee", "イー"), ("ea", "イー"), ("ai", "エイ"), ("ay", "エイ"),
        ("ou", "アウ"), ("ow", "アウ"), ("oi", "オイ"), ("oy", "オイ"),
        ("er", "アー"), ("ir", "アー"), ("ur", "アー"), ("ar", "アー"),
        ("ng", "ング"), ("nk", "ンク"), ("nt", "ント"), ("nd", "ンド"),
        ("st", "スト"), ("sp", "スプ"), ("sc", "スク"), ("sk", "スク"),
        ("tr", "トル"), ("dr", "ドル"), ("pr", "プル"), ("br", "ブル"),
        ("cr", "クル"), ("gr", "グル"), ("fr", "フル"),
        ("ly", "リー"), ("ty", "ティー"), ("ry", "リー"), ("ny", "ニー"),
        ("a", "ア"), ("e", "エ"), ("i", "イ"), ("o", "オ"), ("u", "ウ"),
        ("b", "ブ"), ("c", "ク"), ("d", "ド"), ("f", "フ"), ("g", "グ"),
        ("h", "ハ"), ("j", "ジ"), ("k", "ク"), ("l", "ル"), ("m", "ム"),
        ("n", "ン"), ("p", "プ"), ("q", "ク"), ("r", "ル"), ("s", "ス"),
        ("t", "ト"), ("v", "ブ"), ("w", "ワ"), ("x", "クス"), ("y", "ヤ"), ("z", "ズ")
    ]
    
    for eng, kata in conversions:
        result = result.replace(eng, kata)
    
    return result if result else "？"

def process_phonetic_symbols_pronunciation(audio_file):
    """発音記号表示版発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", ""
    
    try:
        # Step 1: Whisperで音声認識
        english_text = transcribe_audio(audio_file)
        
        # Step 2: IPA発音記号変換
        phonetic_symbols = convert_to_phonetic_symbols(english_text)
        
        # Step 3: カタカナ変換
        katakana_text = convert_to_katakana(english_text)
        
        return (
            "✅ 発音記号版解析完了",
            english_text.title(),
            phonetic_symbols,
            katakana_text
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", ""

# 発音記号表示版Gradioインターフェース
def create_phonetic_symbols_app():
    with gr.Blocks(
        title="発音記号表示版英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 1000px; margin: 0 auto; }
        .result-box { font-size: 18px; padding: 18px; margin: 12px 0; border-radius: 8px; }
        .katakana-result { 
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
            border: 3px solid #4caf50; 
            font-weight: bold;
            font-size: 22px;
        }
        .phonetic-result { 
            background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
            border: 2px solid #ff9800; 
            font-family: 'Courier New', monospace;
            font-size: 16px;
            line-height: 1.6;
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
        .ipa-badge {
            display: inline-block;
            background: #ff9800;
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
            # 🔤 発音記号表示版英語発音解析
            
            **IPA国際音声記号＋カタカナで実際の発音を表示** <span class="ipa-badge">IPA</span>
            
            発音記号で正確な音を、カタカナで直感的な音を同時に表示
            
            ### 🎯 表示例
            - **英語**: "I want to go"
            - **発音記号**: i→/aɪ/ want→/wɑnt/ to→/tuː/ go→/ɡoʊ/
            - **カタカナ**: アイ ワント トゥー ゴウ
            
            ### 📚 特殊フレーズ
            - "got to" → /ɡɑt tuː/ → 「ガタ」
            - "want to" → /wɑnt tuː/ → 「ワナ」
            - "going to" → /ɡoʊɪŋ tuː/ → 「ガナ」
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
                "🔤 発音記号解析開始",
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
                    label="🔤 IPA発音記号",
                    placeholder="国際音声記号がここに表示されます",
                    elem_classes=["phonetic-result", "result-box"],
                    lines=3
                )
                
                katakana_output = gr.Textbox(
                    label="🎌 カタカナ発音",
                    placeholder="カタカナ発音がここに表示されます",
                    elem_classes=["katakana-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_phonetic_symbols_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, phonetic_output, katakana_output]
            )
            
            gr.Markdown("""
            ---
            ### 🔤 発音記号について
            
            - **IPA記号**: 国際音声記号で正確な発音を表示
            - **カタカナ**: 日本人に分かりやすい音の近似表示
            - **両方表示**: 正確性と理解しやすさを両立
            - **実際発音**: 縮約形や連結音も正確に表示
            
            **用途**: 英語教師の発音指導、学習者の発音チェック
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🔤 発音記号表示版英語発音解析システム 起動中...")
    setup_whisper()
    
    app = create_phonetic_symbols_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7867,
        share=False
    )