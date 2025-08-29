import { StyleSheet, ScrollView } from 'react-native';
import { router } from 'expo-router';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import EmbeddedMap from '@/components/EmbeddedMap';
import { Colors } from '@/constants/Colors';

export default function HomeScreen() {
  const handleViewFullMap = () => {
    router.push('/(tabs)/map');
  };

  return (
    <GreenScreenWrapper>
      <ScrollView style={styles.container}>
        <ThemedText type="title" style={styles.title}>Welcome to EcoMatrix</ThemedText>
        
        {/* Environmental Map */}
        <ThemedView style={styles.mapSection}>
          <EmbeddedMap height={250} onViewFullMap={handleViewFullMap} />
        </ThemedView>
        
        <ThemedView style={styles.card}>
          <ThemedText type="subtitle" style={styles.cardTitle}>Environmental Impact</ThemedText>
          <ThemedText>
            Track your daily activities and see how they impact the environment. Small changes 
            can make a big difference!
          </ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.card}>
          <ThemedText type="subtitle" style={styles.cardTitle}>Community Challenges</ThemedText>
          <ThemedText>
            Join community challenges to reduce your carbon footprint and earn points. Compete 
            with friends and make a positive impact together.
          </ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.card}>
          <ThemedText type="subtitle" style={styles.cardTitle}>Eco Tips</ThemedText>
          <ThemedText>
            Get daily tips on how to live more sustainably. Learn about recycling, energy 
            conservation, and eco-friendly products.
          </ThemedText>
        </ThemedView>
        
        <ThemedText style={styles.footer}>
          Together we can make a difference for our planet!
        </ThemedText>
      </ScrollView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 24,
    color: Colors.light.primary,
    textAlign: 'center',
  },
  mapSection: {
    marginBottom: 16,
  },
  card: {
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
    borderLeftWidth: 4,
    borderLeftColor: Colors.light.primary,
  },
  cardTitle: {
    color: Colors.light.primary,
    marginBottom: 8,
  },
  footer: {
    marginTop: 24,
    textAlign: 'center',
    fontStyle: 'italic',
    color: Colors.light.primary,
  },
});
