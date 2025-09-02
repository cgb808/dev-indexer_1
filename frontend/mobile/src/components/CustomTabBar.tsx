import { Ionicons } from '@expo/vector-icons';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { LinearGradient } from 'expo-linear-gradient';
import React from 'react';
import { Dimensions, Pressable, StyleSheet, Text, View } from 'react-native';

const { width } = Dimensions.get('window');

const CustomTabBar: React.FC<BottomTabBarProps> = ({ state, descriptors, navigation }) => {
  const getIcon = (routeName: string, isFocused: boolean) => {
    const iconColor = isFocused ? '#FFFFFF' : '#9CA3AF';
    const iconSize = 24;

    switch (routeName) {
      case 'Chat':
        return <Ionicons name="chatbubble-outline" size={iconSize} color={iconColor} />;
      case 'Jarvis':
        return <Ionicons name="hardware-chip-outline" size={iconSize} color={iconColor} />;
      case 'Models':
        return <Ionicons name="flash-outline" size={iconSize} color={iconColor} />;
      default:
        return <Ionicons name="chatbubble-outline" size={iconSize} color={iconColor} />;
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#1E1E1E', '#0f0f0f']} style={styles.gradient}>
        <View style={styles.tabBar}>
          {state.routes.map((route, index) => {
            const descriptor = descriptors[route.key];
            if (!descriptor) return null;
            const { options } = descriptor;
            const label =
              options.tabBarLabel !== undefined
                ? options.tabBarLabel
                : options.title !== undefined
                  ? options.title
                  : route.name;

            const isFocused = state.index === index;

            const onPress = () => {
              const event = navigation.emit({
                type: 'tabPress',
                target: route.key,
                canPreventDefault: true,
              });

              if (!isFocused && !event.defaultPrevented) {
                navigation.navigate(route.name);
              }
            };

            const onLongPress = () => {
              navigation.emit({
                type: 'tabLongPress',
                target: route.key,
              });
            };

            return (
              <Pressable
                key={route.key}
                accessibilityRole="button"
                accessibilityState={isFocused ? { selected: true } : {}}
                accessibilityLabel={options.title || route.name}
                testID={`tab-${route.name}`}
                onPress={onPress}
                onLongPress={onLongPress}
                style={({ pressed }) => [
                  styles.tabItem,
                  {
                    opacity: pressed ? 0.7 : 1,
                  },
                ]}
              >
                <View style={styles.tabContent}>
                  {isFocused && (
                    <LinearGradient
                      colors={['#007AFF', '#8b5cf6']}
                      style={styles.activeIndicator}
                      start={{ x: 0, y: 0 }}
                      end={{ x: 1, y: 1 }}
                    />
                  )}
                  <View style={styles.iconContainer}>{getIcon(route.name, isFocused)}</View>
                  <Text
                    style={[
                      styles.tabLabel,
                      {
                        color: isFocused ? '#FFFFFF' : '#9CA3AF',
                        fontWeight: isFocused ? '600' : '400',
                      },
                    ]}
                  >
                    {typeof label === 'string' ? label : route.name}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>
      </LinearGradient>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  gradient: {
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingTop: 8,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'transparent',
    paddingBottom: 34, // Safe area for iPhone
    paddingTop: 12,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabContent: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  activeIndicator: {
    position: 'absolute',
    top: -8,
    width: 40,
    height: 4,
    borderRadius: 2,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
});

export default CustomTabBar;
