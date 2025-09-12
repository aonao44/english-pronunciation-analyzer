#!/usr/bin/env python3
"""
Hugging Face Spaces用Whisper発音解析API v2
Phonemizer統合 + 改善されたUI
"""
import gradio as gr
import whisper
import tempfile
import os
import json
from typing import Dict, Any
from phonemizer import phonemize
from phonemizer.backend import EspeakBackend

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

def phonemize_text(text):
    """
    テキストを音素に変換（Phonemizer使用）
    """
    try:
        if not text:
            return []
        
        print(f"🔤 音素変換入力: '{text}'", flush=True)
        
        # Phonemizerで音素に変換（英語）
        phonemes = phonemize(
            text,
            language='en-us',
            backend='espeak',
            executable='/opt/homebrew/bin/espeak',
            strip=True,
            preserve_punctuation=True,
            with_stress=False
        )
        
        print(f"🎵 音素結果: '{phonemes}'", flush=True)
        return phonemes
        
    except Exception as e:
        print(f"❌ 音素変換失敗: {e}")
        return text  # フォールバック

def phonemes_to_katakana(phonemes):
    """
    音素をカタカナに変換（改良版）
    """
    if not phonemes:
        return "？？？"
    
    print(f"🎌 音素→カタカナ変換: '{phonemes}'", flush=True)
    
    # 音素→カタカナ変換テーブル（IPA記号ベース）
    phoneme_map = {
        # 母音
        'iː': 'イー', 'i': 'イ', 'ɪ': 'イ',
        'eɪ': 'エイ', 'e': 'エ', 'ɛ': 'エ',
        'æ': 'ア', 'aː': 'アー', 'a': 'ア', 'ʌ': 'ア',
        'oʊ': 'オウ', 'ɔː': 'オー', 'ɔ': 'オ', 'o': 'オ',
        'uː': 'ウー', 'u': 'ウ', 'ʊ': 'ウ',
        'ə': 'ア', 'ɜː': 'アー',
        
        # 二重母音
        'aɪ': 'アイ', 'aʊ': 'アウ', 'ɔɪ': 'オイ',
        
        # 子音
        'p': 'プ', 'b': 'ブ', 't': 'ト', 'd': 'ド',
        'k': 'ク', 'g': 'グ', 'f': 'フ', 'v': 'ブ',
        'θ': 'ス', 'ð': 'ズ', 's': 'ス', 'z': 'ズ',
        'ʃ': 'シュ', 'ʒ': 'ジュ', 'h': 'ハ',
        'tʃ': 'チ', 'dʒ': 'ジ',
        'm': 'ム', 'n': 'ン', 'ŋ': 'ング',
        'l': 'ル', 'r': 'ル', 'j': 'ヤ', 'w': 'ワ',
        
        # その他
        ' ': ' ', '.': '。', ',': '、', '!': '！', '?': '？'
    }
    
    result = phonemes
    
    # 長い音素から短い音素の順で変換
    for phoneme, katakana in sorted(phoneme_map.items(), key=lambda x: -len(x[0])):
        result = result.replace(phoneme, katakana)
    
    # 残った記号を処理
    import re
    result = re.sub(r'[ˈˌ]', '', result)  # ストレスマーク除去
    result = re.sub(r'[^\u30A0-\u30FF\s。、！？]', '？', result)  # 残った文字を？に
    
    print(f"🎌 カタカナ結果: '{result}'", flush=True)
    return result

def process_pronunciation(audio_file) -> Dict[str, Any]:
    """
    発音解析のメイン処理（Phonemizer統合版）
    """
    try:
        if audio_file is None:
            return {
                "success": False,
                "error": "音声ファイルがありません"
            }
        
        # Step 1: Whisperで文字起こし
        raw_text = transcribe_with_whisper(audio_file)
        
        # Step 2: Phonemizerで音素変換
        phonemes = phonemize_text(raw_text)
        
        # Step 3: 音素→カタカナ変換
        katakana_text = phonemes_to_katakana(phonemes)
        
        return {
            "success": True,
            "whisper_raw": raw_text,
            "phonemes": phonemes,
            "whisper_katakana": katakana_text
        }
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def process_pronunciation_simple(audio_file):
    """
    シンプルなGradioインターフェース用の処理関数
    """
    if audio_file is None:
        return "❌ 音声を録音してください", "", ""
    
    result = process_pronunciation(audio_file)
    
    if result["success"]:
        return (
            f"✅ 解析完了",
            result["whisper_raw"],
            result["whisper_katakana"]
        )
    else:
        return f"❌ エラー: {result['error']}", "", ""

# 改善されたGradioインターフェース
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
            発音学習・指導用に設計されています
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
            
            **特徴**: 自動補正されない実際の発音を表示
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🚀 英語発音解析API v2 起動中...")
    setup_whisper()  # 起動時にモデルをロード
    
    app = create_simple_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )