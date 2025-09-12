#!/usr/bin/env python3
"""
Hugging Face Spaces用Whisper発音解析API
Gradioインターフェース + API機能
"""
import gradio as gr
import whisper
import tempfile
import os
import json
import difflib
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

def convert_to_katakana_simple(text):
    """
    音韻ルールベースのカタカナ変換（任意の英単語に対応）
    """
    print(f"🔤 カタカナ変換入力: '{text}'", flush=True)
    if not text:
        print("⚠️ 空のテキストです")
        return "？？？"
    
    def convert_word_to_katakana(word):
        """単語を音韻ルールでカタカナに変換"""
        result = word.lower()
        
        # 段階的な音韻変換ルール（長いパターンから先に処理）
        phonetic_rules = [
            # 3文字以上の音素組み合わせ
            ('tion', 'ション'), ('sion', 'ション'), ('ough', 'オー'), ('augh', 'オー'),
            ('ight', 'アイト'), ('eigh', 'エイ'), ('ture', 'チャー'),
            
            # 2文字の音素組み合わせ  
            ('th', 'ス'), ('sh', 'シュ'), ('ch', 'チ'), ('ph', 'フ'), ('wh', 'ホ'),
            ('ng', 'ング'), ('nk', 'ンク'), ('nt', 'ント'), ('nd', 'ンド'), ('mp', 'ンプ'),
            ('st', 'スト'), ('sp', 'スプ'), ('sk', 'スク'), ('sc', 'スク'), ('sw', 'スウ'),
            ('tr', 'トル'), ('dr', 'ドル'), ('pr', 'プル'), ('br', 'ブル'), ('fr', 'フル'), 
            ('gr', 'グル'), ('cr', 'クル'), ('bl', 'ブル'), ('cl', 'クル'), ('fl', 'フル'),
            ('pl', 'プル'), ('sl', 'スル'), ('gl', 'グル'),
            
            # 母音の組み合わせ
            ('ai', 'アイ'), ('ay', 'エイ'), ('ei', 'エイ'), ('ey', 'エイ'),
            ('oa', 'オー'), ('oe', 'オー'), ('ou', 'アウ'), ('ow', 'アウ'),
            ('au', 'オー'), ('aw', 'オー'), ('oo', 'ウー'), ('ea', 'イー'),
            ('ee', 'イー'), ('ie', 'アイ'), ('ue', 'ユー'), ('ui', 'ユイ'),
            
            # 語尾パターン
            ('ing', 'イング'), ('ed', 'ド'), ('er', 'アー'), ('est', 'エスト'),
            ('ly', 'リー'), ('ty', 'ティー'), ('ry', 'リー'), ('ny', 'ニー'),
            ('le', 'ル'), ('al', 'アル'), ('ic', 'イック'), ('ous', 'アス'),
            
            # 単一文字の基本音 (最後に処理)
            ('a', 'ア'), ('b', 'ブ'), ('c', 'ク'), ('d', 'ド'), ('e', 'エ'),
            ('f', 'フ'), ('g', 'グ'), ('h', 'ハ'), ('i', 'イ'), ('j', 'ジ'),
            ('k', 'ク'), ('l', 'ル'), ('m', 'ム'), ('n', 'ン'), ('o', 'オ'),
            ('p', 'プ'), ('q', 'ク'), ('r', 'ル'), ('s', 'ス'), ('t', 'ト'),
            ('u', 'ウ'), ('v', 'ブ'), ('w', 'ウ'), ('x', 'クス'), ('y', 'イ'), ('z', 'ズ')
        ]
        
        # ルールを順次適用
        for pattern, katakana in phonetic_rules:
            result = result.replace(pattern, katakana)
        
        # 残った英字があれば？に置換
        import re
        result = re.sub(r'[a-zA-Z]+', '？', result)
        
        return result
    
    # 単語ごとに分割して変換
    words = text.lower().split()
    converted_words = [convert_word_to_katakana(word) for word in words]
    result = ' '.join(converted_words)
    
    print(f"🎌 カタカナ変換結果: '{result}'")
    return result

def process_pronunciation(audio_file) -> Dict[str, Any]:
    """
    発音解析のメイン処理（Gradioインターフェース用）
    """
    try:
        if audio_file is None:
            return {
                "success": False,
                "error": "音声ファイルがありません"
            }
        
        # Whisperで文字起こし
        raw_text = transcribe_with_whisper(audio_file)
        
        # 英語→カタカナ変換
        katakana_text = convert_to_katakana_simple(raw_text)
        
        return {
            "success": True,
            "whisper_raw": raw_text,
            "whisper_katakana": katakana_text
        }
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_pronunciation_gradio(audio_file):
    """
    Gradioインターフェース用の処理関数
    """
    result = process_pronunciation(audio_file)
    
    if result["success"]:
        return f"""
## 🎤 解析結果

**英語表記:** {result["whisper_raw"]}

**カタカナ表記:** {result["whisper_katakana"]}

---
✨ 発音学習用に設計されています。実際の発音がそのまま文字起こしされます。
        """
    else:
        return f"❌ エラー: {result['error']}"

# Gradioインターフェースを作成
def create_gradio_app():
    with gr.Blocks(title="英語発音解析API") as app:
        gr.Markdown("""
        # 🎤 英語発音解析API
        
        英語の発音を録音して、実際の発音をカタカナで表示します。
        発音学習・指導用に設計されており、自動補正されない生の発音結果を提供します。
        """)
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    sources=["microphone", "upload"], 
                    type="filepath",
                    label="🎤 音声を録音またはファイルをアップロード"
                )
                analyze_btn = gr.Button("🎯 解析開始", variant="primary")
            
            with gr.Column():
                output_text = gr.Markdown(label="📊 解析結果")
        
        analyze_btn.click(
            process_pronunciation_gradio,
            inputs=[audio_input],
            outputs=[output_text]
        )
        
        gr.Markdown("""
        ### 📝 使用方法
        1. 🎤 マイクボタンで録音、または音声ファイルをアップロード
        2. 🎯 「解析開始」ボタンをクリック
        3. 📊 英語表記・カタカナ表記の結果を確認
        
        ### ⚡ API使用
        ```
        POST /api/predict
        Content-Type: multipart/form-data
        
        Form data:
        - data: [null, audio_file]
        ```
        """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🚀 英語発音解析API起動中...")
    setup_whisper()  # 起動時にモデルをロード
    
    app = create_gradio_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )