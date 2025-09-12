export const convertToKatakana = (text: string): string => {
  const phoneticMap: { [key: string]: string } = {
    'a': 'ア', 'i': 'イ', 'u': 'ウ', 'e': 'エ', 'o': 'オ',
    'ka': 'カ', 'ki': 'キ', 'ku': 'ク', 'ke': 'ケ', 'ko': 'コ',
    'ga': 'ガ', 'gi': 'ギ', 'gu': 'グ', 'ge': 'ゲ', 'go': 'ゴ',
    'sa': 'サ', 'si': 'シ', 'su': 'ス', 'se': 'セ', 'so': 'ソ',
    'za': 'ザ', 'zi': 'ジ', 'zu': 'ズ', 'ze': 'ゼ', 'zo': 'ゾ',
    'ta': 'タ', 'ti': 'チ', 'tu': 'ツ', 'te': 'テ', 'to': 'ト',
    'da': 'ダ', 'di': 'ヂ', 'du': 'ヅ', 'de': 'デ', 'do': 'ド',
    'na': 'ナ', 'ni': 'ニ', 'nu': 'ヌ', 'ne': 'ネ', 'no': 'ノ',
    'ha': 'ハ', 'hi': 'ヒ', 'hu': 'フ', 'he': 'ヘ', 'ho': 'ホ',
    'ba': 'バ', 'bi': 'ビ', 'bu': 'ブ', 'be': 'ベ', 'bo': 'ボ',
    'pa': 'パ', 'pi': 'ピ', 'pu': 'プ', 'pe': 'ペ', 'po': 'ポ',
    'ma': 'マ', 'mi': 'ミ', 'mu': 'ム', 'me': 'メ', 'mo': 'モ',
    'ya': 'ヤ', 'yu': 'ユ', 'yo': 'ヨ',
    'ra': 'ラ', 'ri': 'リ', 'ru': 'ル', 're': 'レ', 'ro': 'ロ',
    'wa': 'ワ', 'wo': 'ヲ', 'n': 'ン',
    
    'sh': 'シ', 'ch': 'チ', 'th': 'ス', 'ph': 'フ',
    'ng': 'ング', 'nk': 'ンク', 'nt': 'ント',
    
    'hello': 'ヘロー', 'world': 'ワールド', 'good': 'グッド', 
    'morning': 'モーニング', 'thank': 'サンク', 'you': 'ユー',
    'please': 'プリーズ', 'sorry': 'ソーリー', 'excuse': 'エクスキューズ',
    'me': 'ミー', 'water': 'ウォーター', 'coffee': 'コーヒー',
    'apple': 'アップル', 'orange': 'オレンジ', 'banana': 'バナナ',
    
    'f': 'フ', 'v': 'ブ', 'th': 'ス', 'l': 'ル', 'r': 'ル',
    'b': 'ブ', 'p': 'プ', 'd': 'ド', 't': 'ト', 'g': 'グ',
    'k': 'ク', 'j': 'ジ', 's': 'ス', 'z': 'ズ', 'h': 'ハ',
    'm': 'ム', 'n': 'ン', 'w': 'ウ', 'y': 'ヤ'
  };

  if (!text || text.trim() === '') {
    return '';
  }

  let result = text.toLowerCase();
  
  Object.keys(phoneticMap)
    .sort((a, b) => b.length - a.length)
    .forEach(key => {
      const regex = new RegExp(key, 'gi');
      result = result.replace(regex, phoneticMap[key]);
    });

  result = result.replace(/[^ァ-ヶ]/g, '？');
  
  return result || '？';
};