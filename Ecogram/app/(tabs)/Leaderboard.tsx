import React from 'react';
import { FlatList, Image, StyleSheet, View } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

// ---- MOCK: replace with API data ----
const leaderboardData = [
  { id: 1, name: 'Alice', points: 980 },
  { id: 2, name: 'Bob', points: 870 },
  { id: 3, name: 'Charlie', points: 450 },
  { id: 4, name: 'David', points: 800 },
  { id: 5, name: 'Eve', points: 590 },
  { id: 6, name: 'Frank', points: 470 },
  { id: 7, name: 'Grace', points: 760 },
  { id: 8, name: 'Hank', points: 650 },
  { id: 9, name: 'Ivy', points: 720 },
  { id: 10, name: 'Jack', points: 700 },
].sort((a, b) => b.points - a.points);

const currentUserId = 6; // logged-in user

export default function LeaderboardScreen() {
  const topThree = leaderboardData.slice(0, 3);
  const listAfterTop3 = leaderboardData.slice(3, 10); // up to 10 total

  const renderUserRow = ({ item, index }: { item: any; index: number }) => {
    const rankNum = index + 4; // because this list starts after top3
    const isCurrentUser = item.id === currentUserId;

    return (
      <ThemedView style={[styles.leaderItem, isCurrentUser && styles.currentUser]}>
        <ThemedText type="defaultSemiBold" style={styles.rankText}>
          {rankNum}
        </ThemedText>

        <Image
          source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
          style={styles.avatar}
        />

        <ThemedText type="defaultSemiBold" style={styles.userName}>
          {item.name}
        </ThemedText>

        <ThemedText type="defaultSemiBold" style={styles.points}>
          {item.points}
        </ThemedText>
      </ThemedView>
    );
  };

  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        {/* padding above leaderboard */}
        <View style={{ height: 32 }} />

        <ThemedText type="title" style={styles.title}>
          Leaderboard
        </ThemedText>

        {/* Top 3 block with background */}
        <View style={styles.topThreeBlock}>
          <View style={styles.topRow}>
            {/* #2 */}
            <View style={[styles.topCard, styles.second]}>
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={styles.topAvatar}
              />
              <ThemedText type="defaultSemiBold" style={styles.topName}>
                {topThree[1].name}
              </ThemedText>
              <ThemedText style={styles.topScore}>{topThree[1].points}</ThemedText>
              <ThemedText type="defaultSemiBold" style={styles.topRankBadge}>
                2
              </ThemedText>
            </View>

            {/* #1 (center & lifted) */}
            <View style={[styles.topCard, styles.first]}>
              <View style={styles.crownWrap}>
                <IconSymbol name="crown.fill" size={34} color="#FFD700" />
              </View>
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={[styles.topAvatar, { width: 64, height: 64 }]}
              />
              <ThemedText type="defaultSemiBold" style={[styles.topName, styles.firstName]}>
                {topThree[0].name}
              </ThemedText>
              <ThemedText style={[styles.topScore, styles.firstScore]}>
                {topThree[0].points}
              </ThemedText>
              <ThemedText type="defaultSemiBold" style={styles.topRankBadge}>
                1
              </ThemedText>
            </View>

            {/* #3 */}
            <View style={[styles.topCard, styles.third]}>
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={styles.topAvatar}
              />
              <ThemedText type="defaultSemiBold" style={styles.topName}>
                {topThree[2].name}
              </ThemedText>
              <ThemedText style={styles.topScore}>{topThree[2].points}</ThemedText>
              <ThemedText type="defaultSemiBold" style={styles.topRankBadge}>
                3
              </ThemedText>
            </View>
          </View>
        </View>

        {/* Remaining ranks up to 10 */}
        <FlatList
          data={listAfterTop3}
          renderItem={renderUserRow}
          keyExtractor={(item) => `rank-${item.id}`}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 16 },
  title: {
    marginBottom: 20,
    color: Colors.light.primary,
    textAlign: 'center',
    fontSize: 26,
    fontWeight: '700',
  },

  /* --- Top 3 --- */
  topThreeBlock: {
    backgroundColor: '#E8F5E9', // light green bg for the whole top3 box
    borderRadius: 20,
    paddingVertical: 22,
    paddingHorizontal: 12,
    marginBottom: 24,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
  },
  topCard: {
    width: 92,
    borderRadius: 16,
    alignItems: 'center',
    paddingVertical: 10,
    marginHorizontal: 10,
    backgroundColor: '#afd6fbff', // subtle green card, no white “name” badge
  },
  first: {
    marginBottom: 28, // lift center card
    width: 104,
    backgroundColor: '#f2e8beff',
  },
  second: { marginTop: 20 },
  third: { marginTop: 20 },
  crownWrap: { position: 'absolute', top: -22 },
  topAvatar: { width: 52, height: 52, marginVertical: 6 },
  topName: { fontSize: 14, color: Colors.light.primary, textAlign: 'center' },
  firstName: { fontSize: 16, fontWeight: '700' },
  topScore: { fontSize: 13, color: '#4CAF50' },
  firstScore: { fontSize: 15 },
  topRankBadge: { marginTop: 4, fontSize: 14, color: Colors.light.primary },

  /* --- List rows --- */
  leaderItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 12,
    marginBottom: 8,
    borderRadius: 12,
    backgroundColor: '#F5F5F5',
  },
  currentUser: { backgroundColor: '#E3F2FD' }, // highlight current user
  rankText: { width: 30, textAlign: 'center', color: Colors.light.primary, fontSize: 16 },
  avatar: { width: 32, height: 32, marginHorizontal: 8 },
  userName: { flex: 1, fontSize: 16, color: Colors.light.text, fontWeight: '600' },
  points: { fontSize: 16, color: '#4CAF50', fontWeight: '700', marginLeft: 8 },
});