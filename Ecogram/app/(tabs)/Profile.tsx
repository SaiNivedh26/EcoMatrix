import { StyleSheet, TouchableOpacity } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

export default function ProfileScreen() {
  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        <ThemedView style={styles.profileHeader}>
          <ThemedView style={styles.avatarContainer}>
            <IconSymbol name="person.fill" size={60} color="white" />
          </ThemedView>
          <ThemedText type="title" style={styles.userName}>Jane Smith</ThemedText>
          <ThemedText style={styles.userStats}>EcoWarrior · 745 Points</ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.statsContainer}>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>12</ThemedText>
            <ThemedText style={styles.statLabel}>Reports</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>3</ThemedText>
            <ThemedText style={styles.statLabel}>Badges</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>5</ThemedText>
            <ThemedText style={styles.statLabel}>Challenges</ThemedText>
          </ThemedView>
        </ThemedView>
        
        <ThemedText type="subtitle" style={styles.sectionTitle}>Your Impact</ThemedText>
        
        <ThemedView style={styles.impactItem}>
          <IconSymbol name="leaf.fill" size={24} color={Colors.light.primary} />
          <ThemedView style={styles.impactText}>
            <ThemedText type="defaultSemiBold">Carbon Saved</ThemedText>
            <ThemedText>120kg CO2 equivalent</ThemedText>
          </ThemedView>
        </ThemedView>
        
        <ThemedView style={styles.impactItem}>
          <IconSymbol name="drop.fill" size={24} color={Colors.light.primary} />
          <ThemedView style={styles.impactText}>
            <ThemedText type="defaultSemiBold">Water Saved</ThemedText>
            <ThemedText>450 liters</ThemedText>
          </ThemedView>
        </ThemedView>
        
        <TouchableOpacity style={styles.settingsButton}>
          <ThemedText style={styles.settingsButtonText}>Settings</ThemedText>
        </TouchableOpacity>
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: Colors.light.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  userName: {
    color: Colors.light.primary,
    marginBottom: 4,
  },
  userStats: {
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    color: Colors.light.primary,
  },
  statLabel: {
    color: '#666',
  },
  sectionTitle: {
    color: Colors.light.primary,
    marginBottom: 16,
  },
  impactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  impactText: {
    marginLeft: 12,
  },
  settingsButton: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 12,
  },
  settingsButtonText: {
    color: Colors.light.primary,
    fontWeight: 'bold',
  },
});
