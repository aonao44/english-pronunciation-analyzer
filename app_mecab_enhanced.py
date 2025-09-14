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
    """MeCabをセットアップ（読み情報重視）"""
    global mecab
    if mecab is None:
        print("MeCabセットアップ中...")
        try:
            # UniDicで読み情報を取得（最優先）
            mecab = MeCab.Tagger("-Oyomi -d /opt/homebrew/lib/mecab/dic/unidic")
            print("🔧 UniDic辞書で読み取得モード使用")
        except:
            try:
                # IPAdicで読み情報を取得
                mecab = MeCab.Tagger("-Oyomi")
                print("🔧 IPAdic辞書で読み取得モード使用")
            except:
                try:
                    # 通常のMeCabで詳細情報取得
                    mecab = MeCab.Tagger("-Ochasen")
                    print("🔧 Chasen形式で詳細情報取得")
                except:
                    # 最低限の設定
                    mecab = MeCab.Tagger()
                    print("🔧 基本MeCab設定使用")
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
            temperature=0.3,      # 少し多様性を持たせて音韻認識を促進
            best_of=5,           # 適度な候補数
            beam_size=5,         # 適度な探索幅
            compression_ratio_threshold=2.0,  # より厳格な品質基準
            logprob_threshold=-0.8,           # 確信度を少し緩める
            no_speech_threshold=0.4,          # 音声検出感度向上
            condition_on_previous_text=False, # 前文脈影響排除
            initial_prompt="Phonetic pronunciation practice with sounds like one two three", # 音韻重視のコンテキスト
            fp16=False,          # 精度重視でfp16無効化
        )
        
        english_text = result["text"].strip()
        print(f"📝 英語モード結果（生）: '{english_text}'")
        
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
            temperature=0.0,     # より厳格に日本語認識
            best_of=5,           # 候補数を減らして安定化
            beam_size=5,         # 探索幅を減らして安定化
            compression_ratio_threshold=3.0,  # 日本語に適した品質基準
            logprob_threshold=-0.3,           # より高い確信度要求
            no_speech_threshold=0.6,          # 無音判定を厳格に
            condition_on_previous_text=False, # 前文脈影響排除
            initial_prompt="", # プロンプトを空に（繰り返し問題回避）
            fp16=False,          # 精度重視でfp16無効化
        )
        
        japanese_text = result["text"].strip()
        print(f"📝 日本語モード結果（生）: '{japanese_text}'")
        
        print(f"📝 日本語モード結果: '{japanese_text}'")
        return japanese_text
        
    except Exception as e:
        print(f"❌ 日本語モード解析失敗: {e}")
        raise e

def convert_kanji_to_katakana_mecab(text: str) -> str:
    """MeCabを使って漢字→カタカナ変換（改良版）"""
    if not text:
        return "？？？"
    
    print(f"🔧 MeCab変換中: '{text}'")
    
    # 既に全部ひらがなの場合、直接カタカナに変換
    if re.match(r'^[あ-ん゛゜ー・\s]+$', text):
        print(f"🔧 ひらがなを直接カタカナに変換")
        katakana_result = hiragana_to_katakana(text.strip())
        katakana_result = clean_katakana_text(katakana_result)
        print(f"🔧 直接変換結果: '{katakana_result}'")
        return katakana_result
    
    # 既に全部カタカナの場合、そのまま返す
    if re.match(r'^[ァ-ヶー・\s]+$', text):
        print(f"🔧 既にカタカナ: '{text.strip()}'")
        return clean_katakana_text(text.strip())
    
    mecab_tagger = setup_mecab()
    
    try:
        # -Oyomiオプションの場合、直接読みが返される
        result = mecab_tagger.parse(text).strip()
        
        if result and result != text:
            # MeCab読みモードで成功した場合
            print(f"🔧 MeCab読みモード結果: '{result}'")
            # ひらがなをカタカナに変換
            katakana_result = hiragana_to_katakana(result)
            # 不要な文字を除去
            katakana_result = clean_katakana_text(katakana_result)
            
            if katakana_result and katakana_result != "？？？":
                print(f"🔧 最終カタカナ結果: '{katakana_result}'")
                return katakana_result
        
        # 読みモードで失敗した場合、ノード解析にフォールバック
        print("🔧 ノード解析モードにフォールバック")
        node = mecab_tagger.parseToNode(text)
        katakana_parts = []
        
        while node:
            surface = node.surface
            features = node.feature.split(',')
            
            if surface and surface.strip():
                # 各種辞書形式に対応
                reading = ""
                
                if len(features) >= 8 and features[7] != '*':
                    # UniDic形式：読み情報
                    reading = features[7]
                elif len(features) >= 2 and features[1] != '*':
                    # IPAdic形式：読み情報
                    reading = features[1]
                else:
                    # 読み情報がない場合は表層形
                    reading = surface
                
                # カタカナに変換
                katakana = hiragana_to_katakana(reading)
                
                # カタカナでない場合は推測変換
                if not re.match(r'^[ァ-ヶー・\s]+$', katakana):
                    katakana = smart_katakana_conversion(surface)
                
                katakana_parts.append(katakana)
            
            node = node.next
        
        result = ''.join(katakana_parts)
        result = clean_katakana_text(result)
        
        print(f"🔧 MeCab最終結果: '{result}'")
        return result if result else "？？？"
        
    except Exception as e:
        print(f"❌ MeCab変換エラー: {e}")
        # エラー時は基本的なカタカナ変換
        return smart_katakana_conversion(text)

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

def smart_katakana_conversion(text: str) -> str:
    """賢いカタカナ変換（改良版）"""
    if not text:
        return "？"
    
    # 既にカタカナの場合はそのまま
    if re.match(r'^[ァ-ヶー・\s]+$', text):
        return text
    
    # ひらがなの場合はカタカナに変換
    if re.match(r'^[ひらがな\u3040-\u309F\s]+$', text):
        return hiragana_to_katakana(text)
    
    # 漢字の読み変換辞書（拡張版）
    kanji_readings = {
        # 基本的な漢字
        '私': 'ワタシ', '僕': 'ボク', '君': 'キミ', '彼': 'カレ', '彼女': 'カノジョ',
        '今': 'イマ', '明日': 'アシタ', '昨日': 'キノウ', '今日': 'キョウ',
        '時間': 'ジカン', '分': 'フン', '秒': 'ビョウ', '時': 'ジ',
        '行く': 'イク', '来る': 'クル', '見る': 'ミル', '聞く': 'キク',
        '話す': 'ハナス', '言う': 'イウ', '思う': 'オモウ', '知る': 'シル',
        '学校': 'ガッコウ', '先生': 'センセイ', '生徒': 'セイト', '学生': 'ガクセイ',
        '家': 'イエ', '部屋': 'ヘヤ', '会社': 'カイシャ', '仕事': 'シゴト',
        '食べる': 'タベル', '飲む': 'ノム', '寝る': 'ネル', '起きる': 'オキル',
        '買う': 'カウ', '売る': 'ウル', '作る': 'ツクル', '書く': 'カク',
        '読む': 'ヨム', '歌う': 'ウタウ', '踊る': 'オドル', '走る': 'ハシル',
        # 数字
        '一': 'イチ', '二': 'ニ', '三': 'サン', '四': 'ヨン', '五': 'ゴ',
        '六': 'ロク', '七': 'ナナ', '八': 'ハチ', '九': 'キュウ', '十': 'ジュウ',
        '百': 'ヒャク', '千': 'セン', '万': 'マン', '億': 'オク',
        # よく出る単語
        '和': 'ワ', '乗': 'ノ', '度': 'ド', '以': 'イ', '内': 'ナイ',
        '用': 'ヨウ', '所': 'ショ', '業': 'ギョウ', '性': 'セイ', '的': 'テキ'
    }
    
    # 漢字変換を試行
    result = text
    for kanji, reading in kanji_readings.items():
        result = result.replace(kanji, reading)
    
    # 英語の場合
    if re.match(r'^[a-zA-Z\s]+$', text):
        english_readings = {
            'hello': 'ハロー', 'want': 'ワント', 'to': 'トゥー', 'go': 'ゴー',
            'got': 'ガット', 'going': 'ゴーイング', 'i': 'アイ', 'you': 'ユー',
            'the': 'ザ', 'and': 'アンド', 'is': 'イズ', 'it': 'イット',
            'good': 'グッド', 'time': 'タイム', 'what': 'ワット', 'how': 'ハウ',
            'need': 'ニード', 'needing': 'ニーディング', 'needed': 'ニーデッド',
            'really': 'リアリー', 'very': 'ベリー', 'much': 'マッチ', 'like': 'ライク'
        }
        
        lower_text = text.lower().strip()
        if lower_text in english_readings:
            return english_readings[lower_text]
    
    # 数字の場合
    if re.match(r'^[0-9]+$', text):
        return text
    
    # 変換できない場合
    return result if result != text else "？"

def guess_katakana_reading(text: str) -> str:
    """従来の推測関数（互換性のため残す）"""
    return smart_katakana_conversion(text)

def clean_katakana_text(text: str) -> str:
    """カタカナテキストのクリーンアップ（重複除去機能付き）"""
    if not text:
        return "？？？"
    
    # カタカナ・ひらがな・記号のみを保持
    cleaned = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s・ー]', '', text)
    
    # ひらがなをカタカナに変換
    cleaned = hiragana_to_katakana(cleaned)
    
    # 連続する空白を1つに
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 重複する単語を除去
    if cleaned:
        cleaned = remove_duplicate_words(cleaned)
    
    return cleaned if cleaned else "？？？"

def remove_duplicate_words(text: str) -> str:
    """連続する重複単語を除去（安全版）"""
    if not text:
        return text
    
    # スペースで明確に区切られた単語の重複のみ除去
    parts = text.split(' ')
    result_parts = []
    prev_part = None
    
    for part in parts:
        if part.strip() and part != prev_part:
            result_parts.append(part)
        prev_part = part
    
    result = ' '.join(result_parts)
    
    # 明らかな完全重複パターンのみ除去（より厳格に）
    # 「アリガトウアリガトウ」のような同じ単語が2回続く場合のみ
    if len(result) >= 8:  # 最小8文字以上
        # 3文字以上の単位でのみ重複チェック
        for word_len in range(8, len(result) // 2 + 1):  
            first_half = result[:word_len]
            second_half = result[word_len:word_len*2]
            
            # 完全一致 かつ 意味のある長さの場合のみ
            if (first_half == second_half and 
                word_len >= 4 and  # 4文字以上
                len(result) == word_len * 2):  # 完全に2倍
                print(f"🔧 重複パターン検出: '{first_half}' x2")
                return first_half
    
    return result


def process_mecab_enhanced_pronunciation(audio_file):
    """MeCab強化版発音解析のメイン処理"""
    if audio_file is None:
        return "❌ 音声を録音してください", "", "", ""
    
    try:
        # Step 1: 英語モードで解析（高精度設定）
        english_result = transcribe_english_mode(audio_file)
        
        # Step 2: 日本語モードで解析（高精度設定）
        japanese_result = transcribe_japanese_mode(audio_file)
        
        # Step 3: MeCabで漢字→カタカナ変換
        mecab_result = convert_kanji_to_katakana_mecab(japanese_result)
        
        return (
            "✅ MeCab強化版解析完了",
            english_result,
            japanese_result,
            mecab_result
        )
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return f"❌ エラー: {str(e)}", "", "", ""

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
            
            """)
            
            # 音声入力エリア
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 英語を録音してください（MeCab強化版）",
                    show_label=True,
                    container=True,
                    show_download_button=False,
                    show_share_button=False,
                    max_length=30  # 最大30秒
                )
            
            # ボタンエリア
            with gr.Row():
                analyze_btn = gr.Button(
                    "🔧 MeCab強化解析開始",
                    variant="primary",
                    size="lg",
                    scale=3
                )
                clear_btn = gr.Button(
                    "🗑️ クリア",
                    variant="secondary",
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
                
            
            # イベントハンドリング
            analyze_btn.click(
                process_mecab_enhanced_pronunciation,
                inputs=[audio_input],
                outputs=[status_output, english_output, japanese_output, mecab_output]
            )
            
            # クリア機能
            clear_btn.click(
                lambda: (None, "", "", "", ""),
                inputs=[],
                outputs=[audio_input, status_output, english_output, japanese_output, mecab_output]
            )
            
    
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