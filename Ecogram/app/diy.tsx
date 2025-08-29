import React, { useState } from 'react';
import { 
  StyleSheet, 
  TouchableOpacity, 
  Alert, 
  Image, 
  ScrollView, 
  ActivityIndicator, 
  Modal
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { IconSymbol } from '@/components/ui/IconSymbol';
import { Colors } from '@/constants/Colors';

// Backend API URL
const BACKEND_URL = 'http://172.20.10.4:8000';

// Project difficulty levels for color coding
const DIFFICULTY_COLORS = {
  Easy: '#4CAF50',   // Green
  Medium: '#FF9800', // Orange
  Hard: '#F44336',   // Red
};

interface ImageItem {
  uri: string;
  type?: string;
  name?: string;
}

interface Material {
  material: string;
  quantity: string;
}

interface Step {
  step_number: number;
  description: string;
  estimated_time: string;
  safety_tips: string;
}

interface GeneratedImage {
  base64: string;
  filename: string;
  url: string;
  type: string;
  source: string;
}

interface TutorialSource {
  title: string;
  url: string;
  type: string;
  scraped: boolean;
  steps_found: number;
  materials_found: number;
}

interface Project {
  project_name: string;
  difficulty_level: string;
  materials_required: Material[];
  steps: Step[];
  estimated_time: string;
  safety_tips: string[];
  image_description: string;
  image_generation_prompt: string;
  generated_image: GeneratedImage;
  image_generation_failed: boolean;
  image_failure_reason?: string;
}

interface ProjectResponse {
  success: boolean;
  projects: {
    easy: Project;
    medium: Project;
    hard: Project;
    tutorial_sources: TutorialSource[];
  };
}

export default function DIYScreen() {
  const [images, setImages] = useState<ImageItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [projectResults, setProjectResults] = useState<ProjectResponse | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Function to pick images from gallery
  const pickImages = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: false, // Changed to false since backend only processes one image
        quality: 0.8,
      });
      
      if (!result.canceled) {
        const newImages = result.assets.map(asset => ({
          uri: asset.uri,
          type: 'image/jpeg',
          name: asset.uri.split('/').pop() || `image_${Date.now()}.jpg`,
        }));
        setImages([...images, ...newImages]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick images');
      console.error(error);
    }
  };
  
  // Function to take photo with camera
  const takePhoto = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        quality: 0.8,
      });
      
      if (!result.canceled) {
        const newImage = {
          uri: result.assets[0].uri,
          type: 'image/jpeg',
          name: `image_${Date.now()}.jpg`,
        };
        setImages([...images, newImage]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take a photo');
      console.error(error);
    }
  };
  
  // Function to remove an image
  const removeImage = (index: number) => {
    const updatedImages = [...images];
    updatedImages.splice(index, 1);
    setImages(updatedImages);
  };
  
  // Function to process images
  const processImages = async () => {
    if (images.length === 0) {
      Alert.alert('No Images', 'Please select at least one image to process');
      return;
    }
    
    setIsProcessing(true);
    
    try {
      // Create form data
      const formData = new FormData();
      
      // Backend expects a single file with parameter name 'file'
      // Use the first image only
      if (images.length > 0) {
        const image = images[0];
        
        // Append to form data with the correct parameter name
        formData.append('file', {
          uri: image.uri,
          type: image.type,
          name: image.name,
        } as any);
      }
      
      // Make API request to backend
      const response = await fetch(`${BACKEND_URL}/analyze-diy`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      
      const data = await response.json() as ProjectResponse;
      setProjectResults(data);
      
      // Default to showing the 'easy' project first
      setSelectedDifficulty('easy');
      
    } catch (error) {
      console.error('Error processing images:', error);
      Alert.alert(
        'Processing Error', 
        'Failed to process images. Please check your connection and try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  // Function to view project details
  const viewProjectDetails = (project: Project) => {
    setSelectedProject(project);
    setModalVisible(true);
  };
  
  // Function to show difficulty selector
  const renderDifficultySelector = () => {
    if (!projectResults) return null;
    
    const difficulties = [
      { key: 'easy', label: 'Easy' },
      { key: 'medium', label: 'Medium' },
      { key: 'hard', label: 'Hard' },
    ];
    
    return (
      <ThemedView style={styles.difficultySelector}>
        <ThemedText style={styles.sectionTitle}>Select Difficulty Level</ThemedText>
        <ThemedView style={styles.difficultyButtons}>
          {difficulties.map((difficulty) => (
            <TouchableOpacity
              key={difficulty.key}
              style={[
                styles.difficultyButton,
                selectedDifficulty === difficulty.key && styles.difficultyButtonSelected,
                { borderColor: DIFFICULTY_COLORS[difficulty.label as keyof typeof DIFFICULTY_COLORS] }
              ]}
              onPress={() => setSelectedDifficulty(difficulty.key)}
            >
              <ThemedText style={[
                styles.difficultyButtonText,
                selectedDifficulty === difficulty.key && styles.difficultyButtonTextSelected,
                { color: selectedDifficulty === difficulty.key ? 'white' : DIFFICULTY_COLORS[difficulty.label as keyof typeof DIFFICULTY_COLORS] }
              ]}>
                {difficulty.label}
              </ThemedText>
            </TouchableOpacity>
          ))}
        </ThemedView>
      </ThemedView>
    );
  };

  // Function to render project preview
  const renderProjectPreview = () => {
    if (!projectResults || !selectedDifficulty) return null;
    
    const project = projectResults.projects[selectedDifficulty as keyof typeof projectResults.projects] as Project;
    
    return (
      <ThemedView style={styles.projectPreview}>
        <ThemedText style={styles.sectionTitle}>Project Preview</ThemedText>
        
        <ThemedView style={styles.projectCard}>
          <ThemedText style={styles.projectName}>{project.project_name}</ThemedText>
          
          <ThemedView style={styles.projectImageContainer}>
            {project.generated_image ? (
              <Image 
                source={{ uri: `${BACKEND_URL}${project.generated_image.url}` }} 
                style={styles.projectImage}
                resizeMode="cover"
              />
            ) : (
              <ThemedView style={styles.noImagePlaceholder}>
                <IconSymbol name="photo.fill" size={48} color={Colors.light.primary} />
                <ThemedText>No image available</ThemedText>
              </ThemedView>
            )}
          </ThemedView>
          
          <ThemedView style={styles.projectInfo}>
            <ThemedView style={styles.infoRow}>
              <IconSymbol name="clock.fill" size={16} color={Colors.light.primary} />
              <ThemedText style={styles.infoText}>Time: {project.estimated_time}</ThemedText>
            </ThemedView>
            
            <ThemedView style={styles.infoRow}>
              <IconSymbol name="wrench" size={16} color={Colors.light.primary} />
              <ThemedText style={styles.infoText}>
                Materials: {project.materials_required.length} items
              </ThemedText>
            </ThemedView>
            
            <ThemedView style={styles.infoRow}>
              <IconSymbol name="list.number" size={16} color={Colors.light.primary} />
              <ThemedText style={styles.infoText}>
                Steps: {project.steps.length} steps
              </ThemedText>
            </ThemedView>
          </ThemedView>
          
          <TouchableOpacity 
            style={styles.viewDetailsButton}
            onPress={() => viewProjectDetails(project)}
          >
            <ThemedText style={styles.viewDetailsButtonText}>View Full Details</ThemedText>
          </TouchableOpacity>
        </ThemedView>
      </ThemedView>
    );
  };

  // Function to render project details modal
  const renderProjectDetailsModal = () => {
    if (!selectedProject) return null;
    
    return (
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <ThemedView style={styles.modalOverlay}>
          <ThemedView style={styles.modalContent}>
            <ThemedView style={styles.modalHeader}>
              <ThemedText style={styles.modalTitle}>{selectedProject.project_name}</ThemedText>
              <TouchableOpacity 
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <IconSymbol name="xmark" size={24} color="#333" />
              </TouchableOpacity>
            </ThemedView>
            
            <ScrollView style={styles.modalScrollView}>
              {/* Project Image */}
              {selectedProject.generated_image && (
                <Image 
                  source={{ uri: `${BACKEND_URL}${selectedProject.generated_image.url}` }} 
                  style={styles.modalProjectImage}
                  resizeMode="cover"
                />
              )}
              
              {/* Difficulty & Time */}
              <ThemedView style={styles.projectDetailSection}>
                <ThemedView style={styles.projectDetailRow}>
                  <ThemedView style={[
                    styles.difficultyBadge, 
                    { backgroundColor: DIFFICULTY_COLORS[selectedProject.difficulty_level as keyof typeof DIFFICULTY_COLORS] }
                  ]}>
                    <ThemedText style={styles.difficultyBadgeText}>
                      {selectedProject.difficulty_level}
                    </ThemedText>
                  </ThemedView>
                  <ThemedText style={styles.estimatedTime}>
                    Est. Time: {selectedProject.estimated_time}
                  </ThemedText>
                </ThemedView>
              </ThemedView>
              
              {/* Materials */}
              <ThemedView style={styles.projectDetailSection}>
                <ThemedText style={styles.projectDetailSectionTitle}>Materials Required</ThemedText>
                {selectedProject.materials_required.map((material, index) => (
                  <ThemedView key={index} style={styles.materialItem}>
                    <ThemedText style={styles.materialName}>{material.material}</ThemedText>
                    <ThemedText style={styles.materialQuantity}>{material.quantity}</ThemedText>
                  </ThemedView>
                ))}
              </ThemedView>
              
              {/* Steps */}
              <ThemedView style={styles.projectDetailSection}>
                <ThemedText style={styles.projectDetailSectionTitle}>Steps</ThemedText>
                {selectedProject.steps.map((step) => (
                  <ThemedView key={step.step_number} style={styles.stepItem}>
                    <ThemedView style={styles.stepNumberContainer}>
                      <ThemedText style={styles.stepNumber}>{step.step_number}</ThemedText>
                    </ThemedView>
                    <ThemedView style={styles.stepContent}>
                      <ThemedText style={styles.stepDescription}>{step.description}</ThemedText>
                      <ThemedText style={styles.stepTime}>Time: {step.estimated_time}</ThemedText>
                      {step.safety_tips && (
                        <ThemedView style={styles.safetyTipContainer}>
                          <ThemedText style={styles.safetyTipTitle}>Safety Tip:</ThemedText>
                          <ThemedText style={styles.safetyTipText}>{step.safety_tips}</ThemedText>
                        </ThemedView>
                      )}
                    </ThemedView>
                  </ThemedView>
                ))}
              </ThemedView>
              
              {/* Safety Tips */}
              {selectedProject.safety_tips && selectedProject.safety_tips.length > 0 && (
                <ThemedView style={styles.projectDetailSection}>
                  <ThemedText style={styles.projectDetailSectionTitle}>Overall Safety Tips</ThemedText>
                  {selectedProject.safety_tips.map((tip, index) => (
                    <ThemedView key={index} style={styles.safetyTipItem}>
                      <IconSymbol name="exclamationmark.triangle" size={16} color="#FF9800" />
                      <ThemedText style={styles.safetyTipItemText}>{tip}</ThemedText>
                    </ThemedView>
                  ))}
                </ThemedView>
              )}
              
              {/* Tutorial Sources */}
              {projectResults?.projects.tutorial_sources && projectResults.projects.tutorial_sources.length > 0 && (
                <ThemedView style={styles.projectDetailSection}>
                  <ThemedText style={styles.projectDetailSectionTitle}>Additional Resources</ThemedText>
                  {projectResults.projects.tutorial_sources.map((source, index) => (
                    <TouchableOpacity 
                      key={index} 
                      style={styles.tutorialSourceItem}
                      onPress={() => {
                        // Open URL in browser or WebView
                      }}
                    >
                      <ThemedText style={styles.tutorialSourceTitle}>{source.title}</ThemedText>
                      <ThemedText style={styles.tutorialSourceType}>{source.type}</ThemedText>
                    </TouchableOpacity>
                  ))}
                </ThemedView>
              )}
            </ScrollView>
          </ThemedView>
        </ThemedView>
      </Modal>
    );
  };

  return (
    <GreenScreenWrapper>
      <ScrollView style={styles.container}>
        <ThemedText type="title" style={styles.title}>DIY Waste Upcycling</ThemedText>
        <ThemedText style={styles.subtitle}>
          Transform your waste into creative and useful DIY projects
        </ThemedText>
        
        {/* Image Upload Section */}
        <ThemedView style={styles.uploadSection}>
          <ThemedText style={styles.sectionTitle}>Upload Waste Product Photos</ThemedText>
          
          <ThemedView style={styles.uploadButtons}>
            <TouchableOpacity style={styles.uploadButton} onPress={takePhoto}>
              <IconSymbol name="camera.fill" size={24} color={Colors.light.primary} />
              <ThemedText style={styles.uploadButtonText}>Take Photo</ThemedText>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.uploadButton} onPress={pickImages}>
              <IconSymbol name="photo.fill" size={24} color={Colors.light.primary} />
              <ThemedText style={styles.uploadButtonText}>Pick from Gallery</ThemedText>
            </TouchableOpacity>
          </ThemedView>
          
          {/* Thumbnails */}
          {images.length > 0 && (
            <ThemedView style={styles.thumbnailsContainer}>
              <ThemedText style={styles.thumbnailsTitle}>
                Selected Images ({images.length}) {images.length > 1 && '- Only the first image will be processed'}
              </ThemedText>
              <ScrollView horizontal={true} showsHorizontalScrollIndicator={false}>
                <ThemedView style={styles.thumbnailsRow}>
                  {images.map((image, index) => (
                    <ThemedView key={index} style={styles.thumbnailWrapper}>
                      <Image source={{ uri: image.uri }} style={styles.thumbnail} />
                      <TouchableOpacity 
                        style={styles.removeThumbnailButton}
                        onPress={() => removeImage(index)}
                      >
                        <ThemedText style={styles.removeThumbnailButtonText}>×</ThemedText>
                      </TouchableOpacity>
                    </ThemedView>
                  ))}
                </ThemedView>
              </ScrollView>
            </ThemedView>
          )}
          
          {/* Process Button */}
          <TouchableOpacity 
            style={[
              styles.processButton,
              (images.length === 0 || isProcessing) && styles.disabledButton
            ]}
            onPress={processImages}
            disabled={images.length === 0 || isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <IconSymbol name="wand.and.stars" size={20} color="white" />
                <ThemedText style={styles.processButtonText}>
                  Generate DIY Projects
                </ThemedText>
              </>
            )}
          </TouchableOpacity>
        </ThemedView>
        
        {/* Results Section */}
        {renderDifficultySelector()}
        {renderProjectPreview()}
        
        {/* No Results Message */}
        {images.length > 0 && !isProcessing && !projectResults && (
          <ThemedView style={styles.noResultsContainer}>
            <IconSymbol name="arrow.up" size={32} color={Colors.light.primary} />
            <ThemedText style={styles.noResultsText}>
              Click the button above to generate DIY project ideas for your waste items
            </ThemedText>
          </ThemedView>
        )}
        
        {/* Project Details Modal */}
        {renderProjectDetailsModal()}
      </ScrollView>
    </GreenScreenWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 8,
    color: Colors.light.primary,
    textAlign: 'center',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 24,
    color: '#666',
  },
  uploadSection: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginBottom: 16,
  },
  uploadButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  uploadButton: {
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
    width: '45%',
  },
  uploadButtonText: {
    marginLeft: 8,
    fontWeight: '600',
    color: Colors.light.primary,
  },
  thumbnailsContainer: {
    marginBottom: 16,
  },
  thumbnailsTitle: {
    marginBottom: 8,
    fontWeight: '600',
  },
  thumbnailsRow: {
    flexDirection: 'row',
    flexWrap: 'nowrap',
  },
  thumbnailWrapper: {
    position: 'relative',
    margin: 4,
  },
  thumbnail: {
    width: 80,
    height: 80,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  removeThumbnailButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeThumbnailButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  processButton: {
    backgroundColor: Colors.light.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    marginTop: 8,
  },
  processButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  noResultsContainer: {
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
  },
  noResultsText: {
    textAlign: 'center',
    marginTop: 16,
    color: '#666',
  },
  difficultySelector: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  difficultyButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  difficultyButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 2,
    marginHorizontal: 4,
    backgroundColor: 'white',
  },
  difficultyButtonSelected: {
    backgroundColor: Colors.light.primary,
  },
  difficultyButtonText: {
    fontWeight: 'bold',
  },
  difficultyButtonTextSelected: {
    color: 'white',
  },
  projectPreview: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  projectCard: {
    backgroundColor: 'white',
    borderRadius: 8,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
  },
  projectName: {
    fontSize: 18,
    fontWeight: 'bold',
    padding: 16,
    backgroundColor: Colors.light.primary,
    color: 'white',
  },
  projectImageContainer: {
    height: 180,
    backgroundColor: '#eee',
  },
  projectImage: {
    width: '100%',
    height: '100%',
  },
  noImagePlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  projectInfo: {
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  infoText: {
    marginLeft: 8,
  },
  viewDetailsButton: {
    backgroundColor: Colors.light.primary,
    padding: 12,
    alignItems: 'center',
  },
  viewDetailsButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    width: '90%',
    maxHeight: '90%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: Colors.light.primary,
    flex: 1,
  },
  closeButton: {
    padding: 4,
  },
  modalScrollView: {
    maxHeight: '80%',
  },
  modalProjectImage: {
    width: '100%',
    height: 200,
  },
  projectDetailSection: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  projectDetailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  difficultyBadge: {
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 16,
  },
  difficultyBadgeText: {
    color: 'white',
    fontWeight: 'bold',
  },
  estimatedTime: {
    fontWeight: '600',
  },
  projectDetailSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    color: Colors.light.primary,
  },
  materialItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  materialName: {
    flex: 3,
  },
  materialQuantity: {
    flex: 1,
    textAlign: 'right',
    fontWeight: '600',
  },
  stepItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  stepNumberContainer: {
    backgroundColor: Colors.light.primary,
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  stepNumber: {
    color: 'white',
    fontWeight: 'bold',
  },
  stepContent: {
    flex: 1,
  },
  stepDescription: {
    marginBottom: 8,
  },
  stepTime: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  safetyTipContainer: {
    backgroundColor: '#FFF8E1',
    padding: 8,
    borderRadius: 4,
    borderLeftWidth: 3,
    borderLeftColor: '#FF9800',
  },
  safetyTipTitle: {
    fontWeight: 'bold',
    color: '#FF9800',
    marginBottom: 4,
  },
  safetyTipText: {
    fontSize: 12,
  },
  safetyTipItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    backgroundColor: '#FFF8E1',
    padding: 8,
    borderRadius: 4,
  },
  safetyTipItemText: {
    marginLeft: 8,
    flex: 1,
  },
  tutorialSourceItem: {
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 4,
    marginBottom: 8,
  },
  tutorialSourceTitle: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  tutorialSourceType: {
    fontSize: 12,
    color: '#666',
  },
});
