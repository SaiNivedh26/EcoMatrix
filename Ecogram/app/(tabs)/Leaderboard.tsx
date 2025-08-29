import React from 'react';
import { FlatList, Image, StyleSheet, View } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

// Mock Data Example (replace with API later)
const leaderboardData = [
  { id: 1, name: 'Alice', points: 980 },
  { id: 2, name: 'Bob', points: 870 },
  { id: 3, name: 'Charlie', points: 850 },
  { id: 4, name: 'David', points: 400 },
  { id: 5, name: 'Eve', points: 790 },
  { id: 6, name: 'Frank', points: 770 },
  { id: 7, name: 'Grace', points: 760 },
  { id: 8, name: 'Hank', points: 750 },
  { id: 9, name: 'Ivy', points: 720 },
  { id: 10, name: 'Jack', points: 700 },
].sort((a, b) => b.points - a.points);

const currentUserId = 6; // Example: logged-in user

export default function LeaderboardScreen() {
  const topThree = leaderboardData.slice(0, 3);
  const userIndex = leaderboardData.findIndex((u) => u.id === currentUserId);

  // Show up to 10 users
  const displayUsers = leaderboardData.slice(0, 10);

  const renderUserRow = (item: any, index: number) => {
    const rankNum = index + 4;
    const isCurrentUser = item.id === currentUserId;
    return (
      <ThemedView
        style={[
          styles.leaderItem,
          isCurrentUser && styles.currentUserHighlight,
        ]}
      >
        <>
          <ThemedText type="defaultSemiBold" style={styles.rank}>
            {rankNum}
          </ThemedText>
          <Image
            source={{
              uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png',
            }}
            style={styles.avatar}
          />
          <ThemedText type="defaultSemiBold" style={styles.userName}>{item.name}</ThemedText>
          <ThemedText type="defaultSemiBold" style={styles.points}>
            {item.points}
          </ThemedText>
        </>
      </ThemedView>
    );
  };

  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        {/* Padding above leaderboard */}
        <View style={{ paddingTop: 32 }} />
        {/* Title */}
        <ThemedText type="title" style={styles.title}>
          Leaderboard
        </ThemedText>

        {/* Top 3 Section - full green background */}
        <View style={styles.topThreeFullGreen}>
          <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'flex-end' }}>
            {/* 2nd Place */}
            <View style={[styles.topThreeItem, styles.second, { backgroundColor: '#b7defaff', marginRight: 10, marginLeft: 10 }]}> {/* Small space to right of 2nd */}
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={styles.topAvatar}
              />
              <ThemedText type="defaultSemiBold">{topThree[1].name}</ThemedText>
              <ThemedText style={styles.topPoints}>{topThree[1].points}</ThemedText>
              <ThemedText style={styles.topRankNum}>2</ThemedText>
            </View>

            {/* 1st Place - alone, bigger, different color */}
            <View style={[styles.topThreeItem, styles.first, { backgroundColor: '#FFE0B2', width: 80 }]}>
              <View style={{ position: 'absolute', top: -20 }}>
                <IconSymbol name="crown.fill" size={32} color="#FFD700" />
              </View>
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={[styles.topAvatar, { width: 60, height: 60 }]}
              />
              <ThemedText type="defaultSemiBold" style={{ fontSize: 20 }}>{topThree[0].name}</ThemedText>
              <ThemedText style={[styles.topPoints, { fontSize: 16 }]}>{topThree[0].points}</ThemedText>
              <ThemedText style={styles.topRankNum}>1</ThemedText>
            </View>

            {/* 3rd Place */}
            <View style={[styles.topThreeItem, styles.third, { backgroundColor: '#b7defaff', marginLeft: 10 }]}> {/* No extra space after 3rd */}
              <Image
                source={{ uri: 'https://cdn-icons-png.flaticon.com/512/1077/1077012.png' }}
                style={styles.topAvatar}
              />
              <ThemedText type="defaultSemiBold">{topThree[2].name}</ThemedText>
              <ThemedText style={styles.topPoints}>{topThree[2].points}</ThemedText>
              <ThemedText style={styles.topRankNum}>3</ThemedText>
            </View>
          </View>
        </View>

        {/* User and Nearby Ranks */}
        <FlatList
          data={displayUsers.slice(3)}
          renderItem={({ item, index }) => renderUserRow(item, index)}
          keyExtractor={(_, index) => (index + 4).toString()}
        />
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  topThreeFullGreen: {
    backgroundColor: '#E8F5E9', // light green
    borderRadius: 20,
    paddingVertical: 24,
    paddingHorizontal: 12,
    marginBottom: 32,
    marginHorizontal: 8,
    alignItems: 'center',
  },
  topThreeContainer: {
    backgroundColor: '#E8F5E9',
    borderRadius: 20,
    paddingVertical: 24,
    paddingHorizontal: 20,
    marginBottom: 32,
    marginHorizontal: 8,
    alignItems: 'center',
  },
  topRankNum: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginTop: 4,
  },
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 24,
    color: Colors.light.primary,
    textAlign: 'center',
    fontSize: 28,
    fontWeight: 'bold',
  },
  // Top 3 styling
  topThreeWrapper: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 32,
    alignItems: 'flex-end',
    padding: 20,
  },
  topThreeItem: {
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    borderRadius: 16,
    padding: 12,
    width: 85,
  },
  first: {
    marginBottom: 40,
    // Remove marginBottom and marginHorizontal
  },
  second: {
    marginTop: 30, // push 2nd place down
    
  },
  third: {
    marginTop: 30, // push 3rd place down
  },
  topAvatar: {
    width: 50,
    height: 50,
    marginVertical: 6,
  },
  topPoints: {
    color: '#4CAF50',
    fontSize: 18,
  },
  // List users styling
  leaderItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 7,
    borderRadius: 10,
    backgroundColor: '#F5F5F5',
  },
  userName: {
    flex: 1,
    fontSize: 18,
    marginLeft: 4,
    color: Colors.light.text,
    fontWeight: '600',
  },
  currentUserHighlight: {
    backgroundColor: '#E3F2FD', // highlight for logged-in user
  },
  rank: {
    width: 30,
    textAlign: 'center',
    marginRight: 8,
    color: Colors.light.primary,
  },
  avatar: {
    width: 30,
    height: 30,
    marginHorizontal: 8,
  },
  userInfo: {
    flex: 1,
  },
  points: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});