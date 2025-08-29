import { StyleSheet } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

export default function LeaderboardScreen() {
  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        <ThemedText type="title" style={styles.title}>Leaderboard</ThemedText>
        
        <ThemedView style={styles.leaderItem}>
          <ThemedText type="defaultSemiBold" style={styles.rank}>1</ThemedText>
          <ThemedView style={styles.userInfo}>
            <ThemedText type="defaultSemiBold">John Doe</ThemedText>
            <ThemedText>520 points</ThemedText>
          </ThemedView>
          <IconSymbol name="trophy.fill" size={24} color={Colors.light.primary} />
        </ThemedView>
        
        <ThemedView style={styles.leaderItem}>
          <ThemedText type="defaultSemiBold" style={styles.rank}>2</ThemedText>
          <ThemedView style={styles.userInfo}>
            <ThemedText type="defaultSemiBold">Jane Smith</ThemedText>
            <ThemedText>480 points</ThemedText>
          </ThemedView>
        </ThemedView>
        
        <ThemedView style={styles.leaderItem}>
          <ThemedText type="defaultSemiBold" style={styles.rank}>3</ThemedText>
          <ThemedView style={styles.userInfo}>
            <ThemedText type="defaultSemiBold">Alex Johnson</ThemedText>
            <ThemedText>420 points</ThemedText>
          </ThemedView>
        </ThemedView>
        
        <ThemedText style={styles.description}>
          Join our community and contribute to environmental conservation to earn points and climb the leaderboard!
        </ThemedText>
      </ThemedView>
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
  },
  leaderItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    marginBottom: 12,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
  },
  rank: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: Colors.light.primary,
    color: 'white',
    textAlign: 'center',
    textAlignVertical: 'center',
    marginRight: 12,
  },
  userInfo: {
    flex: 1,
  },
  description: {
    marginTop: 24,
    textAlign: 'center',
    color: Colors.light.text,
    lineHeight: 22,
  },
});
