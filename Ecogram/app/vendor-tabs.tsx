import React, { useState, useEffect } from 'react';
import { Image } from 'react-native';
import { getExchanges, ExchangeItem } from '../services/exchangeStorage';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

function PickupsTab() {
  const [exchanges, setExchanges] = useState<ExchangeItem[]>([]);
  const loadExchanges = async () => {
    const list = await getExchanges();
    setExchanges(list);
  };
  useEffect(() => {
    loadExchanges();
  }, []);
  return (
    <View style={styles.tabContainer}>
      <ThemedText type="title" style={styles.tabTitle}>Pickups</ThemedText>
      <TouchableOpacity style={styles.refreshBtn} onPress={loadExchanges}>
        <Text style={{ color: '#388E3C', fontWeight: 'bold' }}>Refresh List</Text>
      </TouchableOpacity>
      {exchanges.length === 0 ? (
        <ThemedText>No exchanges available.</ThemedText>
      ) : (
        exchanges.map(item => (
          <View key={item.id} style={styles.exchangeCard}>
            {item.image ? (
              <Image source={{ uri: item.image }} style={{ width: 80, height: 80, borderRadius: 8, marginBottom: 8 }} />
            ) : null}
            <ThemedText type="subtitle">{item.desc}</ThemedText>
            <ThemedText style={styles.mapText}>
              Location: {item.latitude}, {item.longitude}
            </ThemedText>
          </View>
        ))
      )}
    </View>
  );
}

export default function VendorTabs() {
  const [activeTab, setActiveTab] = useState('home');
  return (
    <ThemedView style={styles.container}>
      <View style={styles.tabBar}>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('home')}>
          <Text style={activeTab === 'home' ? styles.tabActive : styles.tabInactive}>Home</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.tabBtn} onPress={() => setActiveTab('pickups')}>
          <Text style={activeTab === 'pickups' ? styles.tabActive : styles.tabInactive}>Pickups</Text>
        </TouchableOpacity>
      </View>
      {activeTab === 'home' ? (
        <View style={styles.tabContainer}>
          <ThemedText type="title" style={styles.tabTitle}>Vendor Home</ThemedText>
          <ThemedText>Welcome! You are logged in as a vendor.</ThemedText>
        </View>
      ) : (
        <PickupsTab />
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  refreshBtn: {
    backgroundColor: '#e8f5e9',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 16,
    marginBottom: 12,
    alignSelf: 'center',
  },
  container: {
    flex: 1,
    paddingTop: 32,
    backgroundColor: '#fff',
  },
  tabBar: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 16,
  },
  tabBtn: {
    paddingHorizontal: 24,
    paddingVertical: 8,
  },
  tabActive: {
    color: '#388E3C',
    fontWeight: 'bold',
    fontSize: 18,
    borderBottomWidth: 2,
    borderBottomColor: '#388E3C',
  },
  tabInactive: {
    color: '#888',
    fontSize: 18,
  },
  tabContainer: {
    padding: 16,
    alignItems: 'center',
  },
  tabTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  exchangeCard: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    width: '100%',
  },
  mapText: {
    color: '#388E3C',
    marginTop: 4,
    fontSize: 13,
  },
});
