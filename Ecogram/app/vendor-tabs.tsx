import React, { useState, useCallback } from 'react';
import { View, Text, Image, FlatList, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';

interface ExchangeItem {
  id: string;
  image: string;
  description: string;
}

export default function VendorTabs() {
  const [exchanges, setExchanges] = useState<ExchangeItem[]>([]);

  useFocusEffect(
    useCallback(() => {
      const loadExchanges = async () => {
        const data = await AsyncStorage.getItem('exchanges');
        if (data) setExchanges(JSON.parse(data));
        else setExchanges([]);
      };
      loadExchanges();
    }, [])
  );

  const renderExchange = ({ item }: { item: ExchangeItem }) => (
    <View style={styles.exchangeItem}>
      <Image source={{ uri: item.image }} style={styles.exchangeImage} />
      <Text style={styles.exchangeDesc}>{item.description}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Pickups</Text>
      <FlatList
        data={exchanges}
        keyExtractor={item => item.id}
        renderItem={renderExchange}
        ListEmptyComponent={<Text style={styles.emptyText}>No exchanges yet.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#fff' },
  heading: { fontSize: 18, fontWeight: 'bold', marginVertical: 12 },
  exchangeItem: {
    flexDirection: 'row', alignItems: 'center', padding: 12,
    borderBottomWidth: 1, borderBottomColor: '#eee', backgroundColor: '#fafafa',
    borderRadius: 8, marginBottom: 8,
  },
  exchangeImage: { width: 60, height: 60, borderRadius: 8, marginRight: 12 },
  exchangeDesc: { flex: 1, color: '#333', fontSize: 16 },
  emptyText: { textAlign: 'center', color: '#888', marginTop: 32 },
});