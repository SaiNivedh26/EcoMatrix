import { StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { router } from 'expo-router';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import EmbeddedMap from '@/components/EmbeddedMap';
import { Colors } from '@/constants/Colors';
import { DIYCard } from '@/components/DIYCard';

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
<<<<<<< HEAD

        <ThemedView style={styles.cuteRow}>
          <ThemedView style={styles.cuteCard}>
            <ThemedText type="subtitle" style={styles.cardTitle}>DIY</ThemedText>
            <ThemedText style={{marginBottom: 8, textAlign: 'center'}}>Upload a picture and get suggestions for your item.</ThemedText>
            <TouchableOpacity style={styles.button} onPress={() => router.push('/diy')}>
              <ThemedText style={styles.buttonText}>Go to DIY</ThemedText>
            </TouchableOpacity>
          </ThemedView>
          <ThemedView style={styles.cuteCard}>
            <ThemedText type="subtitle" style={styles.cardTitle}>Exchange</ThemedText>
            <ThemedText style={{marginBottom: 8, textAlign: 'center'}}>Upload an item, add location and description, and share for exchange.</ThemedText>
            <TouchableOpacity style={styles.button} onPress={() => router.push('/exchange')}>
              <ThemedText style={styles.buttonText}>Go to Exchange</ThemedText>
            </TouchableOpacity>
          </ThemedView>
        </ThemedView>

=======
        
        {/* <ThemedView style={styles.card}>
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
        </ThemedView> */}
        
        {/* DIY Projects Section */}
        <DIYCard />
        
>>>>>>> 37cfb92ecfcbd84686b5d683342f34603018544a
        <ThemedText style={styles.footer}>
          Together we can make a difference for our planet!
        </ThemedText>
      </ScrollView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
    gap: 16,
  },
  buttonCol: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    minWidth: 120,
  },
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginTop: 32,
    marginBottom: 24,
    color: Colors.light.primary,
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: 28,
    letterSpacing: 0.5,
  },
  cuteRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-start',
    gap: 20,
    marginBottom: 32,
    marginTop: 8,
  },
  cuteCard: {
    flex: 1,
    backgroundColor: '#e8f5e9',
    borderRadius: 18,
    padding: 20,
    marginHorizontal: 8,
    alignItems: 'center',
    shadowColor: '#388E3C',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 6,
    elevation: 3,
    minWidth: 140,
    maxWidth: 180,
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
  button: {
    backgroundColor: Colors.light.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    marginBottom: 8,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
