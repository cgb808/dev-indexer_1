import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useRef, useState } from 'react';
import { FlatList, Pressable, SafeAreaView, StyleSheet, Text, TextInput, View } from 'react-native';
import CustomButton from '../components/CustomButton';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatScreen: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm ZenGlow AI. How can I help you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMicMuted, setIsMicMuted] = useState(false);
  const [volumeLevel, setVolumeLevel] = useState(0.7);
  const [isRecording, setIsRecording] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  const sendMessage = () => {
    if (inputText.trim() === '') return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `I received your message: "${userMessage.text}". This is a simulated response from ZenGlow AI.`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const toggleMicMute = () => {
    setIsMicMuted(!isMicMuted);
  };

  const adjustVolume = (newVolume: number) => {
    setVolumeLevel(Math.max(0, Math.min(1, newVolume)));
  };

  const startVoiceRecording = () => {
    if (isMicMuted) return;
    setIsRecording(true);
    // Simulate voice recording for 2 seconds
    setTimeout(() => {
      setIsRecording(false);
      const voiceMessage: Message = {
        id: Date.now().toString(),
        text: '🎤 Voice message received and transcribed',
        isUser: true,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, voiceMessage]);

      // Simulate AI response
      setIsTyping(true);
      setTimeout(() => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'I received your voice message! Voice input is now supported in ZenGlow.',
          isUser: false,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
        setIsTyping(false);
      }, 1500);
    }, 2000);
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[styles.messageContainer, item.isUser ? styles.userMessage : styles.aiMessage]}>
      <LinearGradient
        colors={item.isUser ? ['#007AFF', '#8b5cf6'] : ['#2A2A2A', '#1E1E1E']}
        style={styles.messageBubble}
      >
        <Text style={[styles.messageText, item.isUser ? styles.userMessageText : styles.aiMessageText]}>
          {item.text}
        </Text>
        <Text style={[styles.timestamp, item.isUser ? styles.userTimestamp : styles.aiTimestamp]}>
          {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </LinearGradient>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0f0f', '#1E1E1E']} style={styles.gradient}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoText}>ZG</Text>
            </View>
            <Text style={styles.headerTitle}>ZenGlow Chat</Text>
            <View style={styles.headerActions}>
              <Pressable onPress={toggleMicMute} style={styles.headerButton}>
                <Ionicons name={isMicMuted ? 'mic-off' : 'mic'} size={20} color={isMicMuted ? '#EF4444' : '#10B981'} />
              </Pressable>
              <View style={styles.statusIndicator}>
                <View style={styles.statusDot} />
                <Text style={styles.statusText}>Online</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Messages Container */}
        <View style={styles.messagesArea}>
          <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={renderMessage}
            keyExtractor={(item) => item.id}
            style={styles.messagesList}
            contentContainerStyle={styles.messagesContainer}
            onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
            showsVerticalScrollIndicator={false}
            ListFooterComponent={
              isTyping ? (
                <View style={styles.typingContainer}>
                  <View style={styles.typingBubble}>
                    <Text style={styles.typingText}>ZenGlow is typing...</Text>
                    <View style={styles.typingDots}>
                      <View style={[styles.typingDot, styles.dot1]} />
                      <View style={[styles.typingDot, styles.dot2]} />
                      <View style={[styles.typingDot, styles.dot3]} />
                    </View>
                  </View>
                </View>
              ) : null
            }
          />
        </View>

        {/* Input Area - Always visible */}
        <View style={styles.inputContainer}>
          {/* Volume Control */}
          <View style={styles.volumeControl}>
            <Ionicons name="volume-low" size={16} color="#9CA3AF" />
            <View style={styles.volumeBar}>
              <View style={[styles.volumeFill, { width: `${volumeLevel * 100}%` }]} />
            </View>
            <Ionicons name="volume-high" size={16} color="#9CA3AF" />
          </View>

          <View style={styles.inputWrapper}>
            {/* Microphone Button */}
            <CustomButton
              title=""
              onPress={isRecording ? () => {} : startVoiceRecording}
              variant={isRecording ? 'gradient' : 'outline'}
              size="medium"
              style={isMicMuted ? styles.micButtonMuted : styles.micButton}
              disabled={isMicMuted}
            >
              <Ionicons
                name={isRecording ? 'radio-button-on' : isMicMuted ? 'mic-off' : 'mic'}
                size={20}
                color={isMicMuted ? '#9CA3AF' : isRecording ? '#FF4444' : '#007AFF'}
              />
            </CustomButton>

            <TextInput
              style={styles.textInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Type your message..."
              placeholderTextColor="#666666"
              multiline
              maxLength={500}
              editable={true}
              autoCapitalize="sentences"
              autoCorrect={true}
              keyboardType="default"
              returnKeyType="default"
              blurOnSubmit={false}
              textAlignVertical="top"
              underlineColorAndroid="transparent"
              selectionColor="#007AFF"
            />

            {/* Send Button */}
            <CustomButton
              title=""
              onPress={sendMessage}
              variant="gradient"
              size="medium"
              style={styles.sendButton}
              disabled={inputText.trim() === ''}
            >
              <Ionicons name="send" size={20} color="#FFFFFF" />
            </CustomButton>
          </View>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
    flexDirection: 'column',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'transparent',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  logoText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10B981',
    marginRight: 6,
  },
  statusText: {
    color: '#10B981',
    fontSize: 12,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2A2A2A',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  messagesList: {
    flex: 1,
  },
  messagesArea: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
    paddingBottom: 20,
  },
  messageContainer: {
    marginBottom: 12,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  aiMessage: {
    alignSelf: 'flex-start',
  },
  messageBubble: {
    borderRadius: 18,
    padding: 12,
    minWidth: 80,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 20,
  },
  userMessageText: {
    color: '#FFFFFF',
  },
  aiMessageText: {
    color: '#E1E1E1',
  },
  timestamp: {
    fontSize: 10,
    marginTop: 4,
    opacity: 0.7,
  },
  userTimestamp: {
    color: '#FFFFFF',
    textAlign: 'right',
  },
  aiTimestamp: {
    color: '#9CA3AF',
    textAlign: 'left',
  },
  typingContainer: {
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  typingBubble: {
    backgroundColor: '#2A2A2A',
    borderRadius: 18,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    maxWidth: '60%',
  },
  typingText: {
    color: '#9CA3AF',
    fontSize: 14,
    marginRight: 8,
  },
  typingDots: {
    flexDirection: 'row',
  },
  typingDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#9CA3AF',
    marginHorizontal: 2,
  },
  dot1: {
    opacity: 0.3,
  },
  dot2: {
    opacity: 0.6,
  },
  dot3: {
    opacity: 1,
  },
  inputContainer: {
    borderTopWidth: 1,
    borderTopColor: '#333',
    backgroundColor: '#2A2A2A',
    minHeight: 120,
    maxHeight: 200,
    paddingTop: 8,
  },
  volumeControl: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 8,
    backgroundColor: '#1E1E1E',
  },
  volumeBar: {
    flex: 1,
    height: 4,
    backgroundColor: '#333',
    borderRadius: 2,
    marginHorizontal: 12,
  },
  volumeFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 16,
  },
  micButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    marginRight: 12,
    paddingHorizontal: 0,
    paddingVertical: 0,
  },
  micButtonMuted: {
    width: 44,
    height: 44,
    borderRadius: 22,
    marginRight: 12,
    paddingHorizontal: 0,
    paddingVertical: 0,
    opacity: 0.5,
  },
  textInput: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: '#000000',
    fontSize: 16,
    maxHeight: 100,
    marginRight: 12,
    borderWidth: 2,
    borderColor: '#007AFF',
    minHeight: 44,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    paddingHorizontal: 0,
    paddingVertical: 0,
  },
});

export default ChatScreen;
