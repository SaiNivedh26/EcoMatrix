import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { BlurView } from 'expo-blur';
import { StyleSheet } from 'react-native';

export default function BlurTabBarBackground() {
  return (
    <BlurView
      // Always use light theme with a green tint
      tint="light"
      intensity={85}
      style={StyleSheet.absoluteFill}
    />
  );
}

export function useBottomTabOverflow() {
  return useBottomTabBarHeight();
}
