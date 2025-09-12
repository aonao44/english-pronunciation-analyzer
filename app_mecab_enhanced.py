#!/usr/bin/env python3
"""
MeCab強化版英語発音解析システム
日本語モード + MeCabで漢字→カタカナ変換 + 精度向上
"""
import gradio as gr
import whisper
import re
import MeCab
from typing import Dict, Any

# WhisperモデルとMeCab
model = None
mecab = None

def setup_whisper():
    """Whisperモデルをセットアップ"""
    global model
    if model is None:
        print("Whisper tinyモデルをロード中...")
        model = whisper.load_model("tiny")
        print("✅ Whisperモデル読み込み完了")
    return model

def setup_mecab():
    """MeCabをセットアップ"""
    global mecab
    if mecab is None:
        print("MeCabセットアップ中...")
        try:
            # UniDicを使用（読み情報が豊富）
            mecab = MeCab.Tagger("-Owakati -d /opt/homebrew/lib/mecab/dic/unidic")
        except:
            try:
                # デフォルト辞書を使用
                mecab = MeCab.Tagger("-Oyomi")
            except:
                # 最低限の設定
                mecab = MeCab.Tagger()
        print("✅ MeCabセットアップ完了")
    return mecab

def transcribe_english_mode(audio_file):
    """英語モードで音声認識（高精度設定）"""
    model = setup_whisper()
    
    try:
        print(f"🇺🇸 英語モード解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language="en",
            temperature=0.0,      # 精度重視（一貫性向上）
            best_of=5,           # 候補数増加
            beam_size=5,         # 探索幅増加
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=False,  # 前の文脈の影響を排除
            initial_prompt="",                 # プロンプトなし
        )
        
        english_text = result["text"].strip()
        print(f"📝 英語モード結果: '{english_text}'")
        
        return english_text
        
    except Exception as e:
        print(f"❌ 英語モード解析失敗: {e}")
        raise e

def transcribe_japanese_mode(audio_file):
    """日本語モードで音声認識（高精度設定）"""
    model = setup_whisper()
    
    try:
        print(f"🇯🇵 日本語モード解析中: {audio_file}")
        
        result = model.transcribe(
            audio_file,
            language="ja",
            temperature=0.0,      # 精度重視（一貫性向上）
            best_of=5,           # 候補数増加
            beam_size=5,         # 探索幅増加
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=False,  # 前の文脈の影響を排除
            initial_prompt="",                 # プロンプトなし
        )
        
        japanese_text = result["text"].strip()
        print(f"📝 日本語モード結果: '{japanese_text}'")
        
        return japanese_text
        
    except Exception as e:
        print(f"❌ 日本語モード解析失敗: {e}")
        raise e

def convert_kanji_to_katakana_mecab(text: str) -> str:
    """MeCabを使って漢字→カタカナ変換"""
    if not text:
        return "？？？"
    
    print(f"🔧 MeCab変換中: '{text}'")
    mecab_tagger = setup_mecab()
    
    try:
        # MeCabで形態素解析
        node = mecab_tagger.parseToNode(text)
        katakana_parts = []
        
        while node:
            # 表層形（元の文字）を取得
            surface = node.surface
            
            # 品詞情報を取得
            features = node.feature.split(',')
            
            if surface:  # 空でない場合のみ処理
                if len(features) > 7:
                    # 読み情報がある場合（UniDic形式）
                    reading = features[7] if features[7] != '*' else surface
                    # ひらがな→カタカナ変換
                    katakana = hiragana_to_katakana(reading)
                elif len(features) > 1:
                    # 基本的な形態素解析結果
                    reading = features[1] if features[1] != '*' else surface
                    katakana = hiragana_to_katakana(reading)
                else:
                    # 読み情報がない場合はそのまま
                    katakana = surface
                
                # カタカナでない場合は元の文字も保持
                if re.match(r'^[ァ-ヶー・\s]+$', katakana):
                    katakana_parts.append(katakana)
                elif re.match(r'^[ァ-ヶー・\s]+$', surface):
                    katakana_parts.append(surface)
                else:
                    # 漢字や英語の場合、読みを推測
                    katakana_parts.append(guess_katakana_reading(surface))
            
            node = node.next
        
        result = ''.join(katakana_parts)
        result = clean_katakana_text(result)
        
        print(f"🔧 MeCab変換結果: '{result}'")
        return result if result else "？？？"
        
    except Exception as e:
        print(f"❌ MeCab変換エラー: {e}")
        # MeCab失敗時は従来のクリーンアップを使用
        return clean_japanese_text(text)

def hiragana_to_katakana(text: str) -> str:
    """ひらがな→カタカナ変換"""
    if not text:
        return text
    
    result = ""
    for char in text:
        # ひらがな範囲（U+3040-U+309F）→カタカナ範囲（U+30A0-U+30FF）
        if '\u3040' <= char <= '\u309F':
            result += chr(ord(char) + 0x60)
        else:
            result += char
    return result

def guess_katakana_reading(text: str) -> str:
    """不明な文字列の読みを推測"""
    if not text:
        return "？"
    
    # 英語っぽい文字列の場合
    if re.match(r'^[a-zA-Z\s]+$', text):
        # 基本的な英語→カタカナ変換
        english_to_katakana = {
            'hello': 'ハロー', 'want': 'ワント', 'to': 'トゥー', 'go': 'ゴー',
            'got': 'ガット', 'going': 'ゴーイング', 'i': 'アイ', 'you': 'ユー',
            'the': 'ザ', 'and': 'アンド', 'is': 'イズ', 'it': 'イット',
            'good': 'グッド', 'time': 'タイム', 'what': 'ワット', 'how': 'ハウ'
        }
        
        lower_text = text.lower().strip()
        if lower_text in english_to_katakana:
            return english_to_katakana[lower_text]
    
    # 数字の場合
    if re.match(r'^[0-9]+$', text):
        return text  # 数字はそのまま
    
    # その他の場合は空文字（除去対象）
    return ""

def clean_katakana_text(text: str) -> str:
    """カタカナテキストのクリーンアップ"""
    if not text:
        return "？？？"
    
    # カタカナ・ひらがな・記号のみを保持
    cleaned = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s・ー]', '', text)
    
    # ひらがなをカタカナに変換
    cleaned = hiragana_to_katakana(cleaned)
    
    # 連続する空白を1つに
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else "？？？"

def clean_japanese_text(text: str) -> str:
    """従来の日本語テキストクリーンアップ（フォールバック用）"""
    if not text:
        return "？？？"
    
    # カタカナ・ひらがな・記号のみを抽出
    cleaned = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s・ー]', '', text)
    
    # 連続する空白を1つに
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else "？？？"

def process_mecab_enhanced_pronunciation(audio_file):
    """MeCab強化版発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", "", ""
    
    try:
        # Step 1: 英語モードで解析（高精度設定）
        english_result = transcribe_english_mode(audio_file)
        
        # Step 2: 日本語モードで解析（高精度設定）
        japanese_result = transcribe_japanese_mode(audio_file)
        
        # Step 3: MeCabで漢字→カタカナ変換
        mecab_result = convert_kanji_to_katakana_mecab(japanese_result)
        
        # Step 4: 従来のクリーンアップも実行（比較用）
        simple_clean = clean_japanese_text(japanese_result)
        
        return (
            "✅ MeCab強化版解析完了",
            english_result,
            japanese_result,
            mecab_result,
            simple_clean
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", "", ""

# MeCab強化版Gradioインターフェース
def create_mecab_enhanced_app():
    with gr.Blocks(
        title="MeCab強化版英語発音解析",
        theme=gr.themes.Soft(),
        css="""
        .main-container { max-width: 1200px; margin: 0 auto; }
        .result-box { font-size: 16px; padding: 16px; margin: 10px 0; border-radius: 8px; }
        .english-result { 
            background: linear-gradient(135deg, #f3e5f5, #e1bee7); 
            border: 2px solid #9c27b0; 
        }
        .japanese-result { 
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9); 
            border: 2px solid #4caf50; 
        }
        .mecab-result { 
            background: linear-gradient(135deg, #fff3e0, #ffe0b2); 
            border: 3px solid #ff9800; 
            font-weight: bold;
            font-size: 20px;
        }
        .simple-result { 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            border: 2px solid #2196f3; 
        }
        .status-box { 
            background: linear-gradient(135deg, #fce4ec, #f8bbd9); 
            border: 2px solid #e91e63;
            text-align: center;
            font-weight: bold;
        }
        .mecab-badge {
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
            # 🔧 MeCab強化版英語発音解析
            
            **MeCabで漢字→カタカナ変換 + Whisper精度向上** <span class="mecab-badge">MeCab</span>
            
            日本語モードの漢字出力をMeCabで正確にカタカナ変換
            
            ### 🔧 強化ポイント
            1. **MeCab変換**: 漢字→読み→カタカナの正確な変換
            2. **精度向上**: temperature=0.0、beam_size=5で一貫性向上
            3. **文脈排除**: 前の解析結果の影響を排除
            4. **比較表示**: MeCab版vs従来版の結果比較
            
            ### 🎯 期待結果
            - **日本語モード**: "私は和んと行く"（漢字混在）
            - **MeCab変換**: "ワタシハワントイク"（正確なカタカナ）
            - **従来版**: "ワント"（漢字除去のみ）
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 英語を録音してください（MeCab強化版）",
                    show_label=True,
                    container=True
                )
            
            # 解析ボタン
            analyze_btn = gr.Button(
                "🔧 MeCab強化解析開始",
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
                    label="🇺🇸 英語モード結果（精度向上版）",
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
                
                mecab_output = gr.Textbox(
                    label="🔧 MeCab変換結果（漢字→カタカナ）",
                    placeholder="MeCabによる正確なカタカナ変換結果",
                    elem_classes=["mecab-result", "result-box"],
                    lines=3
                )
                
                simple_output = gr.Textbox(
                    label="📝 従来版クリーンアップ（比較用）",
                    placeholder="従来の漢字除去のみ",
                    elem_classes=["simple-result", "result-box"],
                    lines=2
                )
            
            # イベントハンドリング
            analyze_btn.click(
                process_mecab_enhanced_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, japanese_output, mecab_output, simple_output]
            )
            
            gr.Markdown("""
            ---
            ### 🔧 MeCab強化版の特徴
            
            - **正確な読み変換**: 漢字を正しい読みでカタカナ化
            - **一貫性向上**: 同じ音声で毎回同じ結果を生成
            - **形態素解析**: 文字単位でなく形態素単位での変換
            - **比較機能**: MeCab版と従来版の結果を同時表示
            
            **技術**: MeCab + UniDic辞書による高精度日本語処理
            """)
    
    return app

# アプリケーション起動
if __name__ == "__main__":
    print("🔧 MeCab強化版英語発音解析システム 起動中...")
    setup_whisper()
    setup_mecab()
    
    app = create_mecab_enhanced_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7869,
        share=False
    )