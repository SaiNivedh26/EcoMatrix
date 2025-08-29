import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, Image, TouchableOpacity, FlatList, StyleSheet, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface ExchangeItem {
  id: string;
  image: string;
  description: string;
}

export default function ExchangeScreen() {
  const [tab, setTab] = useState<'add' | 'list'>('add');
  const [image, setImage] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [exchanges, setExchanges] = useState<ExchangeItem[]>([]);

  useEffect(() => {
    const loadExchanges = async () => {
      try {
        const data = await AsyncStorage.getItem('exchanges');
        if (data) setExchanges(JSON.parse(data));
      } catch (e) {
        console.log('Failed to load exchanges', e);
      }
    };
    loadExchanges();
  }, []);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });
    if (!result.canceled && result.assets && result.assets.length > 0) {
      setImage(result.assets[0].uri);
    }
  };

  const addExchange = async () => {
    if (!image || !description) {
      Alert.alert('Please select an image and enter a description.');
      return;
    }
    const newExchange: ExchangeItem = {
      id: Date.now().toString(),
      image,
      description,
    };
    const updatedExchanges = [newExchange, ...exchanges];
    setExchanges(updatedExchanges);
    await AsyncStorage.setItem('exchanges', JSON.stringify(updatedExchanges));
    setImage(null);
    setDescription('');
  };

  const renderExchange = ({ item }: { item: ExchangeItem }) => (
    <View style={styles.exchangeItem}>
      <Image source={{ uri: item.image }} style={styles.exchangeImage} />
      <Text style={styles.exchangeDesc}>{item.description}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Add Exchange</Text>
      <TouchableOpacity style={styles.imagePicker} onPress={pickImage}>
        {image ? (
          <Image source={{ uri: image }} style={styles.previewImage} />
        ) : (
          <Text style={styles.imagePickerText}>Pick an Image</Text>
        )}
      </TouchableOpacity>
      <TextInput
        style={styles.input}
        placeholder="Enter description"
        value={description}
        onChangeText={setDescription}
        multiline
      />
      <Button title="Add Exchange" onPress={addExchange} />
      <Text style={styles.heading}>Exchange List</Text>
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
  imagePicker: {
    width: 120, height: 120, borderRadius: 16, backgroundColor: '#f0f0f0',
    justifyContent: 'center', alignItems: 'center', marginBottom: 16, overflow: 'hidden',
  },
  imagePickerText: { color: '#888' },
  previewImage: { width: 120, height: 120, borderRadius: 16 },
  input: {
    width: '100%', minHeight: 40, borderColor: '#ccc', borderWidth: 1,
    borderRadius: 8, padding: 8, marginBottom: 16, textAlignVertical: 'top',
  },
  exchangeItem: {
    flexDirection: 'row', alignItems: 'center', padding: 12,
    borderBottomWidth: 1, borderBottomColor: '#eee', backgroundColor: '#fafafa',
    borderRadius: 8, marginBottom: 8,
  },
  exchangeImage: { width: 60, height: 60, borderRadius: 8, marginRight: 12 },
  exchangeDesc: { flex: 1, color: '#333', fontSize: 16 },
  emptyText: { textAlign: 'center', color: '#888', marginTop: 32 },
});