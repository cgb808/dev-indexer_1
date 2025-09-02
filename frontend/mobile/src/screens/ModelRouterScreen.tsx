import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useRef, useState } from 'react';
import { Dimensions, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { PanGestureHandler, State } from 'react-native-gesture-handler';
import CustomButton from '../components/CustomButton';

const { width, height } = Dimensions.get('window');

interface Model {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  emoji: string;
  capabilities: string[];
  isActive: boolean;
}

const models: Model[] = [
  {
    id: 'gemma-2b',
    name: 'Gemma 2B',
    description: 'Fast and efficient text generation',
    icon: 'hardware-chip-outline',
    color: '#10b981',
    emoji: '🤖',
    capabilities: ['Text Generation', 'Code Analysis', 'Quick Responses'],
    isActive: true,
  },
  {
    id: 'phi-3',
    name: 'Phi-3',
    description: 'Advanced reasoning and mathematics',
    icon: 'calculator-outline',
    color: '#8b5cf6',
    emoji: '🧠',
    capabilities: ['Mathematics', 'Reasoning', 'Problem Solving'],
    isActive: false,
  },
  {
    id: 'mistral-7b',
    name: 'Mistral 7B',
    description: 'Powerful open-source language model',
    icon: 'flash-outline',
    color: '#f59e0b',
    emoji: '⚡',
    capabilities: ['General Knowledge', 'Creative Writing', 'Analysis'],
    isActive: false,
  },
  {
    id: 'tiny-model',
    name: 'Tiny Model',
    description: 'Lightweight model for tooling tasks',
    icon: 'construct-outline',
    color: '#3b82f6',
    emoji: '🎯',
    capabilities: ['Tool Classification', 'Quick Actions', 'Automation'],
    isActive: false,
  },
  {
    id: 'bge-small',
    name: 'BGE Small',
    description: 'Optimized for embeddings and retrieval',
    icon: 'search-outline',
    color: '#ef4444',
    emoji: '🔍',
    capabilities: ['Embeddings', 'Retrieval', 'Search'],
    isActive: false,
  },
];

const ModelRouterScreen: React.FC = () => {
  const [activeModelIndex, setActiveModelIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const activeModel = models[activeModelIndex]!;

  const handleModelChange = (index: number) => {
    setActiveModelIndex(index);
    scrollViewRef.current?.scrollTo({
      x: index * (width * 0.8 + 20),
      animated: true,
    });
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  const onGestureEvent = (event: any) => {
    // Track horizontal swipe
  };

  const onHandlerStateChange = (event: any) => {
    if (event.nativeEvent.state === State.END) {
      const { translationX, velocityX } = event.nativeEvent;

      // Detect swipe direction and velocity
      const swipeThreshold = 50;
      const velocityThreshold = 500;

      if (Math.abs(translationX) > swipeThreshold || Math.abs(velocityX) > velocityThreshold) {
        if (translationX > 0 && activeModelIndex > 0) {
          // Swipe right - go to previous model
          handleModelChange(activeModelIndex - 1);
        } else if (translationX < 0 && activeModelIndex < models.length - 1) {
          // Swipe left - go to next model
          handleModelChange(activeModelIndex + 1);
        }
      }
    }
  };

  const renderModelCard = (model: Model, index: number) => {
    const isActive = index === activeModelIndex;

    return (
      <View key={model.id} style={[styles.modelCard, isActive && styles.carouselActiveModelCard]}>
        <LinearGradient
          colors={isActive ? [`${model.color}20`, `${model.color}10`] : ['#2A2A2A', '#1E1E1E']}
          style={styles.modelCardGradient}
        >
          {/* Model Icon */}
          <View style={[styles.modelIcon, { backgroundColor: `${model.color}20` }]}>
            <Text style={styles.modelEmoji}>{model.emoji}</Text>
          </View>

          {/* Model Info */}
          <View style={styles.modelInfo}>
            <Text style={styles.modelName}>{model.name}</Text>
            <Text style={styles.modelDescription}>{model.description}</Text>
          </View>

          {/* Capabilities */}
          <View style={styles.capabilitiesContainer}>
            {model.capabilities.slice(0, 2).map((capability, capIndex) => (
              <View key={capIndex} style={[styles.capabilityChip, { backgroundColor: `${model.color}20` }]}>
                <Text style={[styles.capabilityText, { color: model.color }]}>{capability}</Text>
              </View>
            ))}
          </View>

          {/* Status Indicator */}
          <View style={styles.statusContainer}>
            <View style={[styles.statusDot, { backgroundColor: model.isActive ? '#10B981' : '#6B7280' }]} />
            <Text style={styles.statusText}>{model.isActive ? 'Active' : 'Standby'}</Text>
          </View>
        </LinearGradient>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0f0f', '#1E1E1E']} style={styles.gradient}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View style={styles.logoContainer}>
              <Ionicons name="git-network-outline" size={24} color="#007AFF" />
            </View>
            <Text style={styles.headerTitle}>Model Router</Text>
            <View style={styles.headerActions}>
              <Pressable style={styles.headerButton}>
                <Ionicons name="settings-outline" size={20} color="#9CA3AF" />
              </Pressable>
            </View>
          </View>
        </View>

        {/* Active Model Display */}
        <View style={styles.activeModelSection}>
          <LinearGradient colors={['#2A2A2A', '#1E1E1E']} style={styles.activeModelCard}>
            <View style={styles.activeModelHeader}>
              <View style={[styles.activeModelIcon, { backgroundColor: `${activeModel.color}20` }]}>
                <Text style={styles.activeModelEmoji}>{activeModel.emoji}</Text>
              </View>
              <View style={styles.activeModelInfo}>
                <Text style={styles.activeModelName}>{activeModel.name}</Text>
                <Text style={styles.activeModelDescription}>{activeModel.description}</Text>
              </View>
            </View>

            {/* Audio Controls */}
            <View style={styles.audioControls}>
              <CustomButton title="" onPress={togglePlayback} variant="gradient" size="large" style={styles.playButton}>
                <Ionicons name={isPlaying ? 'pause' : 'play'} size={24} color="#FFFFFF" />
              </CustomButton>
              <View style={styles.audioInfo}>
                <Text style={styles.audioStatus}>{isPlaying ? 'Playing' : 'Paused'}</Text>
                <Text style={styles.audioModel}>{activeModel.name}</Text>
              </View>
            </View>
          </LinearGradient>
        </View>

        {/* Model Carousel */}
        <View style={styles.carouselSection}>
          <Text style={styles.sectionTitle}>Available Models</Text>
          <PanGestureHandler onGestureEvent={onGestureEvent} onHandlerStateChange={onHandlerStateChange}>
            <View style={styles.carouselContainer}>
              <ScrollView
                ref={scrollViewRef}
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.carouselContent}
                snapToInterval={width * 0.8 + 20}
                decelerationRate="fast"
                scrollEnabled={false}
              >
                {models.map((model, index) => renderModelCard(model, index))}
              </ScrollView>
            </View>
          </PanGestureHandler>

          {/* Carousel Indicators */}
          <View style={styles.indicators}>
            {models.map((_, index) => (
              <View key={index} style={[styles.indicator, index === activeModelIndex && styles.activeIndicator]} />
            ))}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionsSection}>
          <View style={styles.actionButtons}>
            <CustomButton
              title="Switch Model"
              onPress={() => handleModelChange((activeModelIndex + 1) % models.length)}
              variant="gradient"
              size="medium"
              style={styles.actionButton}
            />
            <CustomButton
              title="Configure"
              onPress={() => {}}
              variant="outline"
              size="medium"
              style={styles.actionButton}
            />
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
    backgroundColor: '#2A2A2A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '600',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2A2A2A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  activeModelSection: {
    padding: 20,
  },
  activeModelCard: {
    borderRadius: 16,
    padding: 20,
  },
  activeModelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  activeModelIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  activeModelEmoji: {
    fontSize: 24,
  },
  activeModelInfo: {
    flex: 1,
  },
  activeModelName: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 4,
  },
  activeModelDescription: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  audioControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  playButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginRight: 16,
  },
  audioInfo: {
    flex: 1,
  },
  audioStatus: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
  },
  audioModel: {
    color: '#9CA3AF',
    fontSize: 12,
  },
  carouselSection: {
    flex: 1,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  carouselContainer: {
    height: 200,
  },
  carouselContent: {
    paddingRight: 20,
  },
  modelCard: {
    width: width * 0.8,
    height: 200,
    marginRight: 20,
    borderRadius: 16,
    overflow: 'hidden',
  },
  carouselActiveModelCard: {
    transform: [{ scale: 1.05 }],
  },
  modelCardGradient: {
    flex: 1,
    padding: 20,
    justifyContent: 'space-between',
  },
  modelIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'flex-start',
  },
  modelEmoji: {
    fontSize: 20,
  },
  modelInfo: {
    flex: 1,
    marginLeft: 16,
  },
  modelName: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  modelDescription: {
    color: '#9CA3AF',
    fontSize: 14,
    lineHeight: 18,
  },
  capabilitiesContainer: {
    flexDirection: 'row',
    marginTop: 12,
  },
  capabilityChip: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  capabilityText: {
    fontSize: 10,
    fontWeight: '500',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    color: '#9CA3AF',
    fontSize: 12,
  },
  indicators: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 20,
  },
  indicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#333',
    marginHorizontal: 4,
  },
  activeIndicator: {
    backgroundColor: '#007AFF',
    width: 20,
  },
  actionsSection: {
    padding: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
});

export default ModelRouterScreen;
