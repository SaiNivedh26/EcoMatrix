import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { useRouter } from "expo-router";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { Colors } from "@/constants/Colors";

export default function LandingPage() {
  const router = useRouter();
  const [role, setRole] = useState('user');
  return (
    <ThemedView style={styles.container}>
      <View style={styles.logoContainer}>
        <Image
          source={require('@/assets/images/EcoGram_Bharat.png')}
          style={styles.logo}
        />
        <ThemedText type="title" style={styles.appName}>EcoBharat</ThemedText>
      </View>

      <ThemedText style={styles.tagline}>
        Track, Share, and Reduce Your Environmental Footprint
      </ThemedText>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.push("/login")}
        >
          <Text style={styles.buttonText}>Get Started</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.dropdownContainer}>
        <Text style={styles.dropdownLabel}>Login as:</Text>
        <View style={styles.dropdownMenu}>
          <TouchableOpacity
            style={[styles.dropdownOption, role === 'user' && styles.dropdownSelected]}
            onPress={() => setRole('user')}
          >
            <Text style={styles.dropdownText}>User</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.dropdownOption, role === 'vendor' && styles.dropdownSelected]}
            onPress={() => {
              setRole('vendor');
              router.push('/vendor-login');
            }}
          >
            <Text style={styles.dropdownText}>Vendor</Text>
          </TouchableOpacity>
        </View>
  {/* No continue button, immediate redirect for vendor, user uses Get Started */}
  </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  dropdownContainer: {
    marginTop: 24,
    alignItems: 'center',
  },
  dropdownLabel: {
    fontSize: 16,
    marginBottom: 8,
    color: '#333',
    fontWeight: 'bold',
  },
  dropdownMenu: {
    flexDirection: 'row',
    marginBottom: 12,
    gap: 12,
  },
  dropdownOption: {
    backgroundColor: '#F5F5F5',
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ccc',
  },
  dropdownSelected: {
    backgroundColor: Colors.light.primary,
    borderColor: Colors.light.primary,
  },
  dropdownText: {
    color: '#333',
    fontWeight: 'bold',
    fontSize: 16,
  },
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 40,
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 16,
  },
  appName: {
    fontSize: 36,
    fontWeight: "bold",
  },
  tagline: {
    fontSize: 18,
    textAlign: "center",
    marginBottom: 60,
    paddingHorizontal: 20,
  },
  buttonContainer: {
    width: "100%",
    paddingHorizontal: 30,
  },
  button: {
    backgroundColor: "#4CAF50", // Green color for eco theme
    paddingVertical: 15,
    borderRadius: 30,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "bold",
  },
  footer: {
    position: "absolute",
    bottom: 20,
    fontSize: 12,
  }
});
