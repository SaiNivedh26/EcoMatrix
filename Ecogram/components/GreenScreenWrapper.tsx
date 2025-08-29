import React, { ReactNode } from 'react';
import { StyleSheet } from 'react-native';
import { ThemedView } from './ThemedView';
import { Colors } from '@/constants/Colors';

// A wrapper component to ensure all screens use our green theme consistently
interface GreenScreenWrapperProps {
  children: ReactNode;
}

export function GreenScreenWrapper({ children }: GreenScreenWrapperProps) {
  return (
    <ThemedView 
      lightColor={Colors.light.background}
      style={styles.container}
    >
      {children}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
});
