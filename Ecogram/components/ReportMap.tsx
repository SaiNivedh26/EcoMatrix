import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Dimensions, TouchableOpacity } from 'react-native';
import MapView, { Marker, Callout } from 'react-native-maps';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';

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

interface ReportMapProps {
  onMarkerPress?: (report: Report) => void;
}

const ReportMap: React.FC<ReportMapProps> = ({ onMarkerPress }) => {
  const [reports, setReports] = useState<Report[]>([]);
  const [initialRegion, setInitialRegion] = useState({
    latitude: 37.78825,
    longitude: -122.4324,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load reports and set initial map region
    const setup = async () => {
      try {
        // Get current location
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const currentLocation = await Location.getCurrentPositionAsync({});
          setInitialRegion({
            latitude: currentLocation.coords.latitude,
            longitude: currentLocation.coords.longitude,
            latitudeDelta: 0.0922,
            longitudeDelta: 0.0421,
          });
        }

        // Load reports
        const reportsJson = await AsyncStorage.getItem('environmentalReports');
        if (reportsJson) {
          const parsedReports: Report[] = JSON.parse(reportsJson);
          setReports(parsedReports);
        }
      } catch (error) {
        console.error('Error setting up map:', error);
      } finally {
        setLoading(false);
      }
    };

    setup();
  }, []);

  // Format date for display
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ThemedText>Loading map...</ThemedText>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <MapView 
        style={styles.map}
        initialRegion={initialRegion}
        showsUserLocation={true}
        showsMyLocationButton={true}
      >
        {reports.map((report) => (
          <Marker
            key={report.id}
            coordinate={{
              latitude: report.location.latitude,
              longitude: report.location.longitude,
            }}
            pinColor={getPinColorByIssueType(report.issueType)}
            onPress={() => onMarkerPress && onMarkerPress(report)}
          >
            <Callout tooltip>
              <View style={styles.calloutContainer}>
                <ThemedText style={styles.calloutTitle}>{report.issueType}</ThemedText>
                <ThemedText style={styles.calloutDescription} numberOfLines={2}>
                  {report.description}
                </ThemedText>
                <ThemedText style={styles.calloutDate}>{formatDate(report.timestamp)}</ThemedText>
              </View>
            </Callout>
          </Marker>
        ))}
      </MapView>
      
      {reports.length === 0 && (
        <View style={styles.noReportsOverlay}>
          <ThemedText style={styles.noReportsText}>No environmental reports yet</ThemedText>
          <TouchableOpacity style={styles.reportButton}>
            <ThemedText style={styles.reportButtonText}>Report an Issue</ThemedText>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

// Get pin color based on issue type
const getPinColorByIssueType = (issueType: string): string => {
  switch (issueType) {
    case 'Pollution':
      return 'red';
    case 'Deforestation':
      return 'brown';
    case 'Waste':
      return 'orange';
    case 'Wildlife':
      return 'blue';
    default:
      return 'green';
  }
};

const { width, height } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  map: {
    width,
    height,
  },
  calloutContainer: {
    width: 200,
    padding: 10,
    backgroundColor: 'white',
    borderRadius: 8,
    borderColor: Colors.light.primary,
    borderWidth: 1,
  },
  calloutTitle: {
    fontWeight: 'bold',
    color: Colors.light.primary,
    marginBottom: 4,
  },
  calloutDescription: {
    fontSize: 12,
    marginBottom: 4,
  },
  calloutDate: {
    fontSize: 10,
    color: '#666',
  },
  noReportsOverlay: {
    position: 'absolute',
    top: 20,
    alignSelf: 'center',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
    alignItems: 'center',
  },
  noReportsText: {
    marginBottom: 12,
    fontWeight: 'bold',
  },
  reportButton: {
    backgroundColor: Colors.light.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 4,
  },
  reportButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});

export default ReportMap;
