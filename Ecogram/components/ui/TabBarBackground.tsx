// This is a shim for web and Android where the tab bar is generally opaque.
// For our app, we'll use white background in our green and white theme
import { View } from 'react-native';

export default function TabBarBackground() {
  return <View style={{ flex: 1, backgroundColor: '#ffffff' }} />;
}

export function useBottomTabOverflow() {
  return 0;
}
