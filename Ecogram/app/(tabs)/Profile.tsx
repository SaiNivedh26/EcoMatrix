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
        <ThemedView style={styles.profileHeader}>
          <ThemedView style={styles.avatarContainer}>
            <IconSymbol name="person.fill" size={60} color="white" />
          </ThemedView>
            <ThemedText type="title" style={styles.userName}>{name}</ThemedText>
          <ThemedText style={styles.userStats}>EcoWarrior · 745 Points</ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.statsContainer}>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>12</ThemedText>
            <ThemedText style={styles.statLabel}>Reports</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>3</ThemedText>
            <ThemedText style={styles.statLabel}>Badges</ThemedText>
          </ThemedView>
          <ThemedView style={styles.statItem}>
            <ThemedText type="defaultSemiBold" style={styles.statValue}>5</ThemedText>
            <ThemedText style={styles.statLabel}>Challenges</ThemedText>
          </ThemedView>
        </ThemedView>
        <ThemedText type="subtitle" style={styles.sectionTitle}>Recent Activity</ThemedText>
        <ThemedView style={{backgroundColor: '#F5F5F5', borderRadius: 8, padding: 16, marginBottom: 12}}>
          <ThemedText style={{color: Colors.light.primary, fontWeight: 'bold', marginBottom: 8}}>• Reported litter at Central Park</ThemedText>
          <ThemedText style={{color: Colors.light.primary, fontWeight: 'bold', marginBottom: 8}}>• Completed "Plastic-Free Day" challenge</ThemedText>
          <ThemedText style={{color: Colors.light.primary, fontWeight: 'bold'}}>• Earned "EcoWarrior" badge</ThemedText>
        </ThemedView>
        <TouchableOpacity style={styles.settingsButton} onPress={() => setModalVisible(true)}>
          <ThemedText style={styles.settingsButtonText}>Edit</ThemedText>
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
  container: {
    flex: 1,
    padding: 16,
    paddingTop: 32,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 24,
    marginTop: 32,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: Colors.light.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  userName: {
    color: Colors.light.primary,
    marginBottom: 4,
  },
  userStats: {
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    marginBottom: 24,
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    color: Colors.light.primary,
  },
  statLabel: {
    color: '#666',
  },
  sectionTitle: {
    color: Colors.light.primary,
    marginBottom: 16,
  },
  impactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  impactText: {
    marginLeft: 12,
  },
  settingsButton: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 12,
  },
  settingsButtonText: {
    color: Colors.light.primary,
    fontWeight: 'bold',
  },
});
