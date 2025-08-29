// app/login.tsx
import { View, TextInput, StyleSheet, Text, TouchableOpacity, Image, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useState } from "react";
import { useRouter } from "expo-router";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = () => {
    if (!email || !password) {
      // Simple validation
      alert("Please enter both email and password");
      return;
    }
    
    setIsLoading(true);
    
    // Simulate a login process
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
          
          <ThemedText type="title" style={styles.title}>Welcome Back</ThemedText>
          <ThemedText style={styles.subtitle}>Sign in to continue</ThemedText>
          
          <View style={styles.formContainer}>
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
            
            <TouchableOpacity style={styles.forgotPassword}>
              <ThemedText style={styles.forgotPasswordText}>Forgot Password?</ThemedText>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <Text style={styles.loginButtonText}>
                {isLoading ? "Logging in..." : "Login"}
              </Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.signupContainer}>
            <ThemedText>Don&apos;t have an account? </ThemedText>
            <TouchableOpacity onPress={() => router.push("/signup")}>
              <ThemedText style={styles.signupText}>Sign Up</ThemedText>
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
  forgotPassword: {
    alignSelf: "flex-end",
    marginBottom: 20,
  },
  forgotPasswordText: {
    color: "#4CAF50",
  },
  loginButton: {
    backgroundColor: "#4CAF50",
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  loginButtonDisabled: {
    backgroundColor: "#A5D6A7",
  },
  loginButtonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "bold",
  },
  signupContainer: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 30,
  },
  signupText: {
    color: "#4CAF50",
    fontWeight: "bold",
  }
});
