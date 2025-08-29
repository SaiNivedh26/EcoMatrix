import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, Image, ScrollView, TouchableOpacity, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ThemedView } from './ThemedView';
import { ThemedText } from './ThemedText';
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

interface ReportGalleryProps {
  onPressReport?: (report: Report) => void;
}

const ReportGallery: React.FC<ReportGalleryProps> = ({ onPressReport }) => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const reportsJson = await AsyncStorage.getItem('environmentalReports');
      if (reportsJson) {
        const parsedReports: Report[] = JSON.parse(reportsJson);
        // Sort by timestamp, newest first
        parsedReports.sort((a, b) => b.timestamp - a.timestamp);
        setReports(parsedReports);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load reports');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <ThemedView style={styles.loadingContainer}>
        <ThemedText>Loading reports...</ThemedText>
      </ThemedView>
    );
  }

  if (reports.length === 0) {
    return (
      <ThemedView style={styles.emptyContainer}>
        <ThemedText style={styles.emptyText}>No reports yet</ThemedText>
        <ThemedText>Start by reporting an environmental issue</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {reports.map((report) => (
        <TouchableOpacity 
          key={report.id} 
          style={styles.reportCard}
          onPress={() => onPressReport && onPressReport(report)}
        >
          <Image source={{ uri: report.image }} style={styles.reportImage} />
          <View style={styles.reportDetails}>
            <Text style={styles.issueType}>{report.issueType}</Text>
            <Text style={styles.description} numberOfLines={2}>{report.description}</Text>
            <Text style={styles.address} numberOfLines={1}>{report.location.address}</Text>
            <Text style={styles.timestamp}>{formatDate(report.timestamp)}</Text>
          </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: Colors.light.primary,
  },
  reportCard: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    overflow: 'hidden',
  },
  reportImage: {
    width: 100,
    height: 100,
  },
  reportDetails: {
    flex: 1,
    padding: 12,
  },
  issueType: {
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  address: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 10,
    color: '#999',
  },
});

export default ReportGallery;
