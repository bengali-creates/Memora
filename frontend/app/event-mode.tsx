/**
 * Event Mode - Audio Recording with Silero VAD
 *
 * Features:
 * - Record conversations at networking events
 * - Auto-stop after 30 seconds of silence
 * - Real-time recording stats (duration, silence, speech detection)
 * - Upload to backend for AI processing
 */

import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { Mic, MicOff, Upload, Activity } from 'lucide-react-native';
import { useTheme } from '@/constants/theme';
import { useAuth } from '@/services/authContext';
import { audioService, RecordingState } from '@/services/audioService';

export default function EventModeScreen() {
  const t = useTheme();
  const router = useRouter();
  const { getToken } = useAuth();

  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    duration: 0,
    silenceDuration: 0,
    audioLevel: 0,
    isSpeaking: false
  });
  const [audioUri, setAudioUri] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Subscribe to recording state changes
  useEffect(() => {
    const unsubscribe = audioService.onStateChange((state) => {
      setRecordingState(state);

      // Auto-process when recording stops due to silence
      if (!state.isRecording && audioUri) {
        handleProcess();
      }
    });

    return () => {
      unsubscribe();
      audioService.cleanup();
    };
  }, [audioUri]);

  /**
   * Format seconds to MM:SS
   */
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Start recording
   */
  const handleStartRecording = async () => {
    try {
      await audioService.startRecording();
      setAudioUri(null);
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to start recording');
    }
  };

  /**
   * Stop recording
   */
  const handleStopRecording = async () => {
    try {
      const uri = await audioService.stopRecording();
      setAudioUri(uri);

      if (uri) {
        Alert.alert(
          'Recording Complete',
          'Your conversation has been recorded. Process it now?',
          [
            {
              text: 'Later',
              style: 'cancel'
            },
            {
              text: 'Process Now',
              onPress: handleProcess
            }
          ]
        );
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to stop recording');
    }
  };

  /**
   * Process audio and extract contact
   */
  const handleProcess = async () => {
    if (!audioUri) {
      Alert.alert('Error', 'No audio file to process');
      return;
    }

    try {
      setIsProcessing(true);

      // Get auth token
      const token = await getToken();
      if (!token) {
        Alert.alert('Error', 'Please sign in to process audio');
        return;
      }

      // Process audio
      const result = await audioService.processAudio(audioUri, token, {
        eventName: 'Event Recording',
        timestamp: new Date().toISOString()
      });

      setIsProcessing(false);

      if (result.success && result.contact) {
        // Navigate to contact details
        Alert.alert(
          'Success!',
          `Contact extracted: ${result.contact.name || 'Unknown'}`,
          [
            {
              text: 'View Contact',
              onPress: () => router.push(`/contact?id=${result.contact.id}`)
            },
            {
              text: 'Record Another',
              onPress: () => setAudioUri(null)
            }
          ]
        );
      } else {
        Alert.alert('Processing Failed', result.error || 'Could not extract contact information');
      }

    } catch (error: any) {
      setIsProcessing(false);
      Alert.alert('Error', error.message || 'Failed to process audio');
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: t.bg }}>
      <StatusBar style="auto" />

      {/* Header */}
      <View style={{ padding: 24, paddingTop: 60 }}>
        <Text style={{
          fontSize: 28,
          fontFamily: 'Syne_700Bold',
          color: t.text,
          marginBottom: 8
        }}>
          Event Mode
        </Text>
        <Text style={{
          fontSize: 15,
          fontFamily: 'Poppins_400Regular',
          color: t.textMuted
        }}>
          Record conversations and extract contacts automatically
        </Text>
      </View>

      {/* Recording Stats */}
      <View style={{ flex: 1, padding: 24, alignItems: 'center', justifyContent: 'center' }}>

        {/* Central Recording Circle */}
        <View style={{
          width: 200,
          height: 200,
          borderRadius: 100,
          backgroundColor: recordingState.isRecording ? t.accent + '20' : t.bgSecondary,
          borderWidth: 4,
          borderColor: recordingState.isRecording ? t.accent : t.border,
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 40,
          ...(recordingState.isRecording && {
            shadowColor: t.accent,
            shadowOffset: { width: 0, height: 0 },
            shadowOpacity: 0.5,
            shadowRadius: 20,
            elevation: 10,
          })
        }}>
          {recordingState.isRecording ? (
            <Activity size={80} color={t.accent} />
          ) : (
            <Mic size={80} color={t.textMuted} />
          )}
        </View>

        {/* Duration Display */}
        <Text style={{
          fontSize: 48,
          fontFamily: 'Syne_700Bold',
          color: recordingState.isRecording ? t.accent : t.text,
          marginBottom: 12
        }}>
          {formatTime(recordingState.duration)}
        </Text>

        {/* Status Text */}
        <Text style={{
          fontSize: 16,
          fontFamily: 'Poppins_600SemiBold',
          color: t.textMuted,
          marginBottom: 24
        }}>
          {recordingState.isRecording ? (
            recordingState.isSpeaking ? 'Recording...' : 'Listening...'
          ) : audioUri ? (
            'Recording complete'
          ) : (
            'Ready to record'
          )}
        </Text>

        {/* Silence Warning */}
        {recordingState.isRecording && recordingState.silenceDuration > 10 && (
          <View style={{
            backgroundColor: t.orange + '20',
            borderRadius: 12,
            padding: 16,
            marginBottom: 24,
            borderWidth: 1,
            borderColor: t.orange + '40'
          }}>
            <Text style={{
              fontSize: 14,
              fontFamily: 'Poppins_600SemiBold',
              color: t.orange,
              textAlign: 'center'
            }}>
              ⚠️ Silence detected: {formatTime(recordingState.silenceDuration)}
            </Text>
            <Text style={{
              fontSize: 12,
              fontFamily: 'Poppins_400Regular',
              color: t.textMuted,
              textAlign: 'center',
              marginTop: 4
            }}>
              Recording will auto-stop after 30s of silence
            </Text>
          </View>
        )}

        {/* Stats Grid */}
        {recordingState.isRecording && (
          <View style={{
            flexDirection: 'row',
            gap: 16,
            marginBottom: 32
          }}>
            <View style={{
              backgroundColor: t.bgSecondary,
              borderRadius: 12,
              padding: 16,
              alignItems: 'center',
              minWidth: 100
            }}>
              <Text style={{
                fontSize: 12,
                fontFamily: 'Poppins_400Regular',
                color: t.textMuted,
                marginBottom: 4
              }}>
                Silence
              </Text>
              <Text style={{
                fontSize: 20,
                fontFamily: 'Syne_700Bold',
                color: recordingState.silenceDuration > 20 ? t.orange : t.text
              }}>
                {Math.floor(recordingState.silenceDuration)}s
              </Text>
            </View>

            <View style={{
              backgroundColor: t.bgSecondary,
              borderRadius: 12,
              padding: 16,
              alignItems: 'center',
              minWidth: 100
            }}>
              <Text style={{
                fontSize: 12,
                fontFamily: 'Poppins_400Regular',
                color: t.textMuted,
                marginBottom: 4
              }}>
                Speaking
              </Text>
              <View style={{
                width: 40,
                height: 40,
                borderRadius: 20,
                backgroundColor: recordingState.isSpeaking ? t.accent + '40' : t.border,
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <View style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: recordingState.isSpeaking ? t.accent : t.textMuted
                }} />
              </View>
            </View>
          </View>
        )}
      </View>

      {/* Control Buttons */}
      <View style={{ padding: 24, paddingBottom: 40 }}>

        {/* Main Action Button */}
        {!recordingState.isRecording && !audioUri && (
          <TouchableOpacity
            onPress={handleStartRecording}
            style={{
              backgroundColor: t.accent,
              borderRadius: 16,
              padding: 20,
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12,
              marginBottom: 12
            }}
          >
            <Mic size={24} color="#FFFFFF" />
            <Text style={{
              fontSize: 17,
              fontFamily: 'Poppins_600SemiBold',
              color: '#FFFFFF'
            }}>
              Start Recording
            </Text>
          </TouchableOpacity>
        )}

        {recordingState.isRecording && (
          <TouchableOpacity
            onPress={handleStopRecording}
            style={{
              backgroundColor: t.orange,
              borderRadius: 16,
              padding: 20,
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12,
              marginBottom: 12
            }}
          >
            <MicOff size={24} color="#FFFFFF" />
            <Text style={{
              fontSize: 17,
              fontFamily: 'Poppins_600SemiBold',
              color: '#FFFFFF'
            }}>
              Stop Recording
            </Text>
          </TouchableOpacity>
        )}

        {audioUri && !recordingState.isRecording && (
          <View style={{ gap: 12 }}>
            <TouchableOpacity
              onPress={handleProcess}
              disabled={isProcessing}
              style={{
                backgroundColor: t.accent,
                borderRadius: 16,
                padding: 20,
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 12,
                opacity: isProcessing ? 0.6 : 1
              }}
            >
              {isProcessing ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Upload size={24} color="#FFFFFF" />
              )}
              <Text style={{
                fontSize: 17,
                fontFamily: 'Poppins_600SemiBold',
                color: '#FFFFFF'
              }}>
                {isProcessing ? 'Processing...' : 'Process & Extract Contact'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleStartRecording}
              style={{
                backgroundColor: t.bgSecondary,
                borderRadius: 16,
                padding: 20,
                alignItems: 'center',
                borderWidth: 1,
                borderColor: t.border
              }}
            >
              <Text style={{
                fontSize: 15,
                fontFamily: 'Poppins_600SemiBold',
                color: t.text
              }}>
                Record Another
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Info Text */}
        <Text style={{
          fontSize: 13,
          fontFamily: 'Poppins_400Regular',
          color: t.textMuted,
          textAlign: 'center',
          marginTop: 16
        }}>
          💡 Recording will auto-stop after 30 seconds of silence
        </Text>
      </View>
    </View>
  );
}
