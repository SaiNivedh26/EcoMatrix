import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, Modal, View, TextInput, Button, Alert } from 'react-native';
import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { Colors } from '@/constants/Colors';
import { router } from 'expo-router';

export default function VendorProfileScreen() {
  const [modalVisible, setModalVisible] = useState(false);
  const [name, setName] = useState('Vijay Kumar');
  const [password, setPassword] = useState('');
  const [localPassword, setLocalPassword] = useState('');

  const handleSave = () => {
    setLocalPassword(password);
    setModalVisible(false);
    Alert.alert('Saved', 'Your changes have been saved locally.');
  };

  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        <ThemedView style={styles.profileHeader}>
          <ThemedText type="title" style={styles.userName}>{name}</ThemedText>
          <ThemedText style={styles.userStats}>EcoVendor</ThemedText>
        </ThemedView>
        <ThemedText type="subtitle" style={styles.sectionTitle}>Recent Activity</ThemedText>
        <ThemedView style={styles.activitySection}>
          <ThemedText style={styles.activityItem}>• Exchanged 10kg Plastic</ThemedText>
          <ThemedText style={styles.activityItem}>• Sold 5kg Iron</ThemedText>
          <ThemedText style={styles.activityItem}>• Added new item for sale</ThemedText>
        </ThemedView>
        <TouchableOpacity style={styles.settingsButton} onPress={() => setModalVisible(true)}>
          <ThemedText style={styles.settingsButtonText}>Edit</ThemedText>
        </TouchableOpacity>
        <TouchableOpacity style={styles.switchUserButton} onPress={() => router.push('/login')}>
          <ThemedText style={styles.switchUserButtonText}>Switch to User</ThemedText>
        </TouchableOpacity>
        <Modal
          animationType="slide"
          transparent={true}
          visible={modalVisible}
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <ThemedText type="title" style={{marginBottom: 16}}>Edit Profile</ThemedText>
              <TextInput
                style={styles.input}
                placeholder="Change Name"
                value={name}
                onChangeText={setName}
              />
              <TextInput
                style={styles.input}
                placeholder="Change Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
              <View style={{flexDirection: 'row', justifyContent: 'space-between', marginTop: 16}}>
                <Button title="Save" onPress={handleSave} />
                <Button title="Cancel" color="#888" onPress={() => setModalVisible(false)} />
              </View>
            </View>
          </View>
        </Modal>
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  header: {
    paddingTop: 24,
    paddingBottom: 8,
    backgroundColor: 'white',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    marginBottom: 8,
  },
  headerTitle: {
    color: Colors.light.primary,
    fontSize: 28,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  container: {
    flex: 1,
    padding: 16,
    paddingTop: 32,
    backgroundColor: '#f3fbe8',
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 16,
  },
  userName: {
    color: Colors.light.primary,
    marginBottom: 4,
    fontSize: 24,
    fontWeight: 'bold',
  },
  userStats: {
    color: '#666',
    fontSize: 16,
    marginBottom: 4,
  },
  sectionTitle: {
    color: Colors.light.primary,
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  activitySection: {
    marginBottom: 24,
    marginLeft: 8,
  },
  activityItem: {
    color: '#333',
    fontSize: 15,
    marginBottom: 4,
  },
  settingsButton: {
    backgroundColor: Colors.light.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    alignSelf: 'center',
    marginBottom: 12,
  },
  settingsButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  switchUserButton: {
    backgroundColor: Colors.light.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 20,
    alignSelf: 'center',
    marginBottom: 12,
  },
  switchUserButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    width: '80%',
    alignItems: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 15,
    marginBottom: 16,
    borderRadius: 10,
    fontSize: 16,
    width: '100%',
  },
});
