import React, { useState, useRef, useEffect } from 'react';
import { StyleSheet, View, TouchableOpacity, Alert, Platform } from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function HomeScreen() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordingUri, setRecordingUri] = useState<string | null>(null);
  const [transcription, setTranscription] = useState('');
  const [whisperResult, setWhisperResult] = useState<{raw: string, katakana: string} | null>(null);
  const [isProcessingWhisper, setIsProcessingWhisper] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // 音声録音の権限を事前に確認
    checkAudioPermissions();
  }, []);

  const checkAudioPermissions = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('権限が必要です', 'マイクの使用許可が必要です。設定から許可してください。');
      }
    } catch (error) {
      console.error('Permission check error:', error);
    }
  };

  const startRecording = async () => {
    try {
      console.log('録音を開始します...');
      
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('エラー', 'マイクの使用許可が必要です');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
      setTranscription('');
      setRecordingUri(null);
      setWhisperResult(null);

      console.log('録音開始');

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
      console.error('録音開始に失敗しました', err);
      Alert.alert('録音エラー', '録音を開始できませんでした。権限を確認してください。');
    }
  };

  const stopRecording = async () => {
    console.log('録音を停止します...');
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    if (!recording) {
      return;
    }

    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecordingUri(uri);
      console.log('録音完了:', uri);
      setTranscription('録音が完了しました。解析ボタンを押してください。');
    } catch (error) {
      console.error('録音停止エラー:', error);
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
      console.error('再生エラー:', error);
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
      
      let audioBlob;
      
      if (Platform.OS === 'web') {
        // Web環境での処理
        const response = await fetch(recordingUri);
        audioBlob = await response.blob();
      } else {
        // React Native環境での処理
        const fileInfo = await FileSystem.getInfoAsync(recordingUri);
        if (!fileInfo.exists) {
          throw new Error('録音ファイルが見つかりません');
        }
        
        const base64 = await FileSystem.readAsStringAsync(recordingUri, {
          encoding: FileSystem.EncodingType.Base64,
        });
        
        // Base64をBlobに変換
        const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        audioBlob = new Blob([byteArray], { type: 'audio/m4a' });
      }
      
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

      {transcription && (
        <View style={styles.transcriptionContainer}>
          <ThemedText style={styles.transcriptionText}>
            {transcription}
          </ThemedText>
        </View>
      )}

      <ThemedText style={styles.instruction}>
        録音ボタンを押して英語を話してください。
        録音後に解析ボタンを押すと、実際の発音がカタカナで表示されます。
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
  transcriptionContainer: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    width: '100%',
  },
  transcriptionText: {
    fontSize: 14,
    color: '#333333',
    textAlign: 'center',
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