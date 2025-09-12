#!/usr/bin/env python3
"""
日本語モード版英語発音解析システム
英語発音を日本語モードで認識してカタカナ出力を実験
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

def transcribe_english_mode(audio_file):
    """英語モードで音声認識"""
    model = setup_whisper()
    
    try:
        print(f"🇺🇸 英語モード解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language="en",  # 英語モード
            temperature=0.7,
            best_of=3,
            beam_size=2,
        )
        
        english_text = result["text"].strip()
        print(f"📝 英語モード結果: '{english_text}'")
        
        return english_text
        
    except Exception as e:
        print(f"❌ 英語モード解析失敗: {e}")
        raise e

def transcribe_japanese_mode(audio_file):
    """日本語モードで音声認識（英語発音をカタカナ化実験）"""
    model = setup_whisper()
    
    try:
        print(f"🇯🇵 日本語モード解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language="ja",  # 日本語モード
            temperature=0.9,  # 多様性を重視
            best_of=2,
            beam_size=2,
            # 日本語特有の設定
            compression_ratio_threshold=1.8,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6
        )
        
        japanese_text = result["text"].strip()
        print(f"📝 日本語モード結果: '{japanese_text}'")
        
        return japanese_text
        
    except Exception as e:
        print(f"❌ 日本語モード解析失敗: {e}")
        raise e

def transcribe_auto_mode(audio_file):
    """自動言語検出モードで音声認識"""
    model = setup_whisper()
    
    try:
        print(f"🌍 自動検出モード解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language=None,  # 自動検出
            temperature=0.8,
            best_of=2,
            beam_size=2,
        )
        
        auto_text = result["text"].strip()
        detected_language = result.get("language", "unknown")
        print(f"📝 自動検出結果: '{auto_text}' (言語: {detected_language})")
        
        return auto_text, detected_language
        
    except Exception as e:
        print(f"❌ 自動検出解析失敗: {e}")
        raise e

def clean_japanese_text(text: str) -> str:
    """日本語テキストをクリーンアップ（カタカナ・ひらがなのみ抽出）"""
    if not text:
        return "？？？"
    
    # カタカナ・ひらがな・記号のみを抽出
    cleaned = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s・ー]', '', text)
    
    # 連続する空白を1つに
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else "？？？"

def process_japanese_mode_pronunciation(audio_file):
    """日本語モード実験版発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", "", ""
    
    try:
        # Step 1: 英語モードで解析
        english_result = transcribe_english_mode(audio_file)
        
        # Step 2: 日本語モードで解析
        japanese_result = transcribe_japanese_mode(audio_file)
        
        # Step 3: 自動検出モードで解析
        auto_result, detected_lang = transcribe_auto_mode(audio_file)
        
        # Step 4: 日本語結果をクリーンアップ
        cleaned_japanese = clean_japanese_text(japanese_result)
        
        return (
            "✅ 3モード比較解析完了",
            english_result,
            japanese_result,
            cleaned_japanese,
            f"{auto_result} (検出言語: {detected_lang})"
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", "", ""

# 日本語モード実験版Gradioインターフェース
def create_japanese_mode_app():
    with gr.Blocks(
        title="日本語モード実験版英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 1100px; margin: 0 auto; }
        .result-box { font-size: 16px; padding: 16px; margin: 10px 0; border-radius: 8px; }
        .english-result { 
            background: linear-gradient(135deg, #f3e5f5, #e1bee7); 
            border: 2px solid #9c27b0; 
        }
        .japanese-result { 
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
            border: 2px solid #4caf50; 
            font-weight: bold;
        }
        .cleaned-result { 
            background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
            border: 3px solid #ff9800; 
            font-weight: bold;
            font-size: 20px;
        }
        .auto-result { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            border: 2px solid #2196f3; 
        }
        .status-box { 
            background: linear-gradient(135deg, #fce4ec, #f8bbd9); 
            border: 2px solid #e91e63;
            text-align: center;
            font-weight: bold;
        }
        .experiment-badge {
            display: inline-block;
            background: #e91e63;
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
            # 🇯🇵 日本語モード実験版英語発音解析
            
            **3つのモードで同時解析して補正率を比較** <span class="experiment-badge">EXPERIMENT</span>
            
            英語発音を3つの言語モードで解析し、どのモードが実際の発音に近いかを実験
            
            ### 🔬 実験内容
            1. **英語モード**: 標準的な英語認識（補正強）
            2. **日本語モード**: 英語音をカタカナ化実験（補正弱？）
            3. **自動検出**: 言語を自動判定
            4. **クリーンアップ**: カタカナ・ひらがなのみ抽出
            
            ### 🎯 期待結果
            - **英語モード**: "I want to go"（補正済み）
            - **日本語モード**: "アイワントゥゴー"（実音そのまま？）
            - **クリーンアップ**: "アイワントゥゴー"（純粋なカナ）
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 英語を録音してください（3モード同時解析）",
                    show_label=True,
                    container=True
                )
            
            # 解析ボタン
            analyze_btn = gr.Button(
                "🔬 3モード実験解析開始",
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
                    label="🇺🇸 英語モード結果（補正強）",
                    placeholder="英語モード解析結果",
                    elem_classes=["english-result", "result-box"],
                    lines=2
                )
                
                japanese_output = gr.Textbox(
                    label="🇯🇵 日本語モード結果（生データ）",
                    placeholder="日本語モード解析結果",
                    elem_classes=["japanese-result", "result-box"],
                    lines=2
                )
                
                cleaned_output = gr.Textbox(
                    label="✨ クリーンアップ結果（カナのみ）",
                    placeholder="カタカナ・ひらがなのみ抽出結果",
                    elem_classes=["cleaned-result", "result-box"],
                    lines=2
                )
                
                auto_output = gr.Textbox(
                    label="🌍 自動検出結果",
                    placeholder="自動言語検出結果",
                    elem_classes=["auto-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_japanese_mode_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, japanese_output, cleaned_output, auto_output]
            )
            
            gr.Markdown("""
            ---
            ### 🔬 実験の狙い
            
            - **補正率比較**: どのモードが実際の発音に近いか？
            - **カタカナ化**: 日本語モードで自然にカタカナが出るか？
            - **言語検出**: 英語発音を何語として認識するか？
            - **実用性**: 複雑な変換処理なしで目的達成できるか？
            
            **仮説**: 日本語モードなら「got to」→「ガット」のような実音が出るかも
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🔬 日本語モード実験版英語発音解析システム 起動中...")
    setup_whisper()
    
    app = create_japanese_mode_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7868,
        share=False
    )