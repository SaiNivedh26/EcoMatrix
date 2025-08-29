import React, { useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { ThemedView } from '@/components/ThemedView';
import Leaderboard from './(tabs)/Leaderboard';
import MapPage from './(tabs)/map';
import PhotoPage from './(tabs)/photo';
import ProfilePage from './(tabs)/Profile';
import VendorTabs from './vendor-tabs';

export default function VendorHome() {
  const [activeTab, setActiveTab] = React.useState('pickups');
  return (
    <ThemedView style={styles.container}>
      <View style={styles.tabBar}>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('pickups')}>
          <Text style={activeTab === 'pickups' ? styles.tabActive : styles.tabInactive}>Pickups</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('leaderboard')}>
          <Text style={activeTab === 'leaderboard' ? styles.tabActive : styles.tabInactive}>Leaderboard</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('map')}>
          <Text style={activeTab === 'map' ? styles.tabActive : styles.tabInactive}>Map</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('photo')}>
          <Text style={activeTab === 'photo' ? styles.tabActive : styles.tabInactive}>Photo</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('profile')}>
          <Text style={activeTab === 'profile' ? styles.tabActive : styles.tabInactive}>Profile</Text>
        </TouchableOpacity>
      </View>
      {activeTab === 'pickups' && <VendorTabs />}
      {activeTab === 'leaderboard' && <Leaderboard />}
      {activeTab === 'map' && <MapPage />}
      {activeTab === 'photo' && <PhotoPage />}
      {activeTab === 'profile' && <ProfilePage />}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 32,
    backgroundColor: '#fff',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 8,
  },
  tabBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  tabActive: {
    color: '#388E3C',
    fontWeight: 'bold',
    fontSize: 16,
    borderBottomWidth: 2,
    borderBottomColor: '#388E3C',
  },
  tabInactive: {
    color: '#888',
    fontSize: 16,
  },
});


