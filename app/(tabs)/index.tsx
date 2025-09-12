import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, View, TouchableOpacity, Alert, Platform } from 'react-native';
import { Audio } from 'expo-av';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

// Web Speech APIのタイプ定義（Webのみ）
declare global {
  interface Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
  }
}

export default function HomeScreen() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordingUri, setRecordingUri] = useState<string | null>(null);
  const [savedRecordings, setSavedRecordings] = useState<string[]>([]);
  const [transcription, setTranscription] = useState('');
  const [rawAlternatives, setRawAlternatives] = useState<string[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [whisperResult, setWhisperResult] = useState<{raw: string, katakana: string} | null>(null);
  const [isProcessingWhisper, setIsProcessingWhisper] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (Platform.OS === 'web') {
      // Webプラットフォーム用の確認
      const supported = typeof window !== 'undefined' && 
        ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window);
      setSpeechSupported(supported);
      
      if (supported) {
        setupWebSpeechRecognition();
      }
    } else {
      // iOS/Androidでは現在のExpo Goでは制限があるため、Development Buildが必要
      setSpeechSupported(false);
      console.log('iOS/Android speech recognition requires Development Build');
    }
  }, []);

  const selectRawCandidate = (alternatives: string[]): string => {
    if (alternatives.length === 0) return '';
    if (alternatives.length === 1) return alternatives[0];

    // より「生」の発音に近い候補を選択するヒューリスティック
    const scored = alternatives.map((alt, index) => {
      let score = 0;
      
      // 後の候補ほど信頼度が低い（＝補正が少ない可能性）
      score += (alternatives.length - index) * 10;
      
      // 短い単語は発音が不完全な可能性
      if (alt.length < alternatives[0].length) score += 20;
      
      // 一般的でない単語・音の組み合わせを優先
      const commonWords = ['hello', 'thank', 'you', 'water', 'good', 'morning'];
      const isCommon = commonWords.some(word => 
        alt.toLowerCase().includes(word.toLowerCase())
      );
      if (!isCommon) score += 15;
      
      // より多くの子音クラスターがある（発音の特徴を保持）
      const consonantClusters = alt.match(/[bcdfghjklmnpqrstvwxyz]{2,}/gi) || [];
      score += consonantClusters.length * 5;
      
      return { alt, score, index };
    });
    
    // 最高スコアの候補を選択
    scored.sort((a, b) => b.score - a.score);
    console.log('Candidate scores:', scored);
    
    return scored[0].alt;
  };

  const setupWebSpeechRecognition = () => {
    const SpeechRecognitionAPI = window.webkitSpeechRecognition || window.SpeechRecognition;
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    
    // 生の発音により近づける設定
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en'; // より汎用的な設定
    recognition.maxAlternatives = 5; // 複数の候補を取得
    recognition.serviceURI = ''; // デフォルトサービスを使用

    recognition.onstart = () => {
      setIsListening(true);
      console.log('Web speech recognition started');
    };

    recognition.onend = () => {
      setIsListening(false);
      console.log('Web speech recognition ended');
    };

    recognition.onresult = (event: any) => {
      if (event.results.length > 0) {
        const lastResult = event.results[event.results.length - 1];
        
        // 全ての代替候補を取得
        const alternatives: string[] = [];
        for (let i = 0; i < lastResult.length && i < 5; i++) {
          if (lastResult[i]) {
            alternatives.push(lastResult[i].transcript);
          }
        }
        
        console.log('All alternatives:', alternatives);
        setRawAlternatives(alternatives);
        
        // より「生」に近い候補を選択するアルゴリズム
        const selectedTranscript = selectRawCandidate(alternatives);
        console.log('Selected raw transcript:', selectedTranscript);
        
        const katakanaResult = '？？？（Web Speech API結果は表示されません）？？？';
        setTranscription(katakanaResult);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Web speech recognition error:', event.error);
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  };

  const startRecording = async () => {
    try {
      console.log('Requesting permissions..');
      await Audio.requestPermissionsAsync();

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('Starting recording..');
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
      setTranscription('');
      setRawAlternatives([]);
      setRecordingUri(null);

      // 音声認識開始（Webのみ）
      if (speechSupported && Platform.OS === 'web' && recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (error) {
          console.error('Error starting web recognition:', error);
        }
      }

      console.log('Recording started');

      timerRef.current = setInterval(() => {
        setRecordingDuration(prev => {
          if (prev >= 30) {
            stopRecording();
            return 30;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err) {
      console.error('Failed to start recording', err);
      Alert.alert('録音エラー', '録音を開始できませんでした。権限を確認してください。');
    }
  };

  const stopRecording = async () => {
    console.log('Stopping recording..');
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    // 音声認識停止（Webのみ）
    if (speechSupported && Platform.OS === 'web' && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping web recognition:', error);
      }
    }

    if (!recording) {
      return;
    }

    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecordingUri(uri);
      console.log('Recording stopped and stored at', uri);
      
      // 音声認識が利用できない、または何も認識されなかった場合
      if (!speechSupported) {
        if (Platform.OS === 'web') {
          setTranscription('？？？（ブラウザが音声認識をサポートしていません）？？？');
        } else {
          setTranscription('？？？（iOS/Androidでは Development Build が必要です）？？？');
        }
      } else if (!transcription) {
        setTranscription('？？？（音声が認識されませんでした）？？？');
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
    }

    setRecording(null);
    setIsRecording(false);
    setRecordingDuration(0);
  };

  const playRecording = async () => {
    if (!recordingUri) {
      Alert.alert('エラー', '再生する録音がありません');
      return;
    }

    try {
      const { sound } = await Audio.Sound.createAsync({ uri: recordingUri });
      await sound.playAsync();
    } catch (error) {
      console.error('Error playing recording:', error);
      Alert.alert('エラー', '録音の再生に失敗しました');
    }
  };


  const processWithWhisper = async () => {
    console.log('解析ボタンが押されました');
    console.log('recordingUri:', recordingUri);
    
    if (!recordingUri) {
      console.log('録音URIがありません');
      Alert.alert('エラー', '解析する録音がありません');
      return;
    }

    setIsProcessingWhisper(true);
    setWhisperResult(null);
    
    try {
      // Hugging Face Spaces APIエンドポイント
      const API_URL = 'https://naonta44-whisper-pronunciation-api.hf.space/api/predict';
      
      // 音声ファイルを取得
      const response = await fetch(recordingUri);
      const audioBlob = await response.blob();
      
      // FormDataを作成
      const formData = new FormData();
      formData.append('data', JSON.stringify([null, audioBlob]));
      
      console.log('Hugging Face Spaces APIに送信中...');
      
      // APIリクエスト
      const apiResponse = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!apiResponse.ok) {
        throw new Error(`API Error: ${apiResponse.status} ${apiResponse.statusText}`);
      }
      
      const result = await apiResponse.json();
      console.log('HF Spaces API結果:', result);
      
      // Gradio APIの結果をパース
      if (result && result.data && result.data[0]) {
        const resultText = result.data[0];
        
        // 結果から英語表記とカタカナ表記を抽出
        const englishMatch = resultText.match(/\*\*英語表記:\*\* (.+)/);
        const katakanaMatch = resultText.match(/\*\*カタカナ表記:\*\* (.+)/);
        
        const englishText = englishMatch ? englishMatch[1].trim() : '認識できませんでした';
        const katakanaText = katakanaMatch ? katakanaMatch[1].trim() : '？？？';
        
        setWhisperResult({
          raw: englishText,
          katakana: katakanaText
        });
      } else {
        throw new Error('APIから予期しない結果が返されました');
      }
      
    } catch (error) {
      console.error('Hugging Face Spaces API エラー:', error);
      
      // フォールバック: ローカルのモック結果
      console.log('フォールバック: モック結果を使用');
      const mockResults = [
        { raw: "hello world", katakana: "ハロー ワールド" },
        { raw: "thank you very much", katakana: "サンク ユー ベリー マチ" },
        { raw: "good morning", katakana: "グッド モーニング" }
      ];
      
      const randomResult = mockResults[Math.floor(Math.random() * mockResults.length)];
      setWhisperResult({
        raw: randomResult.raw,
        katakana: randomResult.katakana
      });
      
      Alert.alert('注意', 'API接続に失敗しました。デモ結果を表示しています。');
    } finally {
      setIsProcessingWhisper(false);
    }
  };

  const createDevelopmentBuild = () => {
    Alert.alert(
      'Development Build作成方法', 
      'iOSで音声認識を使用するには Development Build が必要です。\n\n手順:\n1. npx expo install expo-dev-client\n2. npx expo run:ios\n3. 実機またはシミュレーターで実行',
      [{ text: 'OK' }]
    );
  };

  return (
    <ThemedView style={styles.container}>
      <ThemedText type="title" style={styles.title}>
        英語発音文字起こし
      </ThemedText>
      
      
      <View style={styles.recordingContainer}>
        <TouchableOpacity
          style={[
            styles.recordButton,
            { backgroundColor: isRecording ? '#ff4444' : '#4CAF50' }
          ]}
          onPress={isRecording ? stopRecording : startRecording}
        >
          <ThemedText style={styles.recordButtonText}>
            {isRecording ? '停止' : '録音開始'}
          </ThemedText>
        </TouchableOpacity>
        
        {isRecording && (
          <View style={styles.statusContainer}>
            <ThemedText style={styles.timer}>
              {recordingDuration}秒 / 30秒 🎤
            </ThemedText>
            {speechSupported && isListening && (
              <ThemedText style={styles.listeningStatus}>
                音声認識中... 🔊
              </ThemedText>
            )}
          </View>
        )}
      </View>



      {recordingUri && (
        <View style={styles.actionButtonsContainer}>
          <TouchableOpacity style={styles.playButton} onPress={playRecording}>
            <ThemedText style={styles.playButtonText}>
              録音を再生 🔊
            </ThemedText>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.whisperButton, isProcessingWhisper && styles.processingButton]} 
            onPress={processWithWhisper}
            disabled={isProcessingWhisper}
          >
            <ThemedText style={styles.whisperButtonText}>
              {isProcessingWhisper ? '解析中... ⏳' : '解析 🎯'}
            </ThemedText>
          </TouchableOpacity>
        </View>
      )}

      {whisperResult && (
        <View style={styles.comparisonContainer}>
          <ThemedText style={styles.comparisonTitle}>
            🎤 解析結果
          </ThemedText>
          <View style={styles.resultItem}>
            <ThemedText style={styles.resultLabel}>カタカナ表記:</ThemedText>
            <ThemedText style={styles.resultText}>
              {whisperResult.katakana}
            </ThemedText>
          </View>
          <View style={styles.resultItem}>
            <ThemedText style={styles.resultLabel}>英語表記:</ThemedText>
            <ThemedText style={styles.resultText}>
              "{whisperResult.raw}"
            </ThemedText>
          </View>
          <TouchableOpacity 
            style={styles.clearComparisonButton}
            onPress={() => setWhisperResult(null)}
          >
            <ThemedText style={styles.clearComparisonButtonText}>結果をクリア</ThemedText>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.supportInfo}>
        <ThemedText style={styles.supportText}>
          音声認識: {speechSupported ? '✅ 利用可能' : '❌ 利用不可'}
        </ThemedText>
        <ThemedText style={styles.supportText}>
          プラットフォーム: {Platform.OS}
        </ThemedText>
        {!speechSupported && Platform.OS !== 'web' && (
          <TouchableOpacity style={styles.helpButton} onPress={createDevelopmentBuild}>
            <ThemedText style={styles.helpButtonText}>
              iOS対応方法を見る
            </ThemedText>
          </TouchableOpacity>
        )}
      </View>

      <ThemedText style={styles.instruction}>
        録音ボタンを押して英語を話してください。
        {speechSupported ? 
          '実際の発音がそのままカタカナで表示されます（補正なし）。' :
          Platform.OS === 'web' ? 
            'ブラウザが音声認識をサポートしていません。' :
            'iOSでの音声認識には Development Build が必要です。'
        }
        {'\n\n'}
        {speechSupported && '※ 正確でない発音も忠実に再現されます。'}
      </ThemedText>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    marginBottom: 40,
    textAlign: 'center',
  },
  recordingContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  recordButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  recordButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  statusContainer: {
    alignItems: 'center',
    marginTop: 10,
  },
  timer: {
    fontSize: 16,
    marginTop: 10,
    color: '#333333',
    fontWeight: '500',
  },
  listeningStatus: {
    fontSize: 14,
    color: '#4CAF50',
    marginTop: 5,
    fontWeight: '500',
  },
  actionButtonsContainer: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  playButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    flex: 1,
  },
  playButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  whisperButton: {
    backgroundColor: '#FF6B35',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    flex: 1,
  },
  whisperButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  processingButton: {
    backgroundColor: '#999999',
  },
  supportInfo: {
    marginBottom: 20,
    alignItems: 'center',
  },
  supportText: {
    fontSize: 12,
    color: '#888888',
    marginBottom: 2,
  },
  helpButton: {
    backgroundColor: '#FF9800',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
    marginTop: 8,
  },
  helpButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  instruction: {
    textAlign: 'center',
    fontSize: 14,
    color: '#666666',
    fontWeight: '400',
  },
  comparisonContainer: {
    width: '100%',
    marginBottom: 20,
    padding: 16,
    borderWidth: 2,
    borderColor: '#4CAF50',
    borderRadius: 12,
    backgroundColor: '#f0f8f0',
  },
  comparisonTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
    color: '#2E7D32',
  },
  comparisonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    gap: 10,
  },
  comparisonItem: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  comparisonLabel: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 6,
    fontWeight: '500',
  },
  comparisonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000000',
    minHeight: 20,
  },
  whisperRawContainer: {
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#fff3e0',
    borderWidth: 1,
    borderColor: '#ffb74d',
    marginBottom: 12,
  },
  whisperRawLabel: {
    fontSize: 12,
    color: '#e65100',
    marginBottom: 4,
    fontWeight: '500',
  },
  whisperRawText: {
    fontSize: 14,
    color: '#bf360c',
    fontFamily: 'monospace',
    fontStyle: 'italic',
  },
  clearComparisonButton: {
    backgroundColor: '#ff5722',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
    alignSelf: 'center',
  },
  clearComparisonButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  resultItem: {
    marginBottom: 15,
  },
  resultLabel: {
    fontSize: 14,
    color: '#333333',
    fontWeight: '600',
    marginBottom: 5,
  },
  resultText: {
    fontSize: 18,
    color: '#000000',
    fontWeight: 'bold',
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 8,
  },
});