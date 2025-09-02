import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import React, { useEffect, useState } from 'react';
import { Dimensions, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import CustomButton from '../components/CustomButton';

const { width } = Dimensions.get('window');

interface JarvisModel {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  capabilities: string[];
  status: 'active' | 'standby' | 'training';
  emoji: string;
}

const jarvisModels: JarvisModel[] = [
  {
    id: 'gemma-2b',
    name: 'Gemma 2B',
    description: 'Fast and efficient text generation',
    icon: 'hardware-chip-outline',
    color: '#10b981',
    capabilities: ['Text Generation', 'Code Analysis', 'Quick Responses'],
    status: 'active',
    emoji: '🤖',
  },
  {
    id: 'phi-3',
    name: 'Phi-3',
    description: 'Advanced reasoning and mathematics',
    icon: 'calculator-outline',
    color: '#8b5cf6',
    capabilities: ['Mathematics', 'Reasoning', 'Problem Solving'],
    status: 'active',
    emoji: '🧠',
  },
  {
    id: 'mistral-7b',
    name: 'Mistral 7B',
    description: 'Powerful open-source language model',
    icon: 'flash-outline',
    color: '#f59e0b',
    capabilities: ['General Knowledge', 'Creative Writing', 'Analysis'],
    status: 'standby',
    emoji: '⚡',
  },
  {
    id: 'tiny-model',
    name: 'Tiny Model',
    description: 'Lightweight model for tooling tasks',
    icon: 'construct-outline',
    color: '#3b82f6',
    capabilities: ['Tool Classification', 'Quick Actions', 'Automation'],
    status: 'active',
    emoji: '🎯',
  },
  {
    id: 'bge-small',
    name: 'BGE Small',
    description: 'Optimized for embeddings and retrieval',
    icon: 'search-outline',
    color: '#ef4444',
    capabilities: ['Embeddings', 'Retrieval', 'Search'],
    status: 'standby',
    emoji: '🔍',
  },
];

const JarvisScreen: React.FC = () => {
  const [activeModel, setActiveModel] = useState('gemma-2b');
  const [isListening, setIsListening] = useState(false);
  const [currentCommand, setCurrentCommand] = useState('');
  const [systemStatus, setSystemStatus] = useState('Ready');
  const [tokensPerSecond, setTokensPerSecond] = useState(0);
  const [cpuUsage, setCpuUsage] = useState(23);
  const [memoryUsage, setMemoryUsage] = useState(15);

  useEffect(() => {
    // Simulate system heartbeat
    const interval = setInterval(() => {
      setSystemStatus((prev) => (prev === 'Ready' ? 'Active' : prev === 'Active' ? 'Processing' : 'Ready'));
      setTokensPerSecond(Math.random() * 30 + 10);
      setCpuUsage(Math.random() * 20 + 15);
      setMemoryUsage(Math.random() * 10 + 10);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleModelSelect = (modelId: string) => {
    setActiveModel(modelId);
    setCurrentCommand(`Switching to ${jarvisModels.find((m) => m.id === modelId)?.name}...`);
    setTimeout(() => setCurrentCommand(''), 2000);
  };

  const toggleListening = () => {
    setIsListening(!isListening);
    setCurrentCommand(isListening ? 'Listening stopped' : 'Listening for commands...');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10b981';
      case 'standby':
        return '#f59e0b';
      case 'training':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const activeModelData = jarvisModels.find((m) => m.id === activeModel);

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0f0f', '#1E1E1E']} style={styles.gradient}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoText}>J</Text>
            </View>
            <Text style={styles.headerTitle}>JustJarvis</Text>
            <View style={styles.statusIndicator}>
              <View style={[styles.statusDot, { backgroundColor: getStatusColor(systemStatus.toLowerCase()) }]} />
              <Text style={[styles.statusText, { color: getStatusColor(systemStatus.toLowerCase()) }]}>
                {systemStatus}
              </Text>
            </View>
          </View>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Active Model Display */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Assistant</Text>
            {activeModelData && (
              <View style={styles.activeModelCard}>
                <LinearGradient colors={['#2A2A2A', '#1E1E1E']} style={styles.modelCardGradient}>
                  <View style={styles.modelHeader}>
                    <View style={[styles.modelIcon, { backgroundColor: `${activeModelData.color}20` }]}>
                      <Text style={styles.modelEmoji}>{activeModelData.emoji}</Text>
                    </View>
                    <View style={styles.modelInfo}>
                      <Text style={styles.modelName}>{activeModelData.name}</Text>
                      <Text style={styles.modelDescription}>{activeModelData.description}</Text>
                    </View>
                  </View>

                  {/* Capabilities */}
                  <View style={styles.capabilitiesContainer}>
                    <Text style={styles.capabilitiesTitle}>Capabilities</Text>
                    <View style={styles.capabilitiesList}>
                      {activeModelData.capabilities.map((capability, index) => (
                        <View key={index} style={[styles.capabilityBadge, { borderColor: activeModelData.color }]}>
                          <Text style={[styles.capabilityText, { color: activeModelData.color }]}>{capability}</Text>
                        </View>
                      ))}
                    </View>
                  </View>

                  {/* Current Command */}
                  {currentCommand && (
                    <View style={styles.commandContainer}>
                      <Text style={styles.commandText}>{currentCommand}</Text>
                    </View>
                  )}
                </LinearGradient>
              </View>
            )}
          </View>

          {/* Model Selection */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Available Models</Text>
            <View style={styles.modelsGrid}>
              {jarvisModels.map((model) => (
                <Pressable
                  key={model.id}
                  style={[styles.modelButton, activeModel === model.id && { borderColor: model.color, borderWidth: 2 }]}
                  onPress={() => handleModelSelect(model.id)}
                >
                  <LinearGradient
                    colors={
                      activeModel === model.id ? [`${model.color}20`, `${model.color}10`] : ['#2A2A2A', '#1E1E1E']
                    }
                    style={styles.modelButtonGradient}
                  >
                    <View style={[styles.modelButtonIcon, { backgroundColor: `${model.color}20` }]}>
                      <Text style={styles.modelButtonEmoji}>{model.emoji}</Text>
                    </View>
                    <View style={styles.modelButtonInfo}>
                      <Text style={styles.modelButtonName}>{model.name}</Text>
                      <View style={styles.modelButtonStatus}>
                        <View
                          style={[styles.modelButtonStatusDot, { backgroundColor: getStatusColor(model.status) }]}
                        />
                        <Text style={styles.modelButtonStatusText}>{model.status}</Text>
                      </View>
                    </View>
                  </LinearGradient>
                </Pressable>
              ))}
            </View>
          </View>

          {/* System Stats */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>System Metrics</Text>
            <View style={styles.metricsGrid}>
              <View style={styles.metricCard}>
                <LinearGradient colors={['#2A2A2A', '#1E1E1E']} style={styles.metricGradient}>
                  <View style={styles.metricHeader}>
                    <Ionicons name="hardware-chip-outline" size={24} color="#007AFF" />
                    <Text style={styles.metricTitle}>CPU Usage</Text>
                  </View>
                  <Text style={[styles.metricValue, { color: '#007AFF' }]}>{cpuUsage.toFixed(0)}%</Text>
                  <Text style={styles.metricSubtitle}>4 cores active</Text>
                  <View style={styles.metricBar}>
                    <View style={[styles.metricBarFill, { width: `${cpuUsage}%`, backgroundColor: '#007AFF' }]} />
                  </View>
                </LinearGradient>
              </View>

              <View style={styles.metricCard}>
                <LinearGradient colors={['#2A2A2A', '#1E1E1E']} style={styles.metricGradient}>
                  <View style={styles.metricHeader}>
                    <Ionicons name="server-outline" size={24} color="#10B981" />
                    <Text style={styles.metricTitle}>Memory</Text>
                  </View>
                  <Text style={[styles.metricValue, { color: '#10B981' }]}>{memoryUsage.toFixed(1)}GB</Text>
                  <Text style={styles.metricSubtitle}>of 8GB used</Text>
                  <View style={styles.metricBar}>
                    <View
                      style={[
                        styles.metricBarFill,
                        { width: `${(memoryUsage / 8) * 100}%`, backgroundColor: '#10B981' },
                      ]}
                    />
                  </View>
                </LinearGradient>
              </View>

              <View style={styles.metricCard}>
                <LinearGradient colors={['#2A2A2A', '#1E1E1E']} style={styles.metricGradient}>
                  <View style={styles.metricHeader}>
                    <Ionicons name="flash-outline" size={24} color="#8b5cf6" />
                    <Text style={styles.metricTitle}>Tokens/sec</Text>
                  </View>
                  <Text style={[styles.metricValue, { color: '#8b5cf6' }]}>{tokensPerSecond.toFixed(1)}</Text>
                  <Text style={styles.metricSubtitle}>processing speed</Text>
                  <View style={styles.metricBar}>
                    <View
                      style={[
                        styles.metricBarFill,
                        { width: `${Math.min(tokensPerSecond * 3, 100)}%`, backgroundColor: '#8b5cf6' },
                      ]}
                    />
                  </View>
                </LinearGradient>
              </View>
            </View>
          </View>
        </ScrollView>

        {/* Bottom Action Bar */}
        <View style={styles.actionBar}>
          <CustomButton
            title={isListening ? 'Stop Listening' : 'Start Listening'}
            onPress={toggleListening}
            variant={isListening ? 'outline' : 'gradient'}
            size="large"
            style={styles.listenButton}
          />
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
    backgroundColor: 'transparent',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  logoText: {
    color: '#007AFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 20,
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
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  activeModelCard: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  modelCardGradient: {
    padding: 20,
  },
  modelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  modelIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  modelEmoji: {
    fontSize: 24,
  },
  modelInfo: {
    flex: 1,
  },
  modelName: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 4,
  },
  modelDescription: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  capabilitiesContainer: {
    marginBottom: 16,
  },
  capabilitiesTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 12,
  },
  capabilitiesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  capabilityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  capabilityText: {
    fontSize: 12,
    fontWeight: '500',
  },
  commandContainer: {
    backgroundColor: '#333',
    borderRadius: 12,
    padding: 12,
  },
  commandText: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  modelsGrid: {
    gap: 12,
  },
  modelButton: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  modelButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  modelButtonIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  modelButtonEmoji: {
    fontSize: 18,
  },
  modelButtonInfo: {
    flex: 1,
  },
  modelButtonName: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  modelButtonStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modelButtonStatusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  modelButtonStatusText: {
    color: '#9CA3AF',
    fontSize: 12,
    textTransform: 'capitalize',
  },
  metricsGrid: {
    gap: 16,
  },
  metricCard: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  metricGradient: {
    padding: 20,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  metricTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '500',
    marginLeft: 8,
  },
  metricValue: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  metricSubtitle: {
    color: '#9CA3AF',
    fontSize: 12,
    marginBottom: 12,
  },
  metricBar: {
    height: 6,
    backgroundColor: '#333',
    borderRadius: 3,
  },
  metricBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  actionBar: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  listenButton: {
    width: '100%',
  },
});

export default JarvisScreen;
