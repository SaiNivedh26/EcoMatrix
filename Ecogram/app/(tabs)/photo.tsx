import React, { useState, useEffect, useRef } from 'react';
import { 
  StyleSheet, 
  TouchableOpacity, 
  Modal, 
  Animated, 
  TextInput, 
  Alert, 
  Image, 
  ScrollView,
  Dimensions,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  View
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';
import * as Haptics from 'expo-haptics';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

// Define the report interface
interface Report {
  id: string;
  image: string;
  description: string;
  location: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  timestamp: number;
  issueType: string;
}

export default function PhotoScreen() {
  // State variables
  const [modalVisible, setModalVisible] = useState(false);
  const [image, setImage] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [address, setAddress] = useState<string>('Tap to set location');
  const [issueTypes] = useState(['Pollution', 'Deforestation', 'Waste', 'Wildlife', 'Other']);
  const [selectedIssueType, setSelectedIssueType] = useState<string>('');
  const [showIssueTypes, setShowIssueTypes] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGettingLocation, setIsGettingLocation] = useState(false);
  
  // Animation refs
  const slideAnim = useRef(new Animated.Value(0)).current;
  
  // Request permissions on component mount
  useEffect(() => {
    (async () => {
      // Request camera permissions
      const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
      if (cameraStatus !== 'granted') {
        Alert.alert('Permission required', 'Camera permission is needed to take photos');
      }
      
      // Request media library permissions
      const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (mediaStatus !== 'granted') {
        Alert.alert('Permission required', 'Media library permission is needed to select photos');
      }
      
      // Request location permissions
      const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
      if (locationStatus !== 'granted') {
        Alert.alert('Permission required', 'Location permission is needed to tag your report');
      }
    })();
  }, []);
  
  // Function to pick an image from gallery
  const pickImage = async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });
      
      if (!result.canceled) {
        setImage(result.assets[0].uri);
        setModalVisible(false);
        // Get location when image is selected
        getCurrentLocation();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick an image');
      console.error(error);
    }
  };
  
  // Function to take a photo with camera
  const takePhoto = async () => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });
      
      if (!result.canceled) {
        setImage(result.assets[0].uri);
        setModalVisible(false);
        // Get location when photo is taken
        getCurrentLocation();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take a photo');
      console.error(error);
    }
  };
  
  // Function to get current location
  const getCurrentLocation = async () => {
    try {
      setIsGettingLocation(true);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced
      });
      setLocation(currentLocation);
      
      // Reverse geocode to get the address
      const geocode = await Location.reverseGeocodeAsync({
        latitude: currentLocation.coords.latitude,
        longitude: currentLocation.coords.longitude,
      });
      
      if (geocode.length > 0) {
        const loc = geocode[0];
        const addressComponents = [
          loc.street,
          loc.city,
          loc.region,
          loc.country
        ].filter(Boolean);
        
        const addressText = addressComponents.join(', ');
        setAddress(addressText || 'Location detected');
      }
    } catch (error) {
      setAddress('Location unavailable');
      Alert.alert('Location Error', 'Could not determine your location. Please ensure location services are enabled.');
      console.error(error);
    } finally {
      setIsGettingLocation(false);
    }
  };
  
  // Function to save the report
  const saveReport = async () => {
    // Validate all required fields
    if (!image) {
      Alert.alert('Missing image', 'Please take a photo or select one from your gallery');
      return;
    }
    
    if (!location) {
      Alert.alert('Missing location', 'Please allow location access to tag your report');
      return;
    }
    
    if (!description.trim()) {
      Alert.alert('Missing description', 'Please provide a description of the issue');
      return;
    }
    
    if (!selectedIssueType) {
      Alert.alert('Missing issue type', 'Please select an issue type');
      return;
    }
    
    try {
      setIsSubmitting(true);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      // Create a report object
      const report: Report = {
        id: Date.now().toString(),
        image,
        description,
        location: {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          address,
        },
        timestamp: Date.now(),
        issueType: selectedIssueType,
      };
      
      // Get existing reports or create a new array
      const existingReportsJson = await AsyncStorage.getItem('environmentalReports');
      let reports: Report[] = existingReportsJson ? JSON.parse(existingReportsJson) : [];
      
      // Add the new report
      reports.push(report);
      
      // Save the updated reports array
      await AsyncStorage.setItem('environmentalReports', JSON.stringify(reports));
      
      Alert.alert(
        'Success!', 
        'Your environmental issue report has been saved. Thank you for contributing to a cleaner planet!',
        [
          { 
            text: 'View on Map', 
            onPress: () => router.replace('/(tabs)/map') 
          },
          { 
            text: 'Report Another', 
            onPress: resetForm
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to save your report. Please try again.');
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Reset the form
  const resetForm = () => {
    setImage(null);
    setDescription('');
    setLocation(null);
    setAddress('Tap to set location');
    setSelectedIssueType('');
    setShowIssueTypes(false);
  };
  
  // Show the modal with animation
  const showModal = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setModalVisible(true);
    Animated.timing(slideAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };
  
  // Hide the modal with animation
  const hideModal = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    Animated.timing(slideAnim, {
      toValue: 0,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      setModalVisible(false);
    });
  };
  
  // Handle issue type selection
  const handleIssueTypeSelect = (type: string) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedIssueType(type);
    setShowIssueTypes(false);
  };
  
  // Navigate back to the map
  const navigateToMap = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    router.replace('/(tabs)/map');
  };
  
  return (
    <GreenScreenWrapper>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
        keyboardVerticalOffset={80}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={true}
          keyboardShouldPersistTaps="handled"
          bounces={true}
        >
          <ThemedView style={styles.container}>
            {/* Header */}
            <ThemedView style={styles.header}>
              <ThemedText type="title" style={styles.title}>Report Environmental Issue</ThemedText>
              <ThemedText style={styles.subtitle}>
                Help us track and address environmental issues in your area
              </ThemedText>
            </ThemedView>
            
            {/* Camera/Image Section */}
            <ThemedView style={styles.imageSection}>
              <TouchableOpacity 
                style={[styles.cameraContainer, image && styles.hasImage]} 
                onPress={showModal}
                activeOpacity={0.8}
              >
                {image ? (
                  <>
                    <Image source={{ uri: image }} style={styles.previewImage} />
                    <TouchableOpacity 
                      style={styles.changePhotoButton}
                      onPress={showModal}
                    >
                      <IconSymbol name="camera.fill" size={20} color="white" />
                      <ThemedText style={styles.changePhotoText}>Change</ThemedText>
                    </TouchableOpacity>
                  </>
                ) : (
                  <ThemedView style={styles.cameraPlaceholder}>
                    <IconSymbol name="camera.fill" size={64} color={Colors.light.primary} />
                    <ThemedText style={styles.cameraText}>Tap to take a photo</ThemedText>
                    <ThemedText style={styles.cameraSubtext}>
                      Take a clear photo of the environmental issue
                    </ThemedText>
                  </ThemedView>
                )}
              </TouchableOpacity>
            </ThemedView>
            
            {/* Form Section */}
            <ThemedView style={styles.formSection}>
              {/* Location Field */}
              <TouchableOpacity 
                style={styles.inputGroup} 
                onPress={getCurrentLocation}
                activeOpacity={0.7}
              >
                <ThemedView style={styles.inputHeader}>
                  <IconSymbol name="map.fill" size={18} color={Colors.light.primary} />
                  <ThemedText type="defaultSemiBold" style={styles.inputLabel}>Location</ThemedText>
                </ThemedView>
                <ThemedView style={[styles.inputBox, styles.locationBox]}>
                  {isGettingLocation ? (
                    <ThemedView style={styles.loadingLocation}>
                      <ActivityIndicator color={Colors.light.primary} />
                      <ThemedText style={styles.loadingText}>Getting location...</ThemedText>
                    </ThemedView>
                  ) : (
                    <>
                      <ThemedText numberOfLines={2} style={styles.locationText}>{address}</ThemedText>
                      <IconSymbol name="plus" size={16} color={Colors.light.primary} />
                    </>
                  )}
                </ThemedView>
              </TouchableOpacity>
              
              {/* Issue Type Field */}
              <ThemedView style={styles.inputGroup}>
                <ThemedView style={styles.inputHeader}>
                  <IconSymbol name="leaf.fill" size={18} color={Colors.light.primary} />
                  <ThemedText type="defaultSemiBold" style={styles.inputLabel}>Issue Type</ThemedText>
                </ThemedView>
                <TouchableOpacity 
                  style={[styles.inputBox, selectedIssueType ? styles.activeInput : {}]} 
                  onPress={() => {
                    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    setShowIssueTypes(!showIssueTypes);
                  }}
                >
                  <ThemedText style={selectedIssueType ? styles.selectedText : styles.placeholderText}>
                    {selectedIssueType || 'Select issue type'}
                  </ThemedText>
                  <IconSymbol 
                    name={showIssueTypes ? "chevron.right" : "chevron.right"} 
                    size={16} 
                    color={Colors.light.primary} 
                  />
                </TouchableOpacity>
                
                {showIssueTypes && (
                  <ThemedView style={styles.issueTypesList}>
                    {issueTypes.map((type) => (
                      <TouchableOpacity 
                        key={type} 
                        style={[
                          styles.issueTypeItem, 
                          selectedIssueType === type && styles.selectedIssueType
                        ]}
                        onPress={() => handleIssueTypeSelect(type)}
                      >
                        <ThemedText style={[
                          styles.issueTypeText,
                          selectedIssueType === type && styles.selectedIssueTypeText
                        ]}>
                          {type}
                        </ThemedText>
                        {selectedIssueType === type && (
                          <IconSymbol name="chevron.right" size={16} color="white" />
                        )}
                      </TouchableOpacity>
                    ))}
                  </ThemedView>
                )}
              </ThemedView>
              
              {/* Description Field */}
              <ThemedView style={styles.inputGroup}>
                <ThemedView style={styles.inputHeader}>
                  <IconSymbol name="list.bullet" size={18} color={Colors.light.primary} />
                  <ThemedText type="defaultSemiBold" style={styles.inputLabel}>Description</ThemedText>
                </ThemedView>
                <TextInput
                  style={[styles.inputBox, styles.textArea, styles.textInput]}
                  placeholder="Describe the environmental issue in detail..."
                  placeholderTextColor="#999"
                  multiline
                  value={description}
                  onChangeText={setDescription}
                />
              </ThemedView>
            </ThemedView>
            
            {/* Action Buttons */}
            <ThemedView style={styles.actionButtons}>
              <TouchableOpacity 
                style={styles.cancelButton} 
                onPress={() => {
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                  router.back();
                }}
              >
                <ThemedText style={styles.cancelButtonText}>Cancel</ThemedText>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]} 
                onPress={saveReport}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <>
                    <IconSymbol name="paperplane.fill" size={20} color="white" />
                    <ThemedText style={styles.submitButtonText}>Submit Report</ThemedText>
                  </>
                )}
              </TouchableOpacity>
            </ThemedView>
          </ThemedView>
        </ScrollView>
      </KeyboardAvoidingView>
      
      {/* Modal for camera options */}
      <Modal
        transparent={true}
        visible={modalVisible}
        animationType="none"
        onRequestClose={hideModal}
      >
        <TouchableOpacity 
          style={styles.modalOverlay} 
          activeOpacity={1}
          onPress={hideModal}
        >
          <Animated.View 
            style={[
              styles.modalView,
              {
                transform: [
                  {
                    translateY: slideAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [300, 0],
                    }),
                  },
                ],
              },
            ]}
          >
            <ThemedView style={styles.modalHeader}>
              <ThemedText type="subtitle" style={styles.modalTitle}>Capture Environmental Issue</ThemedText>
              <ThemedText style={styles.modalSubtitle}>Choose how you want to add a photo</ThemedText>
            </ThemedView>
            
            <ThemedView style={styles.modalButtons}>
              <TouchableOpacity style={styles.modalButton} onPress={takePhoto}>
                <ThemedView style={styles.modalIconBg}>
                  <IconSymbol name="camera.fill" size={28} color={Colors.light.primary} />
                </ThemedView>
                <ThemedText style={styles.modalButtonText}>Take a Photo</ThemedText>
                <ThemedText style={styles.modalButtonSubtext}>Use your camera</ThemedText>
              </TouchableOpacity>
              
              <TouchableOpacity style={styles.modalButton} onPress={pickImage}>
                <ThemedView style={styles.modalIconBg}>
                  <IconSymbol name="photo.fill" size={28} color={Colors.light.primary} />
                </ThemedView>
                <ThemedText style={styles.modalButtonText}>Choose from Gallery</ThemedText>
                <ThemedText style={styles.modalButtonSubtext}>Select existing photo</ThemedText>
              </TouchableOpacity>
            </ThemedView>
            
            <TouchableOpacity 
              style={styles.modalCancelButton} 
              onPress={hideModal}
            >
              <ThemedText style={styles.modalCancelText}>Cancel</ThemedText>
            </TouchableOpacity>
          </Animated.View>
        </TouchableOpacity>
      </Modal>
    </GreenScreenWrapper>
  );
}

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 70,
  },
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    marginBottom: 16,
  },
  title: {
    marginTop: 36,
    marginBottom: 8,
    color: Colors.light.primary,
    textAlign: 'center',
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 8,
  },
  imageSection: {
    marginBottom: 20,
  },
  cameraContainer: {
    height: 220,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    position: 'relative',
  },
  hasImage: {
    borderColor: Colors.light.primary,
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  cameraPlaceholder: {
    alignItems: 'center',
    padding: 16,
  },
  cameraText: {
    marginTop: 12,
    color: Colors.light.primary,
    fontWeight: 'bold',
    fontSize: 16,
  },
  cameraSubtext: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 4,
  },
  changePhotoButton: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
  },
  changePhotoText: {
    color: 'white',
    marginLeft: 4,
    fontSize: 12,
  },
  formSection: {
    marginBottom: 20,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  inputLabel: {
    marginLeft: 6,
    color: Colors.light.primary,
  },
  inputBox: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  activeInput: {
    borderColor: Colors.light.primary,
    borderWidth: 1.5,
  },
  locationBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  loadingLocation: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  loadingText: {
    marginLeft: 8,
    color: Colors.light.primary,
  },
  locationText: {
    flex: 1,
    marginRight: 8,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  textInput: {
    color: '#333',
    fontFamily: 'System',
    fontSize: 16,
  },
  placeholderText: {
    color: '#999',
  },
  selectedText: {
    color: Colors.light.primary,
    fontWeight: 'bold',
  },
  issueTypesList: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    marginTop: 4,
    maxHeight: 180,
    zIndex: 1000,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  issueTypeItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  selectedIssueType: {
    backgroundColor: Colors.light.primary,
  },
  issueTypeText: {
    color: '#333',
  },
  selectedIssueTypeText: {
    color: 'white',
    fontWeight: 'bold',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  submitButton: {
    flex: 3,
    backgroundColor: Colors.light.primary,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center',
  },
  submitButtonDisabled: {
    backgroundColor: '#A0A0A0',
  },
  submitButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  cancelButton: {
    flex: 1,
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    marginRight: 12,
  },
  cancelButtonText: {
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'flex-end',
  },
  modalView: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: -3,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  modalHeader: {
    marginBottom: 20,
  },
  modalTitle: {
    textAlign: 'center',
    marginBottom: 4,
    color: Colors.light.primary,
  },
  modalSubtitle: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 24,
  },
  modalButton: {
    alignItems: 'center',
    width: width / 2 - 40,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  modalIconBg: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  modalButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginBottom: 4,
  },
  modalButtonSubtext: {
    fontSize: 12,
    color: '#666',
  },
  modalCancelButton: {
    padding: 16,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    marginTop: 8,
  },
  modalCancelText: {
    color: '#FF3B30',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
