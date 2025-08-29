import { StyleSheet, TouchableOpacity } from 'react-native';
import React, { useState } from 'react';
import { Modal, View, TextInput, Button, Alert } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

export default function ProfileScreen() {
  const [modalVisible, setModalVisible] = useState(false);
  const [name, setName] = useState('Jane Smith');
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
        <View style={styles.headerSpace} />
        <ThemedView style={styles.profileHeader}>
          <ThemedText type="title" style={styles.userName}>{name}</ThemedText>
          <ThemedText style={styles.userStats}>EcoWarrior · 745 Points</ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.statsSection}>
          <ThemedView style={styles.statBox}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>12</ThemedText>
            <ThemedText style={styles.statLabel}>Reports</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statBox}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>3</ThemedText>
            <ThemedText style={styles.statLabel}>Badges</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statBox}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>5</ThemedText>
            <ThemedText style={styles.statLabel}>Challenges</ThemedText>
          </ThemedView>
        </ThemedView>
        <ThemedText type="subtitle" style={styles.sectionTitle}>Recent Activity</ThemedText>
        <ThemedView style={styles.activitySection}>
          <ThemedText style={styles.activityItem}>• Reported litter at Central Park</ThemedText>
          <ThemedText style={styles.activityItem}>• Completed "Plastic-Free Day" challenge</ThemedText>
          <ThemedText style={styles.activityItem}>• Earned "EcoWarrior" badge</ThemedText>
        </ThemedView>
        <TouchableOpacity style={styles.settingsButton} onPress={() => setModalVisible(true)}>
          <ThemedText style={styles.settingsButtonText}>Edit</ThemedText>
        </TouchableOpacity>
        <TouchableOpacity style={styles.switchUserButton} onPress={() => {
          require('expo-router').router.push('/vendor-login');
        }}>
          <ThemedText style={styles.switchUserButtonText}>Switch to Vendor</ThemedText>
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
  headerSpace: {
    height: 16,
  },
  container: {
    flex: 1,
    padding: 16,
    paddingTop: 32,
    backgroundColor: '#fff',
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
  statsSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 32,
    backgroundColor: '#e8f5e9',
    borderRadius: 16,
    padding: 16,
  },
  statBox: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    color: Colors.light.primary,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 20,
    color: '#388E3C',
    fontWeight: 'bold',
  },
  sectionTitle: {
    color: Colors.light.primary,
    marginBottom: 16,
    fontWeight: 'bold',
    fontSize: 18,
  },
  activitySection: {
    marginTop: 8,
    padding: 16,
    backgroundColor: '#f5f5f5',
    borderRadius: 16,
    marginBottom: 16,
  },
  activityItem: {
    color: '#333',
    marginBottom: 6,
    fontSize: 15,
  },
  settingsButton: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 12,
    alignSelf: 'center',
    marginBottom: 8,
    width: '60%',
  },
  settingsButtonText: {
    color: Colors.light.primary,
    fontWeight: 'bold',
    fontSize: 16,
  },
  switchUserButton: {
    backgroundColor: Colors.light.primary,
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 20,
    marginBottom: 24,
    alignSelf: 'center',
    width: '60%',
  },
  switchUserButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    width: '80%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 16,
  },
});