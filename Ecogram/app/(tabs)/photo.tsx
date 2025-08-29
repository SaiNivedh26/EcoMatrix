import { StyleSheet, TouchableOpacity } from 'react-native';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

export default function PhotoScreen() {
  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        <ThemedText type="title" style={styles.title}>Report Environmental Issue</ThemedText>
        
        <ThemedView style={styles.cameraContainer}>
          <IconSymbol name="camera.fill" size={80} color={Colors.light.primary} />
          <ThemedText style={styles.cameraText}>Tap to take a photo</ThemedText>
        </ThemedView>
        
        <ThemedView style={styles.formContainer}>
          <ThemedText type="subtitle" style={styles.formTitle}>Issue Details</ThemedText>
          
          <ThemedView style={styles.inputField}>
            <ThemedText type="defaultSemiBold">Location</ThemedText>
            <ThemedView style={styles.inputBox}>
              <ThemedText>Tap to set location</ThemedText>
            </ThemedView>
          </ThemedView>
          
          <ThemedView style={styles.inputField}>
            <ThemedText type="defaultSemiBold">Issue Type</ThemedText>
            <ThemedView style={styles.inputBox}>
              <ThemedText>Select issue type</ThemedText>
            </ThemedView>
          </ThemedView>
          
          <ThemedView style={styles.inputField}>
            <ThemedText type="defaultSemiBold">Description</ThemedText>
            <ThemedView style={[styles.inputBox, styles.textArea]}>
              <ThemedText>Add description...</ThemedText>
            </ThemedView>
          </ThemedView>
        </ThemedView>
        
        <TouchableOpacity style={styles.submitButton}>
          <ThemedText style={styles.submitButtonText}>Submit Report</ThemedText>
        </TouchableOpacity>
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 24,
    color: Colors.light.primary,
    textAlign: 'center',
  },
  cameraContainer: {
    height: 200,
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  cameraText: {
    marginTop: 12,
    color: Colors.light.primary,
  },
  formContainer: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  formTitle: {
    color: Colors.light.primary,
    marginBottom: 16,
  },
  inputField: {
    marginBottom: 16,
  },
  inputBox: {
    backgroundColor: 'white',
    borderRadius: 4,
    padding: 12,
    marginTop: 4,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  textArea: {
    height: 100,
  },
  submitButton: {
    backgroundColor: Colors.light.primary,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  submitButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
