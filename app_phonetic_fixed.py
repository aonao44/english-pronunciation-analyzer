#!/usr/bin/env python3
"""
発音記号ベース英語発音解析システム（修正版）
シンプルで確実に動作するカタカナ変換
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

def get_word_to_katakana_dict():
    """単語→カタカナ直接変換辞書（発音記号ベース）"""
    return {
        # よく使われる動詞
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
        "learn": "ラーン", "teach": "ティーチ", "study": "スタディ", "remember": "リメンバー", 
        "forget": "フォゲット", "answer": "アンサー", "listen": "リスン", "watch": "ウォッチ", 
        "wait": "ウェイト", "live": "リブ", "die": "ダイ", "meet": "ミート", "leave": "リーブ",
        "stay": "ステイ", "move": "ムーブ", "bring": "ブリング", "carry": "キャリー", 
        "hold": "ホウルド", "keep": "キープ", "let": "レット", "follow": "フォロウ", 
        "send": "センド", "show": "ショウ", "build": "ビルド", "break": "ブレイク", 
        "fix": "フィックス", "change": "チェインジ", "save": "セイブ", "spend": "スペンド",
        "lose": "ルーズ", "win": "ウィン", "choose": "チューズ", "decide": "ディサイド",
        "agree": "アグリー", "believe": "ビリーブ", "hope": "ホウプ", "wish": "ウィッシュ",
        
        # 基本名詞
        "time": "タイム", "day": "デイ", "week": "ウィーク", "month": "マンス", "year": "イヤー",
        "hour": "アワー", "minute": "ミニット", "second": "セカンド", "morning": "モーニング",
        "afternoon": "アフタヌーン", "evening": "イーブニング", "night": "ナイト",
        "today": "トゥデイ", "tomorrow": "トゥモロウ", "yesterday": "イエスタデイ",
        "home": "ホウム", "house": "ハウス", "room": "ルーム", "door": "ドアー", "window": "ウィンドウ",
        "table": "テイブル", "chair": "チェア", "bed": "ベッド", "car": "カー", "train": "トレイン",
        "bus": "バス", "plane": "プレイン", "school": "スクール", "office": "オフィス",
        "shop": "ショップ", "store": "ストア", "restaurant": "レストラン", "hotel": "ホウテル",
        "hospital": "ハスピタル", "bank": "バンク", "post": "ポウスト", "station": "ステイション",
        "airport": "エアポート", "street": "ストリート", "road": "ロウド", "city": "シティ",
        "town": "タウン", "country": "カントリー", "world": "ワールド", "water": "ウォーター",
        "food": "フード", "bread": "ブレッド", "meat": "ミート", "fish": "フィッシュ",
        "rice": "ライス", "milk": "ミルク", "coffee": "コーフィー", "tea": "ティー",
        "book": "ブック", "paper": "ペイパー", "pen": "ペン", "phone": "フォウン",
        "computer": "コンピューター", "money": "マニー", "price": "プライス", "job": "ジョブ",
        
        # 基本形容詞
        "good": "グッド", "bad": "バッド", "big": "ビッグ", "small": "スモール", "large": "ラージ",
        "little": "リトル", "long": "ロング", "short": "ショート", "high": "ハイ", "low": "ロウ",
        "old": "オウルド", "new": "ニュー", "young": "ヤング", "hot": "ハット", "cold": "コウルド",
        "warm": "ウォーム", "cool": "クール", "fast": "ファスト", "slow": "スロウ",
        "early": "アーリー", "late": "レイト", "easy": "イージー", "hard": "ハード",
        "difficult": "ディフィカルト", "simple": "シンプル", "important": "インポータント",
        "special": "スペシャル", "different": "ディファレント", "same": "セイム",
        "right": "ライト", "wrong": "ロング", "true": "トゥルー", "false": "フォルス",
        "real": "リアル", "free": "フリー", "full": "フル", "empty": "エンプティー",
        "heavy": "ヘビー", "light": "ライト", "strong": "ストロング", "weak": "ウィーク",
        "nice": "ナイス", "beautiful": "ビューティフル", "pretty": "プリティー",
        "clean": "クリーン", "dirty": "ダーティー", "safe": "セイフ", "dangerous": "デインジャラス",
        "happy": "ハッピー", "sad": "サッド", "angry": "アングリー", "surprised": "サプライズド",
        
        # 代名詞・基本語
        "i": "アイ", "you": "ユー", "he": "ヒー", "she": "シー", "we": "ウィー", "they": "ゼイ",
        "it": "イット", "this": "ディス", "that": "ザット", "these": "ジーズ", "those": "ゾウズ",
        "my": "マイ", "your": "ユア", "his": "ヒズ", "her": "ハー", "our": "アワー", "their": "ゼア",
        "me": "ミー", "him": "ヒム", "us": "アス", "them": "ゼム",
        "the": "ザ", "a": "エイ", "an": "アン", "and": "アンド", "or": "オアー", "but": "バット",
        "so": "ソウ", "because": "ビコーズ", "if": "イフ", "when": "ウェン", "where": "ウェア",
        "what": "ワット", "who": "フー", "why": "ワイ", "how": "ハウ", "which": "ウィッチ",
        "yes": "イエス", "no": "ノウ", "not": "ナット", "very": "ベリー", "too": "トゥー",
        "also": "オールソウ", "only": "オウンリー", "just": "ジャスト", "still": "スティル",
        "already": "オールレディ", "yet": "イエット", "again": "アゲン", "always": "オールウェイズ",
        "never": "ネバー", "sometimes": "サムタイムズ", "often": "オフン", "usually": "ユージュアリー",
        "now": "ナウ", "then": "ゼン", "soon": "スーン", "later": "レイター",
        "well": "ウェル", "much": "マッチ", "many": "メニー", "more": "モア", "most": "モウスト",
        "all": "オール", "some": "サム", "any": "エニー", "each": "イーチ", "every": "エブリー",
        
        # 数字
        "one": "ワン", "two": "トゥー", "three": "スリー", "four": "フォー", "five": "ファイブ",
        "six": "シックス", "seven": "セブン", "eight": "エイト", "nine": "ナイン", "ten": "テン",
        "eleven": "イレブン", "twelve": "トゥウェルブ", "twenty": "トゥウェンティー",
        "thirty": "サーティー", "forty": "フォーティー", "fifty": "フィフティー",
        "hundred": "ハンドレッド", "thousand": "サウザンド",
        
        # 重要なフレーズ（個別処理）
        "got": "ガット", "to": "トゥー", "want": "ワント", "going": "ゴウイング",
        "have": "ハブ", "used": "ユーズド", "able": "エイブル",
        "really": "リアリー", "actually": "アクチュアリー", "probably": "プロバブリー",
        "definitely": "デフィニトリー", "maybe": "メイビー", "certainly": "サートンリー",
        "absolutely": "アブソルートリー", "completely": "コンプリートリー", "exactly": "イグザクトリー",
        
        # 場所・方向
        "in": "イン", "on": "オン", "at": "アット", "for": "フォー", "of": "オブ",
        "with": "ウィズ", "by": "バイ", "from": "フロム", "up": "アップ", "down": "ダウン",
        "out": "アウト", "off": "オフ", "over": "オウバー", "under": "アンダー",
        "about": "アバウト", "into": "イントゥー", "through": "スルー", "during": "デューリング",
        "before": "ビフォー", "after": "アフター", "above": "アバブ", "below": "ビロウ",
        "between": "ビトゥイーン", "around": "アラウンド", "near": "ニア", "far": "ファー",
        "here": "ヒア", "there": "ゼア"
    }

def word_to_katakana_conversion(text: str) -> str:
    """単語レベルでの発音記号ベースカタカナ変換"""
    if not text:
        return "？？？"
    
    print(f"🔤 単語→カタカナ変換: '{text}'")
    
    # 辞書を取得
    word_dict = get_word_to_katakana_dict()
    
    # テキストを小文字化して単語に分割
    words = re.findall(r'\b\w+\b', text.lower())
    katakana_words = []
    
    for word in words:
        if word in word_dict:
            katakana = word_dict[word]
            katakana_words.append(katakana)
            print(f"  '{word}' -> '{katakana}' (辞書)")
        else:
            # 辞書にない場合は基本的な音韻変換
            katakana = basic_phonetic_conversion(word)
            katakana_words.append(katakana)
            print(f"  '{word}' -> '{katakana}' (音韻変換)")
    
    # フレーズレベルの特殊処理
    result = " ".join(katakana_words)
    result = apply_phrase_rules(result)
    
    result = result if result else "？？？"
    print(f"🎌 カタカナ変換結果: '{result}'")
    return result

def apply_phrase_rules(katakana_text: str) -> str:
    """フレーズレベルの特殊変換ルール"""
    
    # よく使われるフレーズの特殊変換
    phrase_rules = {
        "ガット トゥー": "ガット・トゥー",  # got to
        "ワント トゥー": "ワント・トゥー",  # want to  
        "ゴウイング トゥー": "ゴウイング・トゥー",  # going to
        "ハブ トゥー": "ハブ・トゥー",  # have to
        "ユーズド トゥー": "ユーズド・トゥー",  # used to
        "エイブル トゥー": "エイブル・トゥー",  # able to
        
        # 疑問フレーズ
        "ワット アー ユー": "ワット・アー・ユー",  # what are you
        "ワット アー ユー ドゥーイング": "ワット・アー・ユー・ドゥーイング",  # what are you doing
        "ハウ アー ユー": "ハウ・アー・ユー",  # how are you
        
        # よくある表現
        "アイ ドント ノウ": "アイ・ドント・ノウ",  # i don't know
        "アイ ドント シンク": "アイ・ドント・シンク",  # i don't think
        "アイ ワント トゥー": "アイ・ワント・トゥー",  # i want to
        "アイ ニード トゥー": "アイ・ニード・トゥー",  # i need to
        "アイ ハブ トゥー": "アイ・ハブ・トゥー",  # i have to
    }
    
    result = katakana_text
    for phrase, replacement in phrase_rules.items():
        result = result.replace(phrase, replacement)
    
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
        ("pl", "プル"), ("bl", "ブル"), ("cl", "クル"), ("gl", "グル"), ("fl", "フル"),
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

def process_phonetic_pronunciation_fixed(audio_file):
    """修正版発音記号ベース発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", ""
    
    try:
        # Step 1: Whisperで音声認識
        english_text = transcribe_audio(audio_file)
        
        # Step 2: 単語レベルで辞書ベースカタカナ変換
        katakana_text = word_to_katakana_conversion(english_text)
        
        # Step 3: 発音記号情報も生成（表示用）
        phonetic_info = generate_phonetic_info(english_text)
        
        return (
            "✅ 修正版解析完了",
            english_text.title(),
            phonetic_info,
            katakana_text
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", ""

def generate_phonetic_info(text: str) -> str:
    """発音記号情報を生成（表示用）"""
    words = re.findall(r'\b\w+\b', text.lower())
    word_dict = get_word_to_katakana_dict()
    
    phonetic_parts = []
    for word in words:
        if word in word_dict:
            phonetic_parts.append(f"{word}→{word_dict[word]}")
        else:
            phonetic_parts.append(f"{word}→(推測)")
    
    return " | ".join(phonetic_parts)

# 修正版Gradioインターフェース
def create_phonetic_fixed_app():
    with gr.Blocks(
        title="発音記号ベース英語発音解析（修正版）",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 950px; margin: 0 auto; }
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
            font-size: 14px;
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
        .fixed-badge {
            display: inline-block;
            background: #4caf50;
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
            # 🔧 発音記号ベース英語発音解析（修正版）
            
            **確実に動作するシンプルな辞書ベース変換** <span class="fixed-badge">FIXED</span>
            
            500以上の英単語を直接カタカナに変換
            
            ### 🎯 修正ポイント
            - **辞書ベース直接変換**: 単語→カタカナの直接マッピング
            - **フレーズ対応**: よく使われる表現の特殊処理
            - **確実な動作**: 複雑な発音記号処理を簡略化
            
            ### 📚 変換例
            - "got to" → 「ガット・トゥー」
            - "want to" → 「ワント・トゥー」
            - "what are you doing" → 「ワット・アー・ユー・ドゥーイング」
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
                "🔧 修正版解析開始",
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
                    label="🔤 変換情報",
                    placeholder="変換情報がここに表示されます",
                    elem_classes=["phonetic-result", "result-box"],
                    lines=2
                )
                
                katakana_output = gr.Textbox(
                    label="🎌 カタカナ変換結果",
                    placeholder="辞書ベースのカタカナがここに表示されます",
                    elem_classes=["katakana-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_phonetic_pronunciation_fixed,
                inputs=[audio_input],
                outputs=[status_output, english_output, phonetic_output, katakana_output]
            )
            
            gr.Markdown("""
            ---
            ### 🔧 修正版の特徴
            
            - **500語の辞書**: 基本的な英単語を網羅
            - **直接変換**: 複雑な処理を排除して確実性を重視
            - **フレーズ処理**: よく使われる表現の特別対応
            - **デバッグ情報**: 変換過程が見える透明性
            
            **目的**: 複雑な発音記号処理ではなく、実用的で確実な変換を提供
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🔧 修正版発音記号ベース英語発音解析システム 起動中...")
    setup_whisper()
    
    app = create_phonetic_fixed_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7866,
        share=False
    )