import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { getExchanges, ExchangeItem } from '../services/exchangeStorage';

export default function UserExchanges() {
  const [exchanges, setExchanges] = useState<ExchangeItem[]>([]);
  useEffect(() => {
    const loadExchanges = async () => {
      const list = await getExchanges();
      setExchanges(list);
    };
    loadExchanges();
  }, []);
  return (
    <ThemedView style={styles.container}>
      <ThemedText type="title" style={styles.title}>Your Exchanges</ThemedText>
      {exchanges.length === 0 ? (
        <ThemedText>No exchanges submitted yet.</ThemedText>
      ) : (
        exchanges.map(item => (
          <View key={item.id} style={styles.card}>
            {item.image ? (
              <Image source={{ uri: item.image }} style={styles.image} />
            ) : null}
            <ThemedText style={styles.desc}>{item.desc}</ThemedText>
            <ThemedText style={styles.mapText}>
              Location: {item.latitude}, {item.longitude}
            </ThemedText>
          </View>
        ))
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  card: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    width: '100%',
    alignItems: 'center',
  },
  image: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginBottom: 8,
  },
  desc: {
    fontSize: 16,
    marginBottom: 4,
    textAlign: 'center',
  },
  mapText: {
    color: '#388E3C',
    fontSize: 13,
  },
});
