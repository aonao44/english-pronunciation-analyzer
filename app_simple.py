#!/usr/bin/env python3
"""
Hugging Face Spaces用Whisper発音解析API - シンプル版
Phonemizerなし、Whisperの結果をそのまま使用
"""
import gradio as gr
import whisper
import tempfile
import os
import json
import re
from typing import Dict, Any

# Whisperモデルをグローバルで読み込み（初回のみ）
model = None

def setup_whisper():
    """Whisperモデルをセットアップ"""
    global model
    if model is None:
        print("Whisper tinyモデルをロード中...")
        model = whisper.load_model("tiny")
        print("✅ Whisperモデル読み込み完了")
    return model

def transcribe_with_whisper(audio_file):
    """
    音声データをWhisperで文字起こし（発音学習用設定）
    """
    model = setup_whisper()
    
    try:
        print(f"🎤 音声ファイルを分析中: {audio_file}")
        
        # 英語認識で実際の発音を取得
        result = model.transcribe(
            audio_file,
            language="en",          # 英語として認識
            temperature=0.8,        # 少し高めで多様性を持たせる
            best_of=3,             # 候補数を適度に設定
            beam_size=3,           # ビーム探索を適度に設定
            compression_ratio_threshold=2.0,  # 品質基準を緩める
            logprob_threshold=-1.5  # 確信度基準を緩める
        )
        
        raw_text = result["text"].strip()
        print(f"📝 Whisper結果: '{raw_text}'", flush=True)
        
        return raw_text
        
    except Exception as e:
        print(f"❌ Whisper文字起こし失敗: {e}")
        raise e

def english_to_katakana_phonetic(text):
    """
    英語をカタカナに変換（音韻ベース・改良版）
    """
    if not text:
        return "？？？"
    
    print(f"🎌 英語→カタカナ変換: '{text}'", flush=True)
    
    # テキストを小文字に変換して単語に分割
    text = text.lower().strip()
    words = re.split(r'\s+', text)
    
    # 単語レベルの変換マップ（よく使われる英語フレーズ）
    word_map = {
        # よくある単語
        "hello": "ハロー", "hi": "ハイ", "hey": "ヘイ",
        "good": "グッド", "morning": "モーニング", "afternoon": "アフタヌーン",
        "evening": "イブニング", "night": "ナイト",
        "thank": "サンク", "thanks": "サンクス", "you": "ユー",
        "yes": "イエス", "no": "ノー", "ok": "オーケー", "okay": "オーケー",
        "please": "プリーズ", "sorry": "ソーリー", "excuse": "エクスキューズ",
        "me": "ミー", "my": "マイ", "i": "アイ", "we": "ウィー", "they": "ゼイ",
        "what": "ワット", "where": "ウェア", "when": "ウェン", "why": "ワイ",
        "how": "ハウ", "who": "フー", "which": "ウィッチ",
        "this": "ディス", "that": "ザット", "these": "ジーズ", "those": "ゾーズ",
        "here": "ヒア", "there": "ゼア", "where": "ウェア",
        "now": "ナウ", "then": "ゼン", "today": "トゥデイ",
        "tomorrow": "トゥモロー", "yesterday": "イエスタデイ",
        
        # 数字
        "one": "ワン", "two": "トゥー", "three": "スリー", "four": "フォー",
        "five": "ファイブ", "six": "シックス", "seven": "セブン", 
        "eight": "エイト", "nine": "ナイン", "ten": "テン",
        
        # 基本動詞
        "go": "ゴー", "come": "カム", "get": "ゲット", "take": "テイク",
        "make": "メイク", "do": "ドゥー", "have": "ハブ", "be": "ビー",
        "see": "シー", "know": "ノー", "think": "シンク", "say": "セイ",
        "want": "ウォント", "need": "ニード", "like": "ライク", "love": "ラブ",
        
        # よくある形容詞
        "big": "ビッグ", "small": "スモール", "good": "グッド", "bad": "バッド",
        "new": "ニュー", "old": "オールド", "young": "ヤング",
        "hot": "ホット", "cold": "コールド", "warm": "ウォーム", "cool": "クール",
        "fast": "ファスト", "slow": "スロー", "high": "ハイ", "low": "ロー",
        
        # 場所・建物
        "home": "ホーム", "house": "ハウス", "school": "スクール",
        "office": "オフィス", "shop": "ショップ", "store": "ストア",
        "restaurant": "レストラン", "hotel": "ホテル", "station": "ステーション",
        
        # 時間表現
        "time": "タイム", "hour": "アワー", "minute": "ミニット",
        "second": "セカンド", "day": "デイ", "week": "ウィーク",
        "month": "マンス", "year": "イヤー"
    }
    
    result_words = []
    
    for word in words:
        if not word:
            continue
            
        # 句読点を除去
        clean_word = re.sub(r'[^\w]', '', word)
        if not clean_word:
            continue
        
        # 単語マップで変換
        if clean_word in word_map:
            result_words.append(word_map[clean_word])
        else:
            # 音韻ベースの変換（文字単位）
            katakana_word = ""
            i = 0
            while i < len(clean_word):
                char = clean_word[i]
                next_char = clean_word[i+1] if i+1 < len(clean_word) else ""
                
                # 2文字の組み合わせをチェック
                two_char = char + next_char
                if two_char in phoneme_map_2char:
                    katakana_word += phoneme_map_2char[two_char]
                    i += 2
                elif char in phoneme_map_1char:
                    katakana_word += phoneme_map_1char[char]
                    i += 1
                else:
                    katakana_word += "？"
                    i += 1
            
            result_words.append(katakana_word if katakana_word else "？？？")
    
    result = " ".join(result_words) if result_words else "？？？"
    print(f"🎌 カタカナ結果: '{result}'", flush=True)
    return result

# 2文字の音韻マップ
phoneme_map_2char = {
    "th": "ス", "sh": "シュ", "ch": "チ", "ph": "フ", "wh": "ウ",
    "ck": "ク", "ng": "ング", "nk": "ンク", "mp": "ンプ", "nt": "ント",
    "st": "スト", "sp": "スプ", "sc": "スク", "sk": "スク", "sm": "スム",
    "sn": "スン", "sl": "スル", "sw": "スウ", "tr": "トル", "pr": "プル",
    "br": "ブル", "cr": "クル", "dr": "ドル", "fr": "フル", "gr": "グル",
    "oo": "ウー", "ee": "イー", "ea": "イー", "ou": "アウ", "ow": "アウ",
    "ai": "エイ", "ay": "エイ", "ey": "エイ", "ie": "アイ", "oe": "オウ"
}

# 1文字の音韻マップ
phoneme_map_1char = {
    "a": "ア", "e": "エ", "i": "イ", "o": "オ", "u": "ウ",
    "b": "ブ", "c": "ク", "d": "ド", "f": "フ", "g": "グ",
    "h": "ハ", "j": "ジ", "k": "ク", "l": "ル", "m": "ム",
    "n": "ン", "p": "プ", "q": "ク", "r": "ル", "s": "ス",
    "t": "ト", "v": "ブ", "w": "ワ", "x": "クス", "y": "ヤ", "z": "ズ"
}

def process_pronunciation_simple(audio_file):
    """
    シンプルなGradioインターフェース用の処理関数（Phonemizerなし）
    """
    if audio_file is None:
        return "❌ 音声を録音してください", "", ""
    
    try:
        # Whisperで文字起こし
        raw_text = transcribe_with_whisper(audio_file)
        
        # 直接カタカナ変換
        katakana_text = english_to_katakana_phonetic(raw_text)
        
        return (
            f"✅ 解析完了",
            raw_text,
            katakana_text
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", ""

# シンプルなGradioインターフェース
def create_simple_app():
    with gr.Blocks(
        title="英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 800px; margin: 0 auto; }
        .result-box { font-size: 18px; padding: 15px; margin: 10px 0; }
        .katakana-result { background: #f0f8ff; border-left: 4px solid #1e90ff; }
        .english-result { background: #f8f8f8; border-left: 4px solid #666; }
        """
    ) as app:
        
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("""
            # 🎤 英語発音解析
            
            **話した英語の実際の発音をカタカナで表示します**  
            発音学習・指導用に設計されています（シンプル版）
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 ここを押して録音",
                    show_label=True,
                    container=True
                )
            
            # 解析ボタン
            analyze_btn = gr.Button(
                "🎯 解析する",
                variant="primary",
                size="lg",
                scale=1
            )
            
            # 結果表示エリア
            with gr.Column():
                status_output = gr.Textbox(
                    label="状態",
                    show_label=False,
                    interactive=False
                )
                
                english_output = gr.Textbox(
                    label="📝 英語表記",
                    placeholder="解析結果がここに表示されます",
                    elem_classes=["english-result"]
                )
                
                katakana_output = gr.Textbox(
                    label="🎌 カタカナ表記",
                    placeholder="発音がカタカナでここに表示されます",
                    elem_classes=["katakana-result"]
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_pronunciation_simple,
                inputs=[audio_input],
                outputs=[status_output, english_output, katakana_output]
            )
            
            gr.Markdown("""
            ---
            ### 💡 使用方法
            1. **🎤 録音ボタン**を押して英語を話す
            2. **🎯 解析する**ボタンをクリック
            3. 結果を確認
            
            **特徴**: Whisperの結果をそのまま使用（Phonemizerなし）
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🚀 英語発音解析API シンプル版 起動中...")
    setup_whisper()  # 起動時にモデルをロード
    
    app = create_simple_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False
    )