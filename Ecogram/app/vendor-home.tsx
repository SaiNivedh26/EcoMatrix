import React, { useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, ScrollView } from 'react-native';
import { ThemedView } from '@/components/ThemedView';
import MapPage from './(tabs)/map';
import PhotoPage from './(tabs)/photo';
import ProfilePage from './(tabs)/Profile';
import VendorProfileScreen from './vendor-profile';
import VendorTabs from './vendor-tabs';


export default function VendorHome() {
  const [activeTab, setActiveTab] = useState('pickups');
  return (
    <ThemedView style={styles.container}>
      <View style={styles.topBarWrapper}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.tabBar}
        >
          <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('pickups')}>
            <Text style={activeTab === 'pickups' ? styles.tabActive : styles.tabInactive}>Pickups</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('map')}>
            <Text style={activeTab === 'map' ? styles.tabActive : styles.tabInactive}>Map</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('photo')}>
            <Text style={activeTab === 'photo' ? styles.tabActive : styles.tabInactive}>Report</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('profile')}>
            <Text style={activeTab === 'profile' ? styles.tabActive : styles.tabInactive}>Profile</Text>
          </TouchableOpacity>
        </ScrollView>
      </View>
      <View style={styles.tabContent}>
        {activeTab === 'pickups' && (
          <View style={styles.pickupsWrapper}>
            <VendorTabs />
          </View>
        )}
        {activeTab === 'map' && <MapPage />}
        {activeTab === 'photo' && <PhotoPage />}
  {activeTab === 'profile' && <VendorProfileScreen />}
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 32,
    backgroundColor: '#fff',
  },
  topBarWrapper: {
    paddingBottom: 0,
    backgroundColor: '#fff',
    zIndex: 2,
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignItems: 'center',
    marginBottom: 8,
    paddingHorizontal: 8,
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
  tabContent: {
    flex: 1,
    paddingTop: 8,
  },
  pickupsWrapper: {
    flex: 1,
    paddingHorizontal: 0,
    paddingTop: 0,
  },
});