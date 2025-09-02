import {
  BoltIcon,
  CpuChipIcon,
  CubeIcon,
  MicrophoneIcon,
  SparklesIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
} from '@heroicons/react/24/outline';
import React, { useEffect, useRef, useState } from 'react';

interface Model {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  emoji: string;
}

const models: Model[] = [
  {
    id: 'gemma-2b',
    name: 'Gemma 2B',
    description: 'Fast and efficient text generation',
    icon: CpuChipIcon,
    color: '#10b981',
    bgColor: '#f0fdf4',
    emoji: '🤖',
  },
  {
    id: 'phi-3',
    name: 'Phi-3',
    description: 'Microsoft Phi-3 for reasoning tasks',
    icon: CubeIcon,
    color: '#8b5cf6',
    bgColor: '#faf5ff',
    emoji: '🧠',
  },
  {
    id: 'mistral-7b',
    name: 'Mistral 7B',
    description: 'Powerful open-source language model',
    icon: SparklesIcon,
    color: '#f59e0b',
    bgColor: '#fffbeb',
    emoji: '⚡',
  },
  {
    id: 'tiny-model',
    name: 'Tiny Model',
    description: 'Lightweight model for tooling tasks',
    icon: BoltIcon,
    color: '#3b82f6',
    bgColor: '#eff6ff',
    emoji: '🎯',
  },
  {
    id: 'bge-small',
    name: 'BGE Small',
    description: 'Optimized for embeddings and retrieval',
    icon: CpuChipIcon,
    color: '#ef4444',
    bgColor: '#fef2f2',
    emoji: '🔍',
  },
];

interface ModelRouterProps {
  onModelChange?: (model: string) => void;
}

export const ModelRouter: React.FC<ModelRouterProps> = ({ onModelChange }: ModelRouterProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [volume, setVolume] = useState(75);
  const [isMuted, setIsMuted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartX(e.pageX - (containerRef.current?.offsetLeft || 0));
    setScrollLeft(containerRef.current?.scrollLeft || 0);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - (containerRef.current?.offsetLeft || 0);
    const walk = (x - startX) * 2;
    if (containerRef.current) {
      containerRef.current.scrollLeft = scrollLeft - walk;
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    setIsDragging(true);
    setStartX(e.touches[0].pageX - (containerRef.current?.offsetLeft || 0));
    setScrollLeft(containerRef.current?.scrollLeft || 0);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return;
    const x = e.touches[0].pageX - (containerRef.current?.offsetLeft || 0);
    const walk = (x - startX) * 2;
    if (containerRef.current) {
      containerRef.current.scrollLeft = scrollLeft - walk;
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  const scrollToModel = (index: number) => {
    if (containerRef.current) {
      const cardWidth = 280; // card width + gap
      containerRef.current.scrollTo({
        left: index * cardWidth,
        behavior: 'smooth',
      });
      setCurrentIndex(index);
      // Notify parent of model change
      onModelChange?.(models[index].name);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Here you would integrate with the audio pipeline
    console.log(`${isRecording ? 'Stopping' : 'Starting'} recording...`);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    // Here you would control audio output
    console.log(`${isMuted ? 'Unmuting' : 'Muting'} audio...`);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseInt(e.target.value);
    setVolume(newVolume);
    // Here you would adjust audio volume
    console.log(`Volume set to ${newVolume}%`);
  };

  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current) {
        const cardWidth = 280;
        const scrollPosition = containerRef.current.scrollLeft;
        const newIndex = Math.round(scrollPosition / cardWidth);
        setCurrentIndex(Math.min(Math.max(newIndex, 0), models.length - 1));
      }
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  return (
    <div className="w-full h-full flex flex-col" style={{ backgroundColor: '#1a1a1a', color: '#E1E1E1' }}>
      <div className="p-4 border-b" style={{ borderColor: '#333' }}>
        <h2 className="text-lg font-semibold" style={{ color: '#E1E1E1' }}>
          AI Models
        </h2>
        <p className="text-sm" style={{ color: '#888' }}>
          Select your assistant
        </p>
      </div>

      {/* Model Cards Container */}
      <div className="flex-1 overflow-hidden">
        <div
          ref={containerRef}
          className="flex overflow-x-auto gap-4 p-4 cursor-grab active:cursor-grabbing"
          style={{ scrollSnapType: 'x mandatory' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          {models.map((model, index) => {
            const Icon = model.icon;
            return (
              <div
                key={model.id}
                className={`flex-shrink-0 w-64 h-72 rounded-xl border-2 transition-all duration-300 cursor-pointer p-6 flex flex-col items-center justify-center text-center`}
                style={{
                  scrollSnapAlign: 'start',
                  backgroundColor: index === currentIndex ? '#2a2a2a' : '#1e1e1e',
                  borderColor: index === currentIndex ? model.color : '#333',
                  transform: index === currentIndex ? 'scale(1.05)' : 'scale(1)',
                  boxShadow: index === currentIndex ? `0 0 20px ${model.color}30` : 'none',
                }}
                onClick={() => scrollToModel(index)}
              >
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center mb-4 text-2xl"
                  style={{ backgroundColor: model.bgColor }}
                >
                  {model.emoji}
                </div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: '#E1E1E1' }}>
                  {model.name}
                </h3>
                <p className="text-sm leading-relaxed mb-4" style={{ color: '#888' }}>
                  {model.description}
                </p>
                {index === currentIndex && (
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: model.color }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Dots Indicator */}
        <div className="flex justify-center mt-4 space-x-2">
          {models.map((_, index) => (
            <button
              key={index}
              onClick={() => scrollToModel(index)}
              className="w-3 h-3 rounded-full transition-all duration-300"
              style={{
                backgroundColor: index === currentIndex ? models[index].color : '#666',
                transform: index === currentIndex ? 'scale(1.25)' : 'scale(1)',
              }}
            />
          ))}
        </div>
      </div>

      {/* Audio Controls */}
      <div className="p-4 border-t" style={{ borderColor: '#333', backgroundColor: '#1e1e1e' }}>
        <div className="flex items-center justify-center space-x-4">
          {/* Record Button */}
          <button
            onClick={toggleRecording}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-300"
            style={{
              backgroundColor: isRecording ? '#dc2626' : '#374151',
              color: 'white',
            }}
          >
            <MicrophoneIcon className="w-5 h-5" />
            <span>{isRecording ? 'Recording...' : 'Record'}</span>
          </button>

          {/* Volume Control */}
          <div className="flex items-center space-x-3">
            <button onClick={toggleMute} className="p-2 rounded-lg transition-colors" style={{ color: '#888' }}>
              {isMuted ? <SpeakerXMarkIcon className="w-5 h-5" /> : <SpeakerWaveIcon className="w-5 h-5" />}
            </button>
            <input
              type="range"
              min="0"
              max="100"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-24 h-2 rounded-lg appearance-none cursor-pointer"
              style={{ backgroundColor: '#666' }}
              disabled={isMuted}
            />
            <span className="text-sm w-8" style={{ color: '#888' }}>
              {isMuted ? 0 : volume}%
            </span>
          </div>
        </div>
      </div>

      {/* Current Model Info */}
      <div className="p-4 border-t text-center" style={{ borderColor: '#333' }}>
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg" style={{ backgroundColor: '#2a2a2a' }}>
          <span className="text-lg">{models[currentIndex].emoji}</span>
          <span className="text-sm font-medium" style={{ color: '#E1E1E1' }}>
            Active: {models[currentIndex].name}
          </span>
        </div>
      </div>
    </div>
  );
};
