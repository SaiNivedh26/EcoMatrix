import React from 'react';
import { saveExchange, getExchanges, ExchangeItem } from '../services/exchangeStorage';
import { View, Text, StyleSheet, TouchableOpacity, Image, TextInput } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

export default function ExchangePage() {
  const [image, setImage] = React.useState<string | null>(null);
  const [desc, setDesc] = React.useState('');
  const [location, setLocation] = React.useState({ latitude: 37.78825, longitude: -122.4324 });
  const [markerSet, setMarkerSet] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<'form' | 'list'>('form');
  const [exchanges, setExchanges] = React.useState<ExchangeItem[]>([]);

  const pickImage = async () => {
    let result = await require('expo-image-picker').launchImageLibraryAsync({
      mediaTypes: require('expo-image-picker').MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });
    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };
  const handleMapPress = (e: { nativeEvent: { coordinate: { latitude: number; longitude: number } } }) => {
    setLocation(e.nativeEvent.coordinate);
    setMarkerSet(true);
  };
  const handleSubmit = async () => {
    if (!image || !desc || !markerSet) return;
    setSubmitting(true);
    await saveExchange({
      id: Date.now().toString(),
      image,
      desc,
      latitude: location.latitude,
      longitude: location.longitude,
    });
    setImage(null);
    setDesc('');
    setMarkerSet(false);
    setSubmitting(false);
    alert('Exchange submitted!');
  };
  const loadExchanges = async () => {
    const list = await getExchanges();
    setExchanges(list.reverse()); // Show most recent first
  };

  React.useEffect(() => {
    loadExchanges();
  }, []);

  return (
    <ThemedView style={styles.container}>
      <View style={{ flexDirection: 'row', justifyContent: 'center', marginBottom: 16, gap: 12 }}>
        <TouchableOpacity style={[styles.uploadBtn, activeTab === 'form' && { backgroundColor: '#388E3C' }]} onPress={() => setActiveTab('form')}>
          <Text style={styles.uploadText}>Add Exchange</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.uploadBtn, activeTab === 'list' && { backgroundColor: '#388E3C' }]} onPress={() => { setActiveTab('list'); loadExchanges(); }}>
          <Text style={styles.uploadText}>View List</Text>
        </TouchableOpacity>
      </View>
      {activeTab === 'form' ? (
        <>
          <TouchableOpacity style={styles.uploadBtn} onPress={pickImage}>
            <Text style={styles.uploadText}>Upload Image</Text>
          </TouchableOpacity>
          {image && (
            <Image source={{ uri: image }} style={styles.imageSmall} />
          )}
          <TextInput
            style={styles.input}
            placeholder="Add a description..."
            value={desc}
            onChangeText={setDesc}
          />
          <View style={styles.mapContainer}>
            <MapView
              style={styles.map}
              initialRegion={{
                latitude: location.latitude,
                longitude: location.longitude,
                latitudeDelta: 0.01,
                longitudeDelta: 0.01,
              }}
              onPress={handleMapPress}
            >
              {markerSet && (
                <Marker coordinate={location} />
              )}
            </MapView>
          </View>
          <TouchableOpacity style={styles.uploadBtn} onPress={async () => {
            if (!image || !desc || !markerSet) return;
            await saveExchange({
              id: Date.now().toString(),
              image,
              desc,
              latitude: location.latitude,
              longitude: location.longitude,
            });
            setImage(null);
            setDesc('');
            setMarkerSet(false);
            await loadExchanges();
            setActiveTab('list');
          }}>
            <Text style={styles.uploadText}>Add Exchange</Text>
          </TouchableOpacity>
        </>
      ) : (
        <View style={{ width: '100%' }}>
          <ThemedText type="title" style={styles.title}>Recent Exchanges</ThemedText>
          {exchanges.length === 0 ? (
            <ThemedText>No exchanges submitted yet.</ThemedText>
          ) : (
            exchanges.map(item => (
              <View key={item.id} style={{ backgroundColor: '#F5F5F5', borderRadius: 8, padding: 12, marginBottom: 12, alignItems: 'center' }}>
                {item.image ? (
                  <Image source={{ uri: item.image }} style={{ width: 80, height: 80, borderRadius: 8, marginBottom: 8 }} />
                ) : null}
                <ThemedText style={{ fontWeight: 'bold', marginBottom: 4 }}>{item.desc}</ThemedText>
                <ThemedText style={{ color: '#388E3C', fontSize: 13 }}>Location: {item.latitude}, {item.longitude}</ThemedText>
              </View>
            ))
          )}
        </View>
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 16,
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  desc: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 8,
  },
  imageSmall: {
    width: 120,
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
  },
  uploadBtn: {
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    marginBottom: 20,
  },
  uploadText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  image: {
    width: 200,
    height: 200,
    borderRadius: 16,
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 16,
    width: '100%',
  },
  mapContainer: {
    width: '100%',
    height: 180,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
  },
  map: {
    flex: 1,
  },
});
