import React, { useState, useEffect } from 'react';
import { StyleSheet, TouchableOpacity } from 'react-native';
import MapView, { Marker, Callout } from 'react-native-maps';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import { router } from 'expo-router';

import { ThemedText } from './ThemedText';
import { ThemedView } from './ThemedView';
import { IconSymbol } from './ui/IconSymbol';
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

interface EmbeddedMapProps {
  height?: number;
  onViewFullMap?: () => void;
}

const EmbeddedMap: React.FC<EmbeddedMapProps> = ({ height = 250, onViewFullMap }) => {
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

  const navigateToFullMap = () => {
    if (onViewFullMap) {
      onViewFullMap();
    } else {
      router.push('/(tabs)/map');
    }
  };

  const navigateToReport = () => {
    router.push('/(tabs)/photo');
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

  return (
    <ThemedView style={[styles.container, { height }]}>
      <ThemedView style={styles.mapHeader}>
        <ThemedText type="subtitle" style={styles.mapTitle}>Environmental Issues Map</ThemedText>
        <TouchableOpacity onPress={navigateToFullMap}>
          <ThemedText style={styles.viewFullMap}>View Full Map</ThemedText>
        </TouchableOpacity>
      </ThemedView>
      
      {loading ? (
        <ThemedView style={styles.loadingContainer}>
          <ThemedText>Loading map...</ThemedText>
        </ThemedView>
      ) : (
        <ThemedView style={styles.mapContainer}>
          <MapView 
            style={styles.map}
            initialRegion={initialRegion}
            showsUserLocation={true}
            pitchEnabled={false}
            rotateEnabled={false}
            scrollEnabled={false}
            zoomEnabled={false}
          >
            {reports.map((report) => (
              <Marker
                key={report.id}
                coordinate={{
                  latitude: report.location.latitude,
                  longitude: report.location.longitude,
                }}
                pinColor={getPinColorByIssueType(report.issueType)}
              >
                <Callout tooltip>
                  <ThemedView style={styles.calloutContainer}>
                    <ThemedText style={styles.calloutTitle}>{report.issueType}</ThemedText>
                    <ThemedText style={styles.calloutDescription} numberOfLines={1}>
                      {report.description}
                    </ThemedText>
                  </ThemedView>
                </Callout>
              </Marker>
            ))}
          </MapView>
          
          <TouchableOpacity style={styles.reportButton} onPress={navigateToReport}>
            <IconSymbol name="plus" size={20} color="white" />
            <ThemedText style={styles.reportButtonText}>Report Issue</ThemedText>
          </TouchableOpacity>
        </ThemedView>
      )}
    </ThemedView>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#F5F5F5',
    marginBottom: 16,
  },
  mapHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  mapTitle: {
    fontSize: 16,
    color: Colors.light.primary,
  },
  viewFullMap: {
    color: Colors.light.primary,
    fontWeight: '600',
    fontSize: 14,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mapContainer: {
    flex: 1,
    position: 'relative',
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  calloutContainer: {
    width: 150,
    padding: 8,
    backgroundColor: 'white',
    borderRadius: 8,
    borderColor: Colors.light.primary,
    borderWidth: 1,
  },
  calloutTitle: {
    fontWeight: 'bold',
    color: Colors.light.primary,
    fontSize: 12,
  },
  calloutDescription: {
    fontSize: 10,
  },
  reportButton: {
    position: 'absolute',
    bottom: 10,
    right: 10,
    backgroundColor: Colors.light.primary,
    borderRadius: 20,
    paddingVertical: 6,
    paddingHorizontal: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  reportButtonText: {
    color: 'white',
    marginLeft: 4,
    fontWeight: '600',
    fontSize: 12,
  },
});

export default EmbeddedMap;
