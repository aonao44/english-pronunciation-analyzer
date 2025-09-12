# 英語発音解析システム

英語学習者の**実際の発音**をカタカナで表示する教育支援ツールです。

## ⭐ 推奨版: MeCab強化版

**`app_mecab_enhanced.py`** - 最も精度が高く実用的なバージョン

### 特徴
- MeCabによる漢字→カタカナの正確な変換
- Whisper精度向上（同じ音声で毎回同じ結果）
- 英語・日本語・自動検出の3モード同時解析
- 実際の発音「got to」→「ガタ」を忠実に再現

## 🚀 使い方

### 1. 環境準備
```bash
# 依存関係をインストール
pip3 install gradio whisper torch
pip3 install mecab-python3 unidic-lite
```

### 2. システム起動
```bash
# 推奨版を起動
python3 app_mecab_enhanced.py
```

### 3. ブラウザでアクセス
```
http://localhost:7869
```

### 4. 操作方法
1. マイクボタンをクリックして英語を録音
2. 「MeCab強化解析開始」をクリック  
3. 4つの結果を比較確認：
   - **英語モード**: 補正された標準英語
   - **日本語モード**: 漢字混じりの生データ
   - **MeCab変換**: 正確なカタカナ変換 ⭐
   - **従来版**: 漢字除去のみ

## 📱 他のバージョン（参考）

| ファイル名 | ポート | 特徴 |
|---|---|---|
| `app_simple.py` | 7861 | 軽量シンプル版 |
| `app_optimized.py` | 7863 | 高速処理版 |
| `app_japanese_mode.py` | 7868 | 3言語モード比較 |
| `app_phonetic_symbols.py` | 7867 | IPA発音記号対応 |

## 🎯 使用例

**発音例**: 「I want to go」を「アイワナゴー」と発音した場合

- **英語モード**: "I want to go" （補正済み）
- **MeCab変換**: "アイワナゴー" （実際の音）⭐

## トラブルシューティング

### MeCabエラーが出る場合
```bash
# macOS
brew install mecab mecab-ipadic
pip3 install mecab-python3

# エラーが続く場合は軽量版を使用
python3 app_simple.py  # → http://localhost:7861
```

### 音声認識されない場合
- マイクの許可設定を確認
- ブラウザのマイクアクセス許可を確認
- 雑音の少ない環境で録音

---

**開発者向け**: 詳細な技術情報は各Pythonファイルのコメントを参照
