# 英語発音解析システム

英語学習者の**実際の発音**をカタカナで表示する教育支援ツールです。

## 使い方

### 1. 環境準備
```bash
pip3 install gradio whisper torch mecab-python3 unidic-lite
```

### 2. システム起動
```bash
python3 app_mecab_enhanced.py
```

### 3. ブラウザでアクセス
```
http://localhost:7869
```

### 4. 操作方法
1. マイクボタンをクリックして英語を録音
2. 「MeCab強化解析開始」をクリック  
3. 結果確認：MeCab変換でカタカナ表示

## 使用例

**発音**: 「I want to go」を「アイワナゴー」と発音
**結果**: "アイワナゴー" （実際の音をカタカナ化）

## トラブルシューティング

### MeCabエラーが出る場合
```bash
brew install mecab mecab-ipadic  # macOS
```

### 音声認識されない場合
- マイクの許可設定を確認
- 雑音の少ない環境で録音
