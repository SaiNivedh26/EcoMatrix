import { StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { View, Image } from 'react-native';
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
        <View style={styles.welcomeRow}>
          <ThemedText type="title" style={styles.title}>Welcome...</ThemedText>
          <Image
            source={require('@/assets/images/EcoGram_Bharat.png')}
            style={styles.welcomeImg}
            resizeMode="contain"
          />
        </View>

        {/* Environmental Map */}
        <ThemedView style={styles.mapSection}>
          <EmbeddedMap height={250} onViewFullMap={handleViewFullMap} />
        </ThemedView>

        <ThemedView style={styles.cuteCol}>
          <ThemedView style={styles.cuteCard}>
            <ThemedText type="subtitle" style={styles.cardTitle}>DIY</ThemedText>
            <ThemedText style={{marginBottom: 8, textAlign: 'center'}}>Upload a picture and get suggestions for your item.</ThemedText>
            <TouchableOpacity style={styles.buttonCenter} onPress={() => router.push('/diy')}>
              <ThemedText style={styles.buttonText}>Go to DIY</ThemedText>
            </TouchableOpacity>
          </ThemedView>
          <ThemedView style={styles.cuteCard}>
            <ThemedText type="subtitle" style={styles.cardTitle}>Exchange</ThemedText>
            <ThemedText style={{marginBottom: 8, textAlign: 'center'}}>Upload an item, add location and description, and share for exchange.</ThemedText>
            <TouchableOpacity style={styles.buttonCenter} onPress={() => router.push('/exchange')}>
              <ThemedText style={styles.buttonText}>Go to Exchange</ThemedText>
            </TouchableOpacity>
          </ThemedView>
        </ThemedView>

        <ThemedText style={styles.footer}>
          Together we can make a difference for our planet!
        </ThemedText>
      </ScrollView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  welcomeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 16,
    marginHorizontal: 8,
  },
  
  welcomeImg: {
    width: 40,
    height: 40,
  },
  cuteCol: {
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20,
    marginBottom: 32,
    marginTop: 8,
  },
  buttonCenter: {
    backgroundColor: Colors.light.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    marginTop: 16,
    alignSelf: 'center',
  },
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
    padding: 0,
  },
  title: {
    marginTop: 32,
    marginBottom: 24,
    color: Colors.light.primary,
    textAlign: 'left',
    fontWeight: 'bold',
    fontSize: 28,
    letterSpacing: 0.5,
  },
  mapSection: {
    marginBottom: 16,
  },
  verticalBox: {
    flexDirection: 'column',
    alignItems: 'center',
    gap: 20,
    marginBottom: 32,
    marginTop: 8,
  },
  cuteCard: {
    backgroundColor: '#e8f5e9',
    borderRadius: 18,
    padding: 20,
    marginVertical: 8,
    alignItems: 'center',
    shadowColor: '#388E3C',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12,
    shadowRadius: 6,
    elevation: 3,
    minWidth: 140,
    maxWidth: 280,
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