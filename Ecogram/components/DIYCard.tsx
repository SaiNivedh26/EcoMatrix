import React from 'react';
import { StyleSheet, TouchableOpacity } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';
import { router } from 'expo-router';

export const DIYCard = () => {
  const navigateToDIY = () => {
    router.push('/diy')
  };

  return (
    <ThemedView style={styles.container}>
      <ThemedText style={styles.sectionTitle}>Upcycle Your Waste</ThemedText>
      
      <ThemedView style={styles.cardContent}>
        <ThemedView style={styles.textContainer}>
          <ThemedText style={styles.title}>DIY Projects</ThemedText>
          <ThemedText style={styles.description}>
            Turn your waste into creative and useful projects. Upload photos of your waste items to get customized DIY ideas.
          </ThemedText>
          <TouchableOpacity 
            style={styles.button} 
            onPress={navigateToDIY}
          >
            <ThemedText style={styles.buttonText}>Explore DIY Ideas</ThemedText>
            <IconSymbol name="arrow.right" size={16} color="#FFFFFF" />
          </TouchableOpacity>
        </ThemedView>
        
        <ThemedView style={styles.imageContainer}>
          <IconSymbol name="leaf.fill" size={48} color={Colors.light.primary} />
        </ThemedView>
      </ThemedView>
    </ThemedView>
  );
};

const styles = StyleSheet.create({
  container: {
    marginTop: 24,
    marginBottom: 16,
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#F5F5F5',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginBottom: 12,
  },
  cardContent: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
  },
  textContainer: {
    flex: 3,
    padding: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: Colors.light.primary,
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  button: {
    backgroundColor: Colors.light.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginRight: 8,
  },
  imageContainer: {
    flex: 2,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
