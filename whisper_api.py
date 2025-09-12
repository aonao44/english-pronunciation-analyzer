#!/usr/bin/env python3
"""
Web API for Whisper transcription
シンプルなFlask APIでWhisper処理を提供
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os
import base64
import difflib

app = Flask(__name__)
CORS(app)  # React アプリからのアクセスを許可

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

def transcribe_with_whisper(audio_data):
    """
    音声データをWhisperで文字起こし（誤認識促進設定）
    """
    model = setup_whisper()
    
    try:
        # 一時ファイルに音声データを保存
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        print(f"🎤 音声ファイルを分析中: {tmp_file_path}")
        
        # 英語認識で実際の発音を取得
        result = model.transcribe(
            tmp_file_path,
            language="en",          # 英語として認識
            temperature=0.8,        # 少し高めで多様性を持たせる
            best_of=3,             # 候補数を適度に設定
            beam_size=3,           # ビーム探索を適度に設定
            compression_ratio_threshold=2.0,  # 品質基準を緩める
            logprob_threshold=-1.5  # 確信度基準を緩める
        )
        
        raw_text = result["text"].strip()
        print(f"📝 Whisper結果: '{raw_text}'", flush=True)
        print(f"📋 結果の長さ: {len(raw_text)}", flush=True)
        print(f"📋 結果が空: {raw_text == ''}", flush=True)
        
        # 一時ファイルを削除
        os.unlink(tmp_file_path)
        
        return raw_text
        
    except Exception as e:
        print(f"❌ Whisper文字起こし失敗: {e}")
        # 一時ファイルを削除（エラー時も）
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
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

def should_exclude_result(reference: str, recognized: str) -> bool:
    """
    明らかにかけ離れた結果のみを除外
    """
    if not reference or not recognized:
        return False
    
    # 簡単な音韻変換（最小限）
    def to_simple_phonetic(text):
        simple = text.lower()
        # 最も基本的な変換のみ
        simple = simple.replace('th', 's')  # think → sink
        simple = simple.replace('r', 'l')   # r/l混同
        simple = simple.replace('v', 'b')   # v/b混同
        return simple
    
    ref_phonetic = to_simple_phonetic(reference)
    rec_phonetic = to_simple_phonetic(recognized)
    
    # 類似度計算
    similarity = difflib.SequenceMatcher(
        None, ref_phonetic, rec_phonetic
    ).ratio()
    
    # 30%未満は除外
    should_exclude = similarity < 0.3
    
    print(f"🔍 除外判定: '{reference}' vs '{recognized}'")
    print(f"   類似度: {similarity:.3f} ({'除外' if should_exclude else '許可'})")
    
    return should_exclude

def convert_japanese_to_katakana(text):
    """
    日本語（ひらがな・漢字・数字）をカタカナに変換
    """
    print(f"🇯🇵 日本語→カタカナ変換入力: '{text}'", flush=True)
    
    if not text:
        return "？？？"
    
    result = text
    
    # 数字をカタカナに変換
    number_map = {
        '0': 'ゼロ', '1': 'イチ', '2': 'ニー', '3': 'サン', '4': 'ヨン',
        '5': 'ゴ', '6': 'ロク', '7': 'ナナ', '8': 'ハチ', '9': 'キュー',
        '10': 'ジュー'
    }
    
    for num, kata in number_map.items():
        result = result.replace(num, kata)
    
    # よくある漢字をカタカナに変換
    kanji_map = {
        '人': 'ニン', '時': 'ジ', '分': 'フン', '秒': 'ビョー',
        '年': 'ネン', '月': 'ツキ', '日': 'ニチ',
        '一': 'イチ', '二': 'ニー', '三': 'サン', '四': 'ヨン', '五': 'ゴ',
        '六': 'ロク', '七': 'ナナ', '八': 'ハチ', '九': 'キュー', '十': 'ジュー',
        '百': 'ヒャク', '千': 'セン', '万': 'マン',
        '世': 'セ', '界': 'カイ', '学': 'ガク', '校': 'コー', '先': 'セン', '生': 'セイ',
        '今': 'イマ', '何': 'ナニ', '私': 'ワタシ', '大': 'ダイ', '小': 'ショー'
    }
    
    for kanji, kata in kanji_map.items():
        result = result.replace(kanji, kata)
    
    # ひらがなをカタカナに変換（Unicodeコード変換）
    katakana_result = ""
    for char in result:
        if '\u3040' <= char <= '\u309F':  # ひらがな範囲
            # ひらがな → カタカナ変換
            katakana_char = chr(ord(char) + 0x60)
            katakana_result += katakana_char
        elif '\u30A0' <= char <= '\u30FF':  # カタカナ範囲
            katakana_result += char  # そのまま
        elif char.isalnum():  # 英数字が残っている場合
            katakana_result += '？'
        else:
            katakana_result += char  # 記号等はそのまま
    
    print(f"🎌 日本語→カタカナ変換結果: '{katakana_result}'", flush=True)
    return katakana_result

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    音声データを受け取ってWhisperで文字起こし
    """
    try:
        # リクエストから音声データを取得
        if 'audio' not in request.files:
            return jsonify({'error': '音声ファイルがありません'}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        if len(audio_data) == 0:
            return jsonify({'error': '音声データが空です'}), 400
        
        
        # Whisperで文字起こし
        raw_text = transcribe_with_whisper(audio_data)
        
        # 英語→カタカナ変換
        katakana_text = convert_to_katakana_simple(raw_text)
        
        return jsonify({
            'success': True,
            'whisper_raw': raw_text,
            'whisper_katakana': katakana_text
        })
        
    except Exception as e:
        print(f"❌ API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    return jsonify({'status': 'OK', 'message': 'Whisper API is running'})

if __name__ == '__main__':
    print("🚀 Whisper API サーバー起動中...")
    setup_whisper()  # 起動時にモデルをロード
    app.run(host='0.0.0.0', port=5001, debug=True)