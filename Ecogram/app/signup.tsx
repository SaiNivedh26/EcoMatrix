// app/signup.tsx
import { View, TextInput, StyleSheet, Text, TouchableOpacity, Image, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useState } from "react";
import { useRouter } from "expo-router";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";

export default function SignUp() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSignUp = () => {
    // Simple validation
    if (!name || !email || !password || !confirmPassword) {
      alert("Please fill in all fields");
      return;
    }
    
    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    
    setIsLoading(true);
    
    // Simulate sign up process
    setTimeout(() => {
      setIsLoading(false);
      router.replace("/(tabs)");
    }, 1500);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1 }}
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
        <ThemedView style={styles.container}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          
          <View style={styles.logoContainer}>
            <Image
              source={require('@/assets/images/icon.png')}
              style={styles.logo}
            />
          </View>
          
          <ThemedText type="title" style={styles.title}>Create Account</ThemedText>
          <ThemedText style={styles.subtitle}>Join EcoMatrix today</ThemedText>
          
          <View style={styles.formContainer}>
            <TextInput
              placeholder="Full Name"
              style={styles.input}
              value={name}
              onChangeText={setName}
              placeholderTextColor="#999"
            />
            
            <TextInput
              placeholder="Email"
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
              placeholderTextColor="#999"
            />
            
            <TextInput
              placeholder="Password"
              style={styles.input}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
              placeholderTextColor="#999"
            />
            
            <TextInput
              placeholder="Confirm Password"
              style={styles.input}
              secureTextEntry
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              placeholderTextColor="#999"
            />
            
            <TouchableOpacity
              style={[styles.signupButton, isLoading && styles.signupButtonDisabled]}
              onPress={handleSignUp}
              disabled={isLoading}
            >
              <Text style={styles.signupButtonText}>
                {isLoading ? "Creating Account..." : "Sign Up"}
              </Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.loginContainer}>
            <ThemedText>Already have an account? </ThemedText>
            <TouchableOpacity onPress={() => router.push("/login")}>
              <ThemedText style={styles.loginText}>Login</ThemedText>
            </TouchableOpacity>
          </View>
        </ThemedView>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    padding: 20,
    justifyContent: "center",
  },
  backButton: {
    position: "absolute",
    top: 50,
    left: 20,
    zIndex: 10,
  },
  backButtonText: {
    fontSize: 16,
    color: "#4CAF50",
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 30,
  },
  logo: {
    width: 80,
    height: 80,
  },
  title: { 
    fontSize: 28, 
    fontWeight: "bold", 
    marginBottom: 10, 
    textAlign: "center" 
  },
  subtitle: {
    textAlign: "center",
    marginBottom: 30,
    fontSize: 16,
  },
  formContainer: {
    width: "100%",
    maxWidth: 400,
    alignSelf: "center",
  },
  input: { 
    borderWidth: 1, 
    borderColor: "#ccc",
    padding: 15, 
    marginBottom: 16, 
    borderRadius: 10,
    fontSize: 16,
  },
  signupButton: {
    backgroundColor: "#4CAF50",
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  signupButtonDisabled: {
    backgroundColor: "#A5D6A7",
  },
  signupButtonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "bold",
  },
  loginContainer: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 30,
  },
  loginText: {
    color: "#4CAF50",
    fontWeight: "bold",
  }
});
