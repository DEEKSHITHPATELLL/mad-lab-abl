import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as Speech from 'expo-speech';

const API_BASE_URL = 'http://192.168.116.67:8000/api/v1';

// Language options with 5 Indian languages
const LANGUAGES = {
  'en': { name: 'English', flag: '🇺🇸', ttsCode: 'en' },
  'hi': { name: 'Hindi', flag: '🇮🇳', ttsCode: 'hi' },
  'kn': { name: 'Kannada', flag: '🇮🇳', ttsCode: 'kn' },
  'ta': { name: 'Tamil', flag: '🇮🇳', ttsCode: 'ta' },
  'te': { name: 'Telugu', flag: '🇮🇳', ttsCode: 'te' },
  'ml': { name: 'Malayalam', flag: '🇮🇳', ttsCode: 'ml' },
};

export default function App() {
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('hi');
  const [inputText, setInputText] = useState('Hello, how are you today?');
  const [translatedText, setTranslatedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        setConnected(true);
      }
    } catch (error) {
      setConnected(false);
    }
  };

  const translateText = async (textToTranslate = null) => {
    const text = textToTranslate || inputText;
    if (!text.trim()) {
      Alert.alert('Error', 'Please enter text to translate');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          source_language: sourceLanguage,
          target_language: targetLanguage,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setTranslatedText(data.translated_text);
      } else {
        throw new Error(data.detail || 'Translation failed');
      }
    } catch (error) {
      Alert.alert('Translation Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const swapLanguages = () => {
    const temp = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(temp);
    if (translatedText) {
      setInputText(translatedText);
      setTranslatedText(inputText);
    }
  };



  // Text-to-Speech Functions
  const speakText = async (text, language) => {
    try {
      if (isPlaying) {
        Speech.stop();
        setIsPlaying(false);
        return;
      }

      setIsPlaying(true);

      const options = {
        language: LANGUAGES[language]?.ttsCode || 'en',
        pitch: 1.0,
        rate: 0.8,
        onDone: () => setIsPlaying(false),
        onError: () => setIsPlaying(false),
      };

      Speech.speak(text, options);

    } catch (error) {
      console.error('Failed to speak text:', error);
      setIsPlaying(false);
      Alert.alert('Speech Error', 'Failed to play speech.');
    }
  };



  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />

      <ScrollView style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>🌍 Voice Translator</Text>
          <View style={styles.statusContainer}>
            <View style={[styles.statusDot, { backgroundColor: connected ? '#4CAF50' : '#F44336' }]} />
            <Text style={styles.statusText}>
              {connected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
        </View>

        <View style={styles.languageSection}>
          <View style={styles.languageRow}>
            <View style={styles.languageContainer}>
              <Text style={styles.label}>From</Text>
              <TouchableOpacity
                style={styles.picker}
                onPress={() => {
                  const languages = Object.keys(LANGUAGES);
                  const currentIndex = languages.indexOf(sourceLanguage);
                  const nextIndex = (currentIndex + 1) % languages.length;
                  setSourceLanguage(languages[nextIndex]);
                }}
              >
                <Text style={styles.pickerText}>
                  {LANGUAGES[sourceLanguage].flag} {LANGUAGES[sourceLanguage].name}
                </Text>
              </TouchableOpacity>
            </View>

            <TouchableOpacity style={styles.swapButton} onPress={swapLanguages}>
              <Text style={styles.swapText}>⇄</Text>
            </TouchableOpacity>

            <View style={styles.languageContainer}>
              <Text style={styles.label}>To</Text>
              <TouchableOpacity
                style={styles.picker}
                onPress={() => {
                  const languages = Object.keys(LANGUAGES);
                  const currentIndex = languages.indexOf(targetLanguage);
                  const nextIndex = (currentIndex + 1) % languages.length;
                  setTargetLanguage(languages[nextIndex]);
                }}
              >
                <Text style={styles.pickerText}>
                  {LANGUAGES[targetLanguage].flag} {LANGUAGES[targetLanguage].name}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        <View style={styles.inputSection}>
          <Text style={styles.label}>Type text to translate:</Text>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Enter text to translate..."
            multiline
          />
        </View>

        <TouchableOpacity
          style={[styles.translateButton, loading && styles.disabledButton]}
          onPress={() => translateText()}
          disabled={loading || !connected}
        >
          <Text style={styles.buttonText}>
            {loading ? 'Translating...' : 'Translate'}
          </Text>
        </TouchableOpacity>

        {translatedText ? (
          <View style={styles.resultSection}>
            <View style={styles.originalSection}>
              <View style={styles.textHeader}>
                <Text style={styles.label}>Original ({LANGUAGES[sourceLanguage].name}):</Text>
                <TouchableOpacity
                  style={styles.speakButton}
                  onPress={() => speakText(inputText, sourceLanguage)}
                >
                  <Text style={styles.speakButtonText}>
                    {isPlaying ? '⏸️' : '🔊'}
                  </Text>
                </TouchableOpacity>
              </View>
              <View style={styles.textBox}>
                <Text style={styles.resultText}>{inputText}</Text>
              </View>
            </View>

            <View style={styles.translationSection}>
              <View style={styles.textHeader}>
                <Text style={styles.label}>Translation ({LANGUAGES[targetLanguage].name}):</Text>
                <TouchableOpacity
                  style={styles.speakButton}
                  onPress={() => speakText(translatedText, targetLanguage)}
                >
                  <Text style={styles.speakButtonText}>
                    {isPlaying ? '⏸️' : '🔊'}
                  </Text>
                </TouchableOpacity>
              </View>
              <View style={styles.resultBox}>
                <Text style={styles.resultText}>{translatedText}</Text>
              </View>
            </View>
          </View>
        ) : null}

        <View style={styles.instructionsSection}>
          <Text style={styles.instructionsTitle}>🎯 Translation Features:</Text>
          <Text style={styles.instructionsText}>
            📝 Text Input & Translation{'\n'}
            🔊 Text-to-Speech Playback{'\n'}
            🇮🇳 5 Indian Languages Support{'\n'}
            🌍 Real-time AI Translation{'\n'}
            📱 Native Mobile Experience{'\n'}
            ⚡ Powered by Google Gemini AI
          </Text>
          <Text style={styles.languageList}>
            Supported Languages: English, Hindi, Kannada, Tamil, Telugu, Malayalam
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#666',
  },
  languageSection: {
    marginBottom: 20,
  },
  languageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  languageContainer: {
    flex: 1,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  picker: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    minHeight: 48,
    justifyContent: 'center',
  },
  pickerText: {
    fontSize: 16,
    color: '#333',
  },
  swapButton: {
    marginHorizontal: 16,
    padding: 12,
    borderRadius: 8,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  swapText: {
    fontSize: 20,
    color: '#007AFF',
  },
  inputSection: {
    marginBottom: 20,
  },
  textInput: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  translateButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  resultSection: {
    marginBottom: 20,
  },
  originalSection: {
    marginBottom: 15,
  },
  translationSection: {
    marginBottom: 10,
  },
  textHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  textBox: {
    backgroundColor: '#f8f9fa',
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
  },
  resultBox: {
    backgroundColor: '#e8f5e8',
    borderLeftWidth: 4,
    borderLeftColor: '#4CAF50',
    borderRadius: 8,
    padding: 16,
  },
  resultText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  speakButton: {
    backgroundColor: '#FF9500',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  speakButtonText: {
    fontSize: 18,
  },
  instructionsSection: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 40,
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  instructionsText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  languageList: {
    fontSize: 12,
    color: '#999',
    marginTop: 10,
    fontStyle: 'italic',
    textAlign: 'center',
  },
});
