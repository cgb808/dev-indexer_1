import { BoltIcon, CpuChipIcon, CubeIcon, SparklesIcon } from '@heroicons/react/24/outline';
import React, { useEffect, useRef, useState } from 'react';

interface Model {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
}

const models: Model[] = [
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: 'Advanced reasoning and creativity',
    icon: CubeIcon,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    description: 'Balanced performance and safety',
    icon: SparklesIcon,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
  },
  {
    id: 'gemini',
    name: 'Gemini',
    description: 'Fast and efficient responses',
    icon: BoltIcon,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    id: 'mistral',
    name: 'Mistral',
    description: 'Open-source excellence',
    icon: CpuChipIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
];

export const ModelRouter: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);
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
    }
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
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Model Router</h2>
        <p className="text-gray-600">Swipe or click to route between AI models</p>
      </div>

      {/* Model Cards Container */}
      <div
        ref={containerRef}
        className="flex overflow-x-auto scrollbar-hide gap-4 pb-4 cursor-grab active:cursor-grabbing"
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
              className={`flex-shrink-0 w-64 h-80 rounded-xl border-2 transition-all duration-300 cursor-pointer ${
                index === currentIndex ? 'border-blue-500 shadow-lg scale-105' : 'border-gray-200 hover:border-gray-300'
              } ${model.bgColor}`}
              style={{ scrollSnapAlign: 'start' }}
              onClick={() => scrollToModel(index)}
            >
              <div className="p-6 h-full flex flex-col items-center justify-center text-center">
                <div
                  className={`w-16 h-16 rounded-full ${model.bgColor} ${model.color} flex items-center justify-center mb-4`}
                >
                  <Icon className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{model.name}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{model.description}</p>
                {index === currentIndex && <div className="mt-4 w-3 h-3 bg-blue-500 rounded-full"></div>}
              </div>
            </div>
          );
        })}
      </div>

      {/* Dots Indicator */}
      <div className="flex justify-center mt-6 space-x-2">
        {models.map((_, index) => (
          <button
            key={index}
            onClick={() => scrollToModel(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentIndex ? 'bg-blue-500 scale-125' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Current Model Info */}
      <div className="text-center mt-6">
        <div className="inline-flex items-center space-x-2 bg-white px-4 py-2 rounded-lg shadow-sm border">
          {React.createElement(models[currentIndex].icon, { className: 'w-5 h-5 text-gray-600' })}
          <span className="text-sm font-medium text-gray-900">Active: {models[currentIndex].name}</span>
        </div>
      </div>
    </div>
  );
};
