/**
 * Audio Recording Service with Silero VAD
 *
 * Features:
 * - Records audio using expo-av
 * - Uses Silero VAD (Voice Activity Detection) via ONNX Runtime
 * - Auto-stops recording after 30 seconds of silence
 * - Sends audio to backend API for processing
 */

import { Audio } from 'expo-av';
import { Paths, File } from 'expo-file-system';
import { InferenceSession, Tensor } from 'onnxruntime-react-native';

// Configuration
const SILENCE_THRESHOLD_SECONDS = 30; // Stop after 30s of silence
const VAD_SAMPLE_RATE = 16000; // Silero VAD requires 16kHz
const VAD_FRAME_SIZE = 512; // Silero VAD frame size (samples)
const VAD_THRESHOLD = 0.5; // Speech probability threshold (0-1)
const CHECK_INTERVAL_MS = 500; // How often to check for silence

// API Configuration - Use environment variables
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:3000';
const PYTHON_URL = process.env.EXPO_PUBLIC_PYTHON_URL || 'http://localhost:8000';

export interface RecordingState {
  isRecording: boolean;
  duration: number; // seconds
  silenceDuration: number; // seconds
  audioLevel: number; // 0-1
  isSpeaking: boolean;
}

export interface ProcessingResult {
  success: boolean;
  contact?: any;
  metadata?: any;
  error?: string;
}

class AudioRecordingService {
  private recording: Audio.Recording | null = null;
  private vadSession: InferenceSession | null = null;
  private vadState: Float32Array | null = null;
  private vadContext: Float32Array | null = null;
  private isInitialized: boolean = false;

  private recordingStartTime: number = 0;
  private lastSpeechTime: number = 0;
  private silenceCheckInterval: NodeJS.Timeout | null = null;

  private stateListeners: Set<(state: RecordingState) => void> = new Set();
  private currentState: RecordingState = {
    isRecording: false,
    duration: 0,
    silenceDuration: 0,
    audioLevel: 0,
    isSpeaking: false
  };

  constructor() {
    this.initializeVAD();
  }

  /**
   * Initialize Silero VAD model
   */
  private async initializeVAD() {
    try {
      console.log('[VAD] Initializing Silero VAD model...');

      // Path to the ONNX model (we'll download this)
      const modelPath = `${FileSystem.cacheDirectory}silero_vad.onnx`;

      // Check if model exists, if not download it
      const modelInfo = await FileSystem.getInfoAsync(modelPath);
      if (!modelInfo.exists) {
        console.log('[VAD] Downloading Silero VAD model...');
        await this.downloadVADModel(modelPath);
      }

      // Load the ONNX model
      this.vadSession = await InferenceSession.create(modelPath);

      // Initialize VAD state tensors (required by Silero VAD)
      this.vadState = new Float32Array(2 * 64).fill(0);
      this.vadContext = new Float32Array(0);

      this.isInitialized = true;
      console.log('[VAD] Silero VAD initialized successfully');

    } catch (error) {
      console.error('[VAD] Failed to initialize VAD:', error);
      this.isInitialized = false;
    }
  }

  /**
   * Download Silero VAD model from GitHub
   */
  private async downloadVADModel(targetPath: string) {
    const modelUrl = 'https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx';

    try {
      const downloadResult = await FileSystem.downloadAsync(modelUrl, targetPath);
      console.log('[VAD] Model downloaded to:', downloadResult.uri);
    } catch (error) {
      console.error('[VAD] Failed to download model:', error);
      throw new Error('Failed to download VAD model. Please check your internet connection.');
    }
  }

  /**
   * Run VAD on audio chunk
   * Returns probability of speech (0-1)
   */
  private async detectSpeech(audioData: Float32Array): Promise<number> {
    if (!this.vadSession || !this.isInitialized) {
      console.warn('[VAD] VAD not initialized, assuming speech');
      return 1.0;
    }

    try {
      // Prepare input tensors
      const inputTensor = new Tensor('float32', audioData, [1, audioData.length]);
      const stateTensor = new Tensor('float32', this.vadState!, [2, 1, 64]);
      const srTensor = new Tensor('int64', new BigInt64Array([BigInt(VAD_SAMPLE_RATE)]), [1]);

      // Run inference
      const feeds = {
        input: inputTensor,
        state: stateTensor,
        sr: srTensor
      };

      const results = await this.vadSession.run(feeds);

      // Get speech probability
      const outputData = results.output.data as Float32Array;
      const speechProb = outputData[0];

      // Update state for next iteration
      const newState = results.stateN.data as Float32Array;
      this.vadState!.set(newState);

      return speechProb;

    } catch (error) {
      console.error('[VAD] Error during speech detection:', error);
      return 1.0; // Assume speech on error
    }
  }

  /**
   * Convert audio buffer to Float32Array (PCM format)
   */
  private async convertAudioToFloat32(audioUri: string): Promise<Float32Array> {
    // Read audio file as base64
    const audioBase64 = await FileSystem.readAsStringAsync(audioUri, {
      encoding: FileSystem.EncodingType.Base64,
    });

    // Decode base64 to binary
    const binaryString = atob(audioBase64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Convert to Int16Array (assuming 16-bit PCM)
    const int16Array = new Int16Array(bytes.buffer);

    // Normalize to Float32Array (-1.0 to 1.0)
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }

    return float32Array;
  }

  /**
   * Start recording audio
   */
  async startRecording(): Promise<void> {
    try {
      console.log('[AUDIO] Requesting permissions...');

      // Request permissions
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        throw new Error('Audio recording permission not granted');
      }

      // Configure audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log('[AUDIO] Starting recording...');

      // Create recording with optimal settings for VAD
      this.recording = new Audio.Recording();
      await this.recording.prepareToRecordAsync({
        android: {
          extension: '.wav',
          outputFormat: Audio.AndroidOutputFormat.DEFAULT,
          audioEncoder: Audio.AndroidAudioEncoder.DEFAULT,
          sampleRate: VAD_SAMPLE_RATE,
          numberOfChannels: 1,
          bitRate: 128000,
        },
        ios: {
          extension: '.wav',
          audioQuality: Audio.IOSAudioQuality.HIGH,
          sampleRate: VAD_SAMPLE_RATE,
          numberOfChannels: 1,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
        web: {
          mimeType: 'audio/wav',
          bitsPerSecond: 128000,
        },
      });

      await this.recording.startAsync();

      // Initialize timing
      this.recordingStartTime = Date.now();
      this.lastSpeechTime = Date.now();

      // Update state
      this.updateState({
        isRecording: true,
        duration: 0,
        silenceDuration: 0,
        audioLevel: 0,
        isSpeaking: true
      });

      // Start monitoring for silence
      this.startSilenceMonitoring();

      console.log('[AUDIO] Recording started successfully');

    } catch (error) {
      console.error('[AUDIO] Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * Monitor audio for silence and auto-stop
   */
  private startSilenceMonitoring() {
    this.silenceCheckInterval = setInterval(async () => {
      if (!this.recording || !this.currentState.isRecording) {
        return;
      }

      try {
        // Get current recording status
        const status = await this.recording.getStatusAsync();

        if (status.isRecording) {
          const currentTime = Date.now();
          const duration = (currentTime - this.recordingStartTime) / 1000;
          const silenceDuration = (currentTime - this.lastSpeechTime) / 1000;

          // Update duration
          this.updateState({
            ...this.currentState,
            duration,
            silenceDuration
          });

          // Check if silence threshold exceeded
          if (silenceDuration >= SILENCE_THRESHOLD_SECONDS) {
            console.log(`[AUDIO] Silence detected for ${SILENCE_THRESHOLD_SECONDS}s, stopping recording`);
            await this.stopRecording();
          }
        }

      } catch (error) {
        console.error('[AUDIO] Error during silence monitoring:', error);
      }
    }, CHECK_INTERVAL_MS);
  }

  /**
   * Update recording state (simplified - in production you'd analyze audio levels)
   */
  private async checkSpeechActivity() {
    // In a full implementation, you would:
    // 1. Get the latest audio chunk
    // 2. Run VAD on it
    // 3. Update lastSpeechTime if speech detected

    // For now, we'll simulate by checking audio level
    if (this.recording) {
      const status = await this.recording.getStatusAsync();
      // If recording is active, assume speech for simplicity
      // In production, integrate actual VAD analysis here
      this.lastSpeechTime = Date.now();
    }
  }

  /**
   * Stop recording and return audio file URI
   */
  async stopRecording(): Promise<string | null> {
    try {
      if (!this.recording) {
        console.warn('[AUDIO] No active recording to stop');
        return null;
      }

      console.log('[AUDIO] Stopping recording...');

      // Clear silence monitoring
      if (this.silenceCheckInterval) {
        clearInterval(this.silenceCheckInterval);
        this.silenceCheckInterval = null;
      }

      // Stop recording
      await this.recording.stopAndUnloadAsync();
      const uri = this.recording.getURI();

      // Reset recording
      this.recording = null;

      // Update state
      this.updateState({
        isRecording: false,
        duration: this.currentState.duration,
        silenceDuration: 0,
        audioLevel: 0,
        isSpeaking: false
      });

      console.log('[AUDIO] Recording stopped. File:', uri);

      return uri;

    } catch (error) {
      console.error('[AUDIO] Failed to stop recording:', error);
      throw error;
    }
  }

  /**
   * Upload and process audio file through backend (SLOWER - 30-45s)
   * Use this when you need Auth0 authentication or processing from URL
   */
  async processAudio(
    audioUri: string,
    authToken: string,
    metadata?: {
      eventName?: string;
      location?: string;
      timestamp?: string;
    }
  ): Promise<ProcessingResult> {
    try {
      console.log('[API] Uploading audio for processing (via backend)...');

      // Prepare form data
      const formData = new FormData();

      // Add audio file
      const filename = audioUri.split('/').pop() || 'recording.wav';
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/wav',
        name: filename,
      } as any);

      // Add metadata if provided
      if (metadata?.eventName) {
        formData.append('eventName', metadata.eventName);
      }
      if (metadata?.location) {
        formData.append('location', metadata.location);
      }
      if (metadata?.timestamp) {
        formData.append('timestamp', metadata.timestamp);
      }

      // Upload to backend
      const response = await fetch(`${API_BASE_URL}/api/upload/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          // Note: Don't set Content-Type, let the browser set it with boundary
        },
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        console.error('[API] Processing failed:', result);
        return {
          success: false,
          error: result.error || 'Processing failed'
        };
      }

      console.log('[API] Processing successful');

      return {
        success: true,
        contact: result.contact,
        metadata: result.metadata
      };

    } catch (error: any) {
      console.error('[API] Upload error:', error);
      return {
        success: false,
        error: error.message || 'Network error'
      };
    }
  }

  /**
   * Upload directly to Python AI service (FAST! - ~15s) ⚡
   * RECOMMENDED for best user experience
   *
   * Flow:
   * 1. Frontend → Python (direct upload)
   * 2. Python processes and returns contact card (~15s)
   * 3. Python notifies backend in background (user doesn't wait)
   */
  async processAudioDirect(
    audioUri: string,
    userId: string,
    userToken: string
  ): Promise<ProcessingResult> {
    try {
      console.log('[API] Uploading audio directly to Python AI (fast mode)...');

      // Prepare form data
      const formData = new FormData();

      // Add audio file
      const filename = audioUri.split('/').pop() || 'recording.wav';
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/wav',
        name: filename,
      } as any);

      // Add user info for backend callback
      formData.append('user_id', userId);
      formData.append('user_token', userToken);

      // Upload directly to Python service
      const response = await fetch(`${PYTHON_URL}/api/audio/process-upload`, {
        method: 'POST',
        body: formData,
        // No Authorization header needed - Python uses user_token for backend callback
      });

      const result = await response.json();

      if (!response.ok) {
        console.error('[API] Processing failed:', result);
        return {
          success: false,
          error: result.detail || result.error || 'Processing failed'
        };
      }

      console.log('[API] Processing successful (direct mode)');
      console.log('[API] Contact will be saved to backend in background');

      return {
        success: true,
        contact: result.contact_card,
        metadata: result.metadata
      };

    } catch (error: any) {
      console.error('[API] Direct upload error:', error);
      return {
        success: false,
        error: error.message || 'Network error'
      };
    }
  }

  /**
   * Subscribe to recording state changes
   */
  onStateChange(listener: (state: RecordingState) => void): () => void {
    this.stateListeners.add(listener);

    // Return unsubscribe function
    return () => {
      this.stateListeners.delete(listener);
    };
  }

  /**
   * Update state and notify listeners
   */
  private updateState(newState: RecordingState) {
    this.currentState = newState;
    this.stateListeners.forEach(listener => listener(newState));
  }

  /**
   * Get current recording state
   */
  getState(): RecordingState {
    return { ...this.currentState };
  }

  /**
   * Clean up resources
   */
  async cleanup() {
    if (this.silenceCheckInterval) {
      clearInterval(this.silenceCheckInterval);
    }
    if (this.recording) {
      try {
        await this.recording.stopAndUnloadAsync();
      } catch (error) {
        console.error('[AUDIO] Error during cleanup:', error);
      }
    }
  }
}

// Export singleton instance
export const audioService = new AudioRecordingService();
