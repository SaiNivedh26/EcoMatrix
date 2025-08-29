import React, { useState } from 'react';
import { StyleSheet, View, TouchableOpacity, Image, Modal, Dimensions } from 'react-native';
import { router } from 'expo-router';

import { GreenScreenWrapper } from '@/components/GreenScreenWrapper';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import ReportMap from '@/components/ReportMap';
import ReportGallery from '@/components/ReportGallery';
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

export default function MapScreen() {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map');
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  const handleReportPress = (report: Report) => {
    setSelectedReport(report);
    setDetailModalVisible(true);
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const goToReportScreen = () => {
    router.push('/photo');
  };

  return (
    <GreenScreenWrapper>
      <ThemedView style={styles.container}>
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>Environmental Reports</ThemedText>
          <ThemedView style={styles.toggleRow}>
            <TouchableOpacity 
              style={[styles.cornerToggleButton, viewMode === 'map' && styles.activeToggle, {alignSelf: 'flex-start'}]}
              onPress={() => setViewMode('map')}
            >
              <IconSymbol name="map.fill" size={18} color={viewMode === 'map' ? 'white' : Colors.light.primary} />
              <ThemedText style={[styles.toggleText, viewMode === 'map' && styles.activeToggleText]}>Map</ThemedText>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.cornerToggleButton, viewMode === 'list' && styles.activeToggle, {alignSelf: 'flex-end'}]}
              onPress={() => setViewMode('list')}
            >
              <IconSymbol name="list.bullet" size={18} color={viewMode === 'list' ? 'white' : Colors.light.primary} />
              <ThemedText style={[styles.toggleText, viewMode === 'list' && styles.activeToggleText]}>List</ThemedText>
            </TouchableOpacity>
          </ThemedView>
        </ThemedView>

        <ThemedView style={styles.content}>
          {viewMode === 'map' ? (
            <ReportMap onMarkerPress={handleReportPress} />
          ) : (
            <ReportGallery onPressReport={handleReportPress} />
          )}
        </ThemedView>

        <TouchableOpacity 
          style={styles.addButton}
          onPress={goToReportScreen}
        >
          <IconSymbol name="plus" size={24} color="white" />
        </TouchableOpacity>

        {/* Report Detail Modal */}
        <Modal
          visible={detailModalVisible}
          transparent={true}
          animationType="slide"
          onRequestClose={() => setDetailModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              {selectedReport && (
                <>
                  <Image source={{ uri: selectedReport.image }} style={styles.modalImage} />
                  <ThemedView style={styles.modalDetails}>
                    <ThemedText type="subtitle" style={styles.modalIssueType}>
                      {selectedReport.issueType}
                    </ThemedText>
                    <ThemedText style={styles.modalDescription}>
                      {selectedReport.description}
                    </ThemedText>
                    <ThemedText style={styles.modalAddress}>
                      <ThemedText style={{ fontWeight: 'bold' }}>Location: </ThemedText>
                      {selectedReport.location.address}
                    </ThemedText>
                    <ThemedText style={styles.modalTimestamp}>
                      Reported on {formatDate(selectedReport.timestamp)}
                    </ThemedText>
                  </ThemedView>
                  <TouchableOpacity 
                    style={styles.modalCloseButton}
                    onPress={() => setDetailModalVisible(false)}
                  >
                    <ThemedText style={styles.modalCloseButtonText}>Close</ThemedText>
                  </TouchableOpacity>
                </>
              )}
            </View>
          </View>
        </Modal>
      </ThemedView>
    </GreenScreenWrapper>
  );
}

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 8,
  },
  cornerToggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.light.primary,
    backgroundColor: 'white',
    minWidth: 90,
    marginHorizontal: 4,
    elevation: 2,
    shadowColor: '#388E3C',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.10,
    shadowRadius: 4,
  },
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    marginTop: 32,
    marginBottom: 16,
    color: Colors.light.primary,
    textAlign: 'center',
  },
  viewToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.light.primary,
    overflow: 'hidden',
  },
  toggleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    width: 100,
  },
  activeToggle: {
    backgroundColor: Colors.light.primary,
  },
  toggleText: {
    marginLeft: 4,
    color: Colors.light.primary,
  },
  activeToggleText: {
    color: 'white',
  },
  content: {
    flex: 1,
  },
  addButton: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: Colors.light.primary,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: width * 0.9,
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
  },
  modalImage: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  modalDetails: {
    padding: 16,
  },
  modalIssueType: {
    color: Colors.light.primary,
    marginBottom: 8,
  },
  modalDescription: {
    fontSize: 16,
    marginBottom: 12,
  },
  modalAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  modalTimestamp: {
    fontSize: 12,
    color: '#999',
  },
  modalCloseButton: {
    padding: 16,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  modalCloseButtonText: {
    color: Colors.light.primary,
    fontWeight: 'bold',
  },
});
