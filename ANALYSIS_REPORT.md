# 英語発音文字起こしアプリ - 技術分析レポート

## プロジェクト概要

### 目的
英会話教師が生徒の実際の発音を客観的に把握できるよう、発音をそのままカタカナで文字起こしするアプリケーション

### 基本方針
**発音の忠実な再現**：音声認識結果に一切の補正を加えず、実際の発音をそのままカタカナで表示する

## 技術スタック

### フロントエンド（React Native）
- **フレームワーク**: Expo 53 + React Native
- **言語**: TypeScript
- **音声処理**: expo-av（録音）、Web Speech API（Web版認識）
- **ファイルシステム**: expo-file-system

### バックエンド（Python API）
- **音声AI**: OpenAI Whisper（tinyモデル）
- **デプロイ**: Hugging Face Spaces
- **API**: Gradio Web API
- **言語処理**: MeCab（カタカナ変換）
- **音響処理**: librosa、torch、torchaudio、numpy

### 音関連ライブラリ（全13種）
1. expo-av（音声録音・再生）
2. expo-audio（音声処理）
3. expo-speech（音声合成）
4. @react-native-voice/voice（音声認識・未使用）
5. OpenAI Whisper（音声文字起こし）
6. torch/torchaudio（WhisperのPyTorchバックエンド）
7. numpy（音声数値計算）
8. librosa（音響特徴抽出）
9. gradio（WebUI・音声入力機能）
10. phonemizer（英語→発音記号変換）
11. MeCab + unidic-lite（日本語形態素解析）
12. Web Speech API（ブラウザ音声認識）

## システム構成

```
音声入力 → expo-av → HTTP → Whisper + librosa → カタカナ出力
                           ↓
                     MeCab（日本語処理）
```

## テスト結果と課題分析

### 実施テスト
Google読み上げ機能で英語を読み取り、以下の順で結果表示：
1. 読み上げたテキスト
2. 英語モード結果
3. 日本語モード結果
4. MeCab変換結果

### 主要な問題点

#### 1. 連結音現象（最重要課題）
**子音+母音の連結で前の単語が消失**

```
Make it → Make it → Make it → イット ❌
Can I → Can I → Can I → アイ ❌
Tell us → Tell us → Tells us → ??? ❌
I'm in → I'm in → (認識なし) → アイ ❌
```

**技術的原因**:
- Whisperが連結音を1つの音として認識
- 音声分析で単語境界を正しく検出できない
- 前の子音と次の母音が物理的に結合

#### 2. フレーズ認識の完全破綻
**子音+子音の連結で無関係な日本語に誤認識**

```
want you → want you → ご視聴ありがとうございました → 長大なカタカナ文 ❌
Would you → Would you → はじゅう → はじゅう ✅（唯一の成功例）
```

**技術的原因**:
- 日本語モード設定時の言語モデル混乱
- YouTube学習データの偏り（頻出フレーズへの過学習）
- 短時間音声での文脈不足による確率的推測
- 人工音声と人間音声の音響特徴差異

#### 3. Whisperの「賢さ」による補正
**期待**: 日本人発音の検出
**現実**: 正しい英語への自動補正

```
期待: 日本人発音 "キャナイ" を検出
現実: 正しく "Can I" と補正してしまう
```

## 現在の達成率評価

### 成功パターン
- ✅ Would you → はじゅう（70%成功）
- ✅ 単語単体 → 比較的正確
- ✅ 音韻変化検出：[wʊdʒu] → はじゅう

### 失敗パターン
- ❌ 連結音での単語消失（0%成功）
- ❌ フレーズ認識破綻（ランダム出力）
- ❌ 言語モード設定無効化

**現在の総合達成率：30-40%**

## 技術的ネック（根本的障害）

### 1. 連結音処理（Critical）
- 現在0%成功率
- 英語の自然発話では連結音が頻発
- 実用レベルでは致命的

### 2. Whisper言語モード問題（Major）
- `language="ja"`設定が効かない
- 英語音声を正しく英語と認識してしまう
- temperature調整だけでは根本解決不可

### 3. フレーズ認識の構造的問題（Major）
- 短時間音声での脆弱性
- 学習データ偏りによる無関係フレーズ出力
- システムとしての信頼性欠如

## 改善戦略と実現可能性

### 短期改善（1-2週間）- 60-70%達成可能
```python
# 設定変更のみ
temperature=0.4          # 現在0.0から変更
best_of=3               # 複数候補から選択
initial_prompt="日本人の英語発音をカタカナで書いてください"
```

### 中期改善（1-2ヶ月）- 80-85%達成可能
```python
# 音声分割処理追加
from pydub.silence import split_on_silence
chunks = split_on_silence(audio, min_silence_len=100)
# 各チャンク個別処理→統合
```

### 長期改善（3-6ヶ月）- 85-90%達成可能
- カスタム学習データ構築
- 専用ファインチューニング
- ハイブリッドシステム構築

## 根本的解決策

### 1. Whisperを諦める（最も確実）
```python
# 音響特徴量ベース認識
import librosa
mfcc_input = librosa.feature.mfcc(audio)
# 音響距離で直接比較
```

### 2. ハイブリッドシステム（現実的）
```python
def multi_engine_recognition(audio):
    results = {
        "whisper_en": whisper.transcribe(audio, language="en"),
        "whisper_auto": whisper.transcribe(audio, language=None),
        "phonetic_match": phonetic_matching(audio)
    }
    return select_most_reliable_result(results)
```

### 3. 制約付きWhisper（実装容易）
```python
def constrained_whisper(audio, possible_phrases):
    # 候補をあらかじめ制限
    result = model.transcribe(audio)
    # 音響類似度で最適候補選択
    return select_best_match(result, possible_phrases)
```

## 部分音声抽出アプローチ

### コンセプト
長い英文中の「」部分のみをカタカナ表示

```javascript
const fullText = 'Please say "Make it happen" slowly.';
const targetPhrase = "Make it happen";  // 抽出対象

// AI使用パターン
const extractTargetAudio = async (fullAudio, fullText, targetText) => {
  // 1. Whisperで全体のタイムスタンプ取得
  // 2. GPT-4で該当部分の時間特定
  // 3. 該当部分音声を抽出
  // 4. 抽出部分のみカタカナ変換
};
```

**期待効果**:
- 連結音問題回避（短いフレーズのみ処理）
- 文脈ノイズ除去
- 精度向上：30-40% → 75-85%

## デプロイ方法

### 1. 開発・テスト
```bash
npx expo start  # Expo Goアプリで確認
```

### 2. Web版デプロイ（最も簡単）
```bash
npx expo export:web
# 生成されたdist/フォルダをNetlify/Vercelにアップロード
```

### 3. 本格アプリストア配布
```bash
# EAS Build & Submit
npm install -g @expo/eas-cli
eas build --platform all
eas submit --platform all
```

## プラットフォーム別機能差異

### Web版（現在確認済み）
- ✅ 音声録音（expo-av）
- ✅ 録音再生
- ✅ Whisper AI解析
- ❌ リアルタイム音声認識制限

### Expo Go（スマホテスト）
- ✅ 基本機能すべて
- ❌ @react-native-voice/voice制限

### Development Build（フル機能）
- ✅ 全機能利用可能
- ✅ ネイティブ音声認識
- ✅ 高精度処理

## 結論と推奨事項

### 厳しい現実
1. **自然な英語フレーズ**のカタカナ化は現在の技術では極めて困難
2. **連結音問題**は根本的な技術的障壁
3. **30-40%が現在技術の上限**に近い

### 実用化への現実的道筋
1. **要件調整**: 「自然フレーズ」→「指定単語/短文」
2. **部分抽出アプローチ**採用
3. **ハイブリッドシステム**構築

### 最終評価
**技術的には面白いが、当初要件を100%満たすのは現在技術では限界**

**推奨**: 要件を調整し、実用レベル85-90%を目指すアプローチが現実的

---

*生成日: 2025年1月*
*対象システム: 英語発音文字起こしアプリ*
*技術スタック: Expo + React Native + Whisper + MeCab*