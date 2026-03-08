import { useTheme } from "@/constants/theme";
import { StatusBar } from "expo-status-bar";
import { Bot, Mic, MicOff, Phone, PhoneOff } from "lucide-react-native";
import { useState, useCallback, useRef } from "react";
import { Text, View, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from "react-native";
import { useConversation } from "@elevenlabs/react-native";
import { useAuth } from "@/services/authContext";
import Constants from "expo-constants";

// Configuration from environment variables
const ELEVENLABS_AGENT_ID = Constants.expoConfig?.extra?.elevenlabsAgentId ||
                            process.env.EXPO_PUBLIC_ELEVENLABS_AGENT_ID ||
                            '';

export interface TalkBotMessage {
  role: 'user' | 'agent';
  text: string;
  timestamp: number;
}

export default function TalkBotScreen() {
  const t = useTheme();
  const { user } = useAuth();

  const [messages, setMessages] = useState<TalkBotMessage[]>([]);
  const [isStarting, setIsStarting] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  // Use ElevenLabs conversation hook
  const conversation = useConversation({
    // Callback when user speaks (transcription received)
    onMessage: (props) => {
      console.log('[TALKBOT] Message:', props);

      const talkBotMessage: TalkBotMessage = {
        role: props.role === 'user' ? 'user' : 'agent',
        text: props.message,
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, talkBotMessage]);

      // Auto-scroll to bottom
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    },

    onConnect: () => {
      console.log('[TALKBOT] Connected to ElevenLabs');
    },

    onDisconnect: () => {
      console.log('[TALKBOT] Disconnected from ElevenLabs');
    },

    onError: (error: any) => {
      console.error('[TALKBOT] Error:', error);
      Alert.alert('Error', typeof error === 'string' ? error : (error?.message || 'An error occurred'));
    },

    onStatusChange: (status) => {
      console.log('[TALKBOT] Status change:', status);
    },

    onModeChange: (mode) => {
      console.log('[TALKBOT] Mode change:', mode.mode);
    },
  });

  const handleStartConversation = useCallback(async () => {
    if (!user?.email) {
      Alert.alert('Error', 'You must be logged in to use TalkBot');
      return;
    }

    if (!ELEVENLABS_AGENT_ID) {
      Alert.alert(
        'Configuration Error',
        'ElevenLabs Agent ID is not configured. Please set EXPO_PUBLIC_ELEVENLABS_AGENT_ID in your .env file.'
      );
      return;
    }

    try {
      setIsStarting(true);
      setMessages([]); // Clear previous messages

      const conversationId = `conv_${Date.now()}_${user.email}`;

      await conversation.startSession({
        agentId: ELEVENLABS_AGENT_ID,

        // Pass user info as dynamic variables (sent to webhook)
        dynamicVariables: {
          user_id: user.email,
          conversation_id: conversationId,
        },
      });

      console.log('[TALKBOT] Conversation started:', conversationId);
    } catch (error: any) {
      console.error('[TALKBOT] Failed to start:', error);
      Alert.alert('Error', error.message || 'Failed to start conversation');
    } finally {
      setIsStarting(false);
    }
  }, [user, conversation]);

  const handleStopConversation = useCallback(async () => {
    try {
      await conversation.endSession('user');
      console.log('[TALKBOT] Conversation ended');
    } catch (error: any) {
      console.error('[TALKBOT] Failed to stop:', error);
      Alert.alert('Error', error.message || 'Failed to stop conversation');
    }
  }, [conversation]);

  const handleToggleMute = useCallback(() => {
    try {
      const newMutedState = !isMuted;
      conversation.setMicMuted(newMutedState);
      setIsMuted(newMutedState);
      console.log('[TALKBOT] Mic muted:', newMutedState);
    } catch (error: any) {
      console.error('[TALKBOT] Failed to toggle mute:', error);
      Alert.alert('Error', error.message || 'Failed to toggle mute');
    }
  }, [isMuted, conversation]);

  const isActive = conversation.status === 'connected';
  const isAgentSpeaking = conversation.isSpeaking;

  return (
    <View style={{ flex: 1, backgroundColor: t.bg }}>
      <StatusBar style="auto" />

      {/* Header */}
      <View style={{
        padding: 20,
        paddingTop: 60,
        borderBottomWidth: 1,
        borderBottomColor: t.border,
      }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
          <View style={{
            width: 48,
            height: 48,
            borderRadius: 16,
            backgroundColor: t.accentDim,
            borderWidth: 1,
            borderColor: t.accent + "40",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <Bot size={24} color={t.accent} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 18, fontFamily: "Syne_700Bold", color: t.text }}>
              Voice TalkBot
            </Text>
            <Text style={{ fontSize: 13, fontFamily: "Poppins_400Regular", color: t.textMuted }}>
              {isActive ? 'Connected' : 'Ready to talk'}
            </Text>
          </View>
          {isActive && isAgentSpeaking && (
            <View style={{ flexDirection: "row", gap: 2 }}>
              <View style={{ width: 4, height: 16, backgroundColor: t.accent, borderRadius: 2 }} />
              <View style={{ width: 4, height: 20, backgroundColor: t.accent, borderRadius: 2 }} />
              <View style={{ width: 4, height: 14, backgroundColor: t.accent, borderRadius: 2 }} />
            </View>
          )}
        </View>
      </View>

      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 20, gap: 12 }}
      >
        {messages.length === 0 && !isActive && (
          <View style={{ alignItems: "center", paddingVertical: 40 }}>
            <Text style={{ fontSize: 14, fontFamily: "Poppins_400Regular", color: t.textMuted, textAlign: "center" }}>
              Tap the phone button below to start{'\n'}talking with your AI assistant
            </Text>
          </View>
        )}

        {messages.map((msg, idx) => (
          <View
            key={idx}
            style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              backgroundColor: msg.role === 'user' ? t.accent : t.surface,
              padding: 12,
              borderRadius: 12,
              marginBottom: 8,
            }}
          >
            <Text style={{
              fontSize: 14,
              fontFamily: "Poppins_400Regular",
              color: msg.role === 'user' ? '#FFFFFF' : t.text,
            }}>
              {msg.text}
            </Text>
            <Text style={{
              fontSize: 11,
              fontFamily: "Poppins_400Regular",
              color: msg.role === 'user' ? '#FFFFFF99' : t.textMuted,
              marginTop: 4,
            }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </Text>
          </View>
        ))}
      </ScrollView>

      {/* Controls */}
      <View style={{
        padding: 20,
        paddingBottom: 40,
        borderTopWidth: 1,
        borderTopColor: t.border,
        gap: 16,
      }}>
        {/* Status indicator */}
        {isActive && (
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 }}>
            <View style={{
              width: 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: isAgentSpeaking ? t.accent : '#10B981',
            }} />
            <Text style={{ fontSize: 13, fontFamily: "Poppins_400Regular", color: t.textMuted }}>
              {isAgentSpeaking ? 'Agent speaking...' : 'Listening...'}
            </Text>
          </View>
        )}

        <View style={{ flexDirection: "row", gap: 12, justifyContent: "center" }}>
          {/* Mute button */}
          {isActive && (
            <TouchableOpacity
              onPress={handleToggleMute}
              style={{
                width: 56,
                height: 56,
                borderRadius: 28,
                backgroundColor: isMuted ? '#EF4444' : t.surface,
                borderWidth: 2,
                borderColor: isMuted ? '#DC2626' : t.border,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isMuted ? (
                <MicOff size={24} color="#FFFFFF" />
              ) : (
                <Mic size={24} color={t.text} />
              )}
            </TouchableOpacity>
          )}

          {/* Main call button */}
          <TouchableOpacity
            onPress={isActive ? handleStopConversation : handleStartConversation}
            disabled={isStarting}
            style={{
              width: 72,
              height: 72,
              borderRadius: 36,
              backgroundColor: isActive ? '#EF4444' : t.accent,
              borderWidth: 3,
              borderColor: isActive ? '#DC2626' : t.accent + '80',
              alignItems: "center",
              justifyContent: "center",
              elevation: 8,
              shadowColor: isActive ? '#EF4444' : t.accent,
              shadowOffset: { width: 0, height: 4 },
              shadowOpacity: 0.3,
              shadowRadius: 8,
            }}
          >
            {isStarting ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : isActive ? (
              <PhoneOff size={32} color="#FFFFFF" />
            ) : (
              <Phone size={32} color="#FFFFFF" />
            )}
          </TouchableOpacity>
        </View>

        <Text style={{
          fontSize: 12,
          fontFamily: "Poppins_400Regular",
          color: t.textMuted,
          textAlign: "center",
        }}>
          {isActive ? 'Tap to end conversation' : 'Tap to start voice conversation'}
        </Text>
      </View>
    </View>
  );
}
