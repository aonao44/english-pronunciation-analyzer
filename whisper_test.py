#!/usr/bin/env python3
"""
超シンプル版: Whisperの誤認識を3行で実現
"""
import whisper
import sys
import os

def setup_whisper():
    """Whisperモデルをセットアップ"""
    print("Whisper tinyモデルをロード中...")
    try:
        # 1. 小さいモデルを読み込み（誤認識しやすい）
        model = whisper.load_model("tiny")
        print("✅ Whisperモデル読み込み完了")
        return model
    except Exception as e:
        print(f"❌ Whisperモデル読み込み失敗: {e}")
        return None

def transcribe_raw(model, audio_file):
    """
    補正なしの生の発音を文字起こし
    """
    if not os.path.exists(audio_file):
        print(f"❌ 音声ファイルが見つかりません: {audio_file}")
        return None
        
    print(f"🎤 音声ファイルを分析中: {audio_file}")
    
    try:
        # 2. 誤認識を促進する設定で文字起こし
        result = model.transcribe(
            audio_file,
            language="en",
            temperature=1.0,        # 高ランダム性 = 誤認識促進
            best_of=1,             # 候補を1つに制限
            beam_size=1,           # ビーム探索を最小に
            compression_ratio_threshold=1.5,  # 低品質許容
            logprob_threshold=-2.0  # 低確信度許容
        )
        
        raw_text = result["text"].strip()
        print(f"📝 補正なし結果: '{raw_text}'")
        return raw_text
        
    except Exception as e:
        print(f"❌ 文字起こし失敗: {e}")
        return None

def convert_to_katakana_simple(text):
    """
    シンプルなカタカナ変換（基本的な置換のみ）
    """
    if not text:
        return "？？？"
    
    # 基本的な英語音 → カタカナ変換
    replacements = {
        'hello': 'ヘロー',
        'hallo': 'ハロー', 
        'helo': 'ヘロ',
        'harrow': 'ハロー',
        'water': 'ウォーター',
        'warter': 'ワーター',
        'woter': 'ウォーター',
        'thank': 'サンク',
        'sank': 'サンク',
        'you': 'ユー',
        'good': 'グッド',
        'gud': 'グッド',
        'morning': 'モーニング',
        'mornin': 'モーニン'
    }
    
    result = text.lower()
    for eng, kat in replacements.items():
        result = result.replace(eng, kat)
    
    # 残った英字は？に
    import re
    result = re.sub(r'[a-zA-Z]+', '？', result)
    
    return result

def main():
    """
    メイン実行関数
    """
    print("🎯 Whisper補正なし文字起こしテスト")
    print("=" * 50)
    
    # Whisperセットアップ
    model = setup_whisper()
    if not model:
        return
    
    # コマンドライン引数から音声ファイルパス取得
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        # デフォルトのサンプルファイルパス
        audio_file = "sample_recording.wav"
        print(f"⚠️  使用方法: python whisper_test.py <音声ファイル>")
        print(f"📁 デフォルトファイル '{audio_file}' を探します...")
    
    # 文字起こし実行
    raw_result = transcribe_raw(model, audio_file)
    
    if raw_result:
        # カタカナ変換
        katakana_result = convert_to_katakana_simple(raw_result)
        
        print("\n🎉 結果:")
        print(f"   英語: {raw_result}")
        print(f"   カタカナ: {katakana_result}")
        print("\n💡 より良い結果を得るには:")
        print("   1. より下手な発音で録音してみる")
        print("   2. 音声品質を下げてみる") 
        print("   3. base モデルも試してみる")
    else:
        print("❌ 文字起こしに失敗しました")

if __name__ == "__main__":
    main()