import * as Haptics from 'expo-haptics';
import { LinearGradient } from 'expo-linear-gradient';
import React from 'react';
import { ActivityIndicator, Pressable, PressableProps, Text, TextStyle, ViewStyle } from 'react-native';

export interface CustomButtonProps extends PressableProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'gradient';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'link' | 'search' | 'imagebutton';
  hitSlop?: { top?: number; left?: number; bottom?: number; right?: number };
  testID?: string;
  children?: React.ReactNode;
}

const CustomButton: React.FC<CustomButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  style,
  textStyle,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  hitSlop = { top: 10, left: 10, bottom: 10, right: 10 },
  testID,
  children,
  ...pressableProps
}) => {
  const handlePress = () => {
    if (!disabled && !loading) {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onPress();
    }
  };

  const getButtonStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      borderRadius: 12,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'row',
      ...getSizeStyle(),
    };

    switch (variant) {
      case 'primary':
        return {
          ...baseStyle,
          backgroundColor: '#007AFF',
        };
      case 'secondary':
        return {
          ...baseStyle,
          backgroundColor: '#6B7280',
        };
      case 'outline':
        return {
          ...baseStyle,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderColor: '#007AFF',
        };
      case 'gradient':
        return {
          ...baseStyle,
          padding: 0, // Remove padding for gradient
        };
      default:
        return baseStyle;
    }
  };

  const getSizeStyle = (): ViewStyle => {
    switch (size) {
      case 'small':
        return {
          paddingHorizontal: 16,
          paddingVertical: 8,
          minHeight: 36,
        };
      case 'large':
        return {
          paddingHorizontal: 32,
          paddingVertical: 16,
          minHeight: 56,
        };
      case 'medium':
      default:
        return {
          paddingHorizontal: 24,
          paddingVertical: 12,
          minHeight: 44,
        };
    }
  };

  const getTextStyle = (): TextStyle => {
    const baseTextStyle: TextStyle = {
      fontWeight: '600',
      textAlign: 'center',
    };

    switch (size) {
      case 'small':
        baseTextStyle.fontSize = 14;
        break;
      case 'large':
        baseTextStyle.fontSize = 18;
        break;
      case 'medium':
      default:
        baseTextStyle.fontSize = 16;
        break;
    }

    switch (variant) {
      case 'primary':
      case 'gradient':
        baseTextStyle.color = '#FFFFFF';
        break;
      case 'secondary':
        baseTextStyle.color = '#FFFFFF';
        break;
      case 'outline':
        baseTextStyle.color = '#007AFF';
        break;
    }

    if (disabled) {
      baseTextStyle.color = '#9CA3AF';
    }

    return baseTextStyle;
  };

  const renderContent = () => (
    <>
      {loading && (
        <ActivityIndicator
          size="small"
          color={variant === 'outline' ? '#007AFF' : '#FFFFFF'}
          style={{ marginRight: 8 }}
        />
      )}
      {children ? children : <Text style={[getTextStyle(), textStyle]}>{loading ? 'Loading...' : title}</Text>}
    </>
  );

  if (variant === 'gradient') {
    return (
      <Pressable
        onPress={handlePress}
        disabled={disabled || loading}
        accessibilityLabel={accessibilityLabel || title}
        accessibilityHint={accessibilityHint}
        accessibilityRole={accessibilityRole}
        accessibilityState={{ disabled: disabled || loading }}
        hitSlop={hitSlop}
        testID={testID}
        style={({ pressed }) => [
          {
            opacity: pressed ? 0.8 : 1,
            borderRadius: 12,
          },
          style,
        ]}
        {...pressableProps}
      >
        <LinearGradient
          colors={['#007AFF', '#8b5cf6']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[getButtonStyle(), getSizeStyle()]}
        >
          {renderContent()}
        </LinearGradient>
      </Pressable>
    );
  }

  return (
    <Pressable
      onPress={handlePress}
      disabled={disabled || loading}
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityRole={accessibilityRole}
      accessibilityState={{ disabled: disabled || loading }}
      hitSlop={hitSlop}
      testID={testID}
      style={({ pressed }) => [
        getButtonStyle(),
        {
          opacity: disabled || loading ? 0.5 : pressed ? 0.8 : 1,
        },
        style,
      ]}
      {...pressableProps}
    >
      {renderContent()}
    </Pressable>
  );
};

export default CustomButton;
