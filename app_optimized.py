#!/usr/bin/env python3
"""
最適化英語発音解析システム
軽量高速でありながら発音をそのままカタカナ表示する実用版
"""
import gradio as gr
import whisper
import numpy as np
import tempfile
import os
import json
import re
from typing import Dict, Any

# Whisperモデル（軽量）
model = None

def setup_whisper():
    """Whisperモデルをセットアップ（軽量版）"""
    global model
    if model is None:
        print("Whisper tinyモデルをロード中...")
        model = whisper.load_model("tiny")
        print("✅ Whisperモデル読み込み完了")
    return model

def optimized_transcribe(audio_file):
    """
    最適化された文字起こし（実際の発音キャッチ）
    """
    model = setup_whisper()
    
    try:
        print(f"🎤 最適化解析中: {audio_file}")
        
        # 実際の発音を捉える最適化パラメータ
        result = model.transcribe(
            audio_file,
            language="en",
            temperature=0.9,        # 多様性を重視
            best_of=2,              # 軽量化（候補数削減）
            beam_size=2,            # 軽量化
            compression_ratio_threshold=1.8,
            logprob_threshold=-1.6,
            no_speech_threshold=0.5
        )
        
        raw_text = result["text"].strip()
        print(f"📝 解析結果: '{raw_text}'")
        
        return raw_text
        
    except Exception as e:
        print(f"❌ 解析失敗: {e}")
        raise e

def advanced_katakana_conversion(text: str) -> str:
    """
    実用的高精度カタカナ変換（実際の発音重視）
    """
    if not text:
        return "？？？"
    
    print(f"🎌 カタカナ変換: '{text}'")
    
    # テキストを正規化
    text = text.lower().strip()
    
    # 実際の発音パターン（最も重要なもの）
    pronunciation_patterns = {
        # 縮約形・連結音（最重要）
        "got to": "ガラ", "gotta": "ガラ", "gata": "ガラ", "gara": "ガラ",
        "want to": "ワナ", "wanna": "ワナ", "wana": "ワナ", "wanna": "ワナ",
        "going to": "ゴナ", "gonna": "ゴナ", "gona": "ゴナ",
        "what are you": "ワラユ", "whatchu": "ワチュ", "wachu": "ワチュ",
        "what are you doing": "ワラユドゥーイン", "whatchu doing": "ワチュドゥーイン",
        "i don't know": "アイドンノ", "i dunno": "アイダノ", "i duno": "アイダノ",
        "let me": "レミー", "lemme": "レミー", "leme": "レミー",
        "give me": "ギミー", "gimme": "ギミー", "gime": "ギミー",
        "out of": "アウラ", "outta": "アウラ", "auda": "アウラ",
        "a lot of": "アロラ", "alotta": "アロラ", "aloda": "アロラ",
        "kind of": "カイナ", "kinda": "カイナ", "kainda": "カイナ",
        "sort of": "ソーラ", "sorta": "ソーラ", "soda": "ソーラ",
        "because": "コズ", "cause": "コズ", "cuz": "コズ", "cos": "コズ",
        
        # よく間違えやすい単語
        "need": "ニード", "nid": "ニード", "ned": "ニード",
        "really": "リアリー", "rily": "リリー", "relly": "レリー",
        "probably": "プロバブリー", "probly": "プロブリー", "proly": "プロリー",
        "actually": "アクチュアリー", "actuly": "アクチュリー", "achly": "アクリー",
        "literally": "リテラリー", "litrly": "リトラリー", "litraly": "リトラリー",
        
        # 基本単語（発音重視）
        "the": "ザ", "of": "ア", "to": "タ", "and": "エン", "a": "ア",
        "in": "イン", "is": "イズ", "it": "イト", "you": "ユー", "that": "ザト",
        "he": "ヒー", "was": "ワズ", "for": "フォー", "are": "アー", "as": "アズ",
        "with": "ウィス", "his": "ヒズ", "they": "ゼイ", "i": "アイ", "at": "アト",
        "be": "ビー", "this": "ディス", "have": "ハブ", "from": "フロム", "or": "オー",
        "one": "ワン", "had": "ハド", "by": "バイ", "word": "ワード", "but": "バト",
        "not": "ナト", "what": "ワト", "all": "オール", "were": "ワー", "we": "ウィー",
        "when": "ウェン", "your": "ヨー", "can": "キャン", "said": "セド", "there": "ゼア",
        "do": "ドゥー", "will": "ウィル", "if": "イフ", "up": "アップ", "out": "アウト",
        "so": "ソー", "time": "タイム", "very": "ベリー", "when": "ウェン", "come": "カム",
        "how": "ハウ", "get": "ゲト", "go": "ゴー", "no": "ノー", "way": "ウェイ",
        "day": "デイ", "man": "マン", "new": "ニュー", "now": "ナウ", "old": "オールド",
        "see": "シー", "him": "ヒム", "two": "トゥー", "who": "フー", "did": "ディド",
        "yes": "イエス", "her": "ハー", "she": "シー", "may": "メイ", "say": "セイ"
    }
    
    # フレーズレベルでマッチング
    converted_text = text
    for pattern, katakana in pronunciation_patterns.items():
        if pattern in converted_text:
            converted_text = converted_text.replace(pattern, katakana)
    
    # 残った英語を音韻変換
    words = converted_text.split()
    final_words = []
    
    for word in words:
        # カタカナかどうかチェック
        if re.match(r'^[\u30A0-\u30FF\s・ー]+$', word):
            final_words.append(word)
        else:
            # 音韻変換（軽量版）
            converted_word = simple_phonetic_conversion(word)
            final_words.append(converted_word)
    
    result = " ".join(final_words) if final_words else "？？？"
    print(f"🎌 最終結果: '{result}'")
    return result

def simple_phonetic_conversion(word: str) -> str:
    """
    シンプルな音韻変換（軽量高速）
    """
    if not word:
        return "？"
    
    # 基本的な音韻変換ルール（高速処理用）
    conversions = [
        # 長めのパターンから処理
        ("tion", "ション"), ("sion", "ション"),
        ("ough", "アフ"), ("augh", "オー"),
        ("ight", "アイト"), ("ought", "オート"),
        ("th", "ス"), ("sh", "シ"), ("ch", "チ"), ("ph", "フ"), ("wh", "ウ"),
        ("oo", "ウー"), ("ee", "イー"), ("ea", "イー"), ("ai", "エイ"), ("ay", "エイ"),
        ("ou", "アウ"), ("ow", "アウ"), ("oi", "オイ"), ("oy", "オイ"),
        ("er", "アー"), ("ir", "アー"), ("ur", "アー"), ("ar", "アー"),
        ("ng", "ング"), ("nk", "ンク"), ("nt", "ント"), ("nd", "ンド"),
        ("st", "スト"), ("sp", "スプ"), ("sc", "スク"), ("sk", "スク"),
        ("tr", "トル"), ("pr", "プル"), ("br", "ブル"), ("cr", "クル"),
        ("dr", "ドル"), ("fr", "フル"), ("gr", "グル"),
        
        # 基本母音・子音
        ("a", "ア"), ("e", "エ"), ("i", "イ"), ("o", "オ"), ("u", "ウ"),
        ("b", "ブ"), ("c", "ク"), ("d", "ド"), ("f", "フ"), ("g", "グ"),
        ("h", "ハ"), ("j", "ジ"), ("k", "ク"), ("l", "ル"), ("m", "ム"),
        ("n", "ン"), ("p", "プ"), ("q", "ク"), ("r", "ル"), ("s", "ス"),
        ("t", "ト"), ("v", "ブ"), ("w", "ワ"), ("x", "クス"), ("y", "ヤ"), ("z", "ズ")
    ]
    
    result = word.lower()
    for eng, kata in conversions:
        result = result.replace(eng, kata)
    
    # 残った文字を処理
    result = re.sub(r'[^\\u30A0-\\u30FF\\s・ー]', '？', result)
    
    return result if result else "？"

def process_optimized_pronunciation(audio_file):
    """
    最適化発音解析のメイン処理
    """
    if audio_file is None:
        return "❌ 音声を録音してください", "", ""
    
    try:
        # 最適化解析実行
        raw_text = optimized_transcribe(audio_file)
        
        # 高精度カタカナ変換
        katakana_text = advanced_katakana_conversion(raw_text)
        
        return (
            "✅ 解析完了（最適化版）",
            raw_text,
            katakana_text
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", ""

# 最適化Gradioインターフェース
def create_optimized_app():
    with gr.Blocks(
        title="最適化英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 850px; margin: 0 auto; }
        .result-box { font-size: 18px; padding: 18px; margin: 12px 0; border-radius: 8px; }
        .katakana-result { 
            background: linear-gradient(135deg, #e8f4fd, #d1ecf1); 
            border: 2px solid #2196f3; 
            font-weight: bold;
            font-size: 20px;
        }
        .english-result { 
            background: linear-gradient(135deg, #f5f5f5, #eeeeee); 
            border: 2px solid #757575; 
        }
        .status-box { 
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
            border: 2px solid #4caf50;
            text-align: center;
            font-weight: bold;
        }
        .speed-badge {
            display: inline-block;
            background: #ff9800;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }
        """
    ) as app:
        
        with gr.Column(elem_classes=["main-container"]):
            gr.Markdown("""
            # ⚡ 最適化英語発音解析システム
            
            **軽量高速＋高精度で実際の発音をカタカナ表示** <span class="speed-badge">FAST</span>
            
            発音学習・指導に最適化された実用版
            
            ### 🎯 変換例
            - "Got to" → 「ガラ」
            - "Want to" → 「ワナ」  
            - "I don't know" → 「アイドンノ」
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 英語を録音してください（1-10秒推奨）",
                    show_label=True,
                    container=True
                )
            
            # 解析ボタン
            analyze_btn = gr.Button(
                "⚡ 高速解析開始",
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
                
                katakana_output = gr.Textbox(
                    label="🎌 実際の発音（カタカナ）",
                    placeholder="実際の発音がカタカナでここに表示されます",
                    elem_classes=["katakana-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_optimized_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, katakana_output]
            )
            
            gr.Markdown("""
            ---
            ### ⚡ 最適化ポイント
            
            - **軽量モデル**: Whisper tiny（高速処理）
            - **実用パラメータ**: 精度と速度のバランス最適化
            - **頻出パターン**: 実際の発音変化を重点的に対応
            - **高速変換**: 音韻ルールを軽量化
            
            **処理時間**: 約3-5秒（実用レベル）
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("⚡ 最適化英語発音解析システム 起動中...")
    setup_whisper()
    
    app = create_optimized_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7863,
        share=False
    )