#!/usr/bin/env python3
"""
発音精度フィルター
基準テキストとの類似度でWhisper結果をフィルタリング
"""
import difflib
from typing import Optional, List, Tuple

class PronunciationFilter:
    def __init__(self):
        # 音韻変換テーブル（英語→音韻記号風）
        self.phonetic_map = {
            # 母音
            'a': 'ə', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
            'ai': 'aɪ', 'ay': 'aɪ', 'ei': 'eɪ', 'ey': 'eɪ',
            'oo': 'u', 'ou': 'aʊ', 'ow': 'aʊ',
            
            # 子音（日本人が混同しやすい音）
            'th': 's', 'f': 'h', 'v': 'b',
            'r': 'l', 'l': 'r',  # 日本人のr/l混同
            'b': 'p', 'p': 'b',  # 無声/有声混同
            'd': 't', 't': 'd',
            'g': 'k', 'k': 'g',
            
            # 語尾の変化
            'ed': 't', 'ing': 'in',
        }
    
    def to_phonetic(self, text: str) -> str:
        """テキストを音韻的表現に変換"""
        result = text.lower()
        
        # 長い音から先に変換（"th"が"t"+"h"より先）
        for original, phonetic in sorted(
            self.phonetic_map.items(), 
            key=lambda x: -len(x[0])
        ):
            result = result.replace(original, phonetic)
        
        return result
    
    def calculate_similarity(self, reference: str, recognized: str) -> float:
        """
        2つのテキストの音韻的類似度を計算（0.0-1.0）
        """
        # 音韻的変換
        ref_phonetic = self.to_phonetic(reference)
        rec_phonetic = self.to_phonetic(recognized)
        
        # 類似度計算（SequenceMatcher使用）
        similarity = difflib.SequenceMatcher(
            None, ref_phonetic, rec_phonetic
        ).ratio()
        
        return similarity
    
    def is_acceptable_pronunciation(
        self, 
        reference: str, 
        recognized: str, 
        threshold: float = 0.4
    ) -> Tuple[bool, float]:
        """
        発音が許容範囲内かどうか判定
        
        Args:
            reference: 基準テキスト ("need in")
            recognized: 認識結果 ("needy", "katon")
            threshold: 許容する最小類似度 (0.4 = 40%)
        
        Returns:
            (判定結果, 類似度スコア)
        """
        similarity = self.calculate_similarity(reference, recognized)
        is_acceptable = similarity >= threshold
        
        print(f"📏 類似度判定:")
        print(f"   基準: '{reference}' → 音韻: '{self.to_phonetic(reference)}'")
        print(f"   認識: '{recognized}' → 音韻: '{self.to_phonetic(recognized)}'")
        print(f"   類似度: {similarity:.3f} ({'✅合格' if is_acceptable else '❌不合格'})")
        
        return is_acceptable, similarity
    
    def get_pronunciation_feedback(
        self, 
        reference: str, 
        recognized: str
    ) -> dict:
        """
        発音フィードバック情報を生成
        """
        is_acceptable, similarity = self.is_acceptable_pronunciation(
            reference, recognized
        )
        
        if similarity >= 0.8:
            level = "excellent"
            message = "素晴らしい発音です！"
        elif similarity >= 0.6:
            level = "good" 
            message = "良い発音です。"
        elif similarity >= 0.4:
            level = "fair"
            message = "もう少し練習してみましょう。"
        else:
            level = "poor"
            message = "基準テキストと大きく異なります。"
        
        return {
            "acceptable": is_acceptable,
            "similarity": similarity,
            "level": level,
            "message": message,
            "reference": reference,
            "recognized": recognized
        }

# テスト用関数
def test_filter():
    filter_system = PronunciationFilter()
    
    test_cases = [
        ("need in", "needy"),      # 類似 → 許容
        ("need in", "neetin"),     # 很類似 → 許容  
        ("need in", "katon"),      # 全然違う → 除外
        ("hello", "helo"),         # 類似 → 許容
        ("hello", "zebra"),        # 全然違う → 除外
        ("water", "warter"),       # 類似 → 許容
    ]
    
    print("🧪 発音フィルターテスト")
    print("=" * 50)
    
    for reference, recognized in test_cases:
        feedback = filter_system.get_pronunciation_feedback(reference, recognized)
        print(f"\n結果: {feedback['message']}")
        print("-" * 30)

if __name__ == "__main__":
    test_filter()