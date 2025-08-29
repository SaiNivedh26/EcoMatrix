// app/index.tsx
import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import { useRouter } from "expo-router";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";

export default function LandingPage() {
  const router = useRouter();

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

      <ThemedText style={styles.footer}>
        © 2025 EcoMatrix Team
      </ThemedText>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
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
