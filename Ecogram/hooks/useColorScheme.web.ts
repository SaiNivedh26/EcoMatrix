/**
 * Custom hook that always returns 'light' for the EcoMatrix green and white theme
 * This is the web version, but behavior is the same as the native version
 */
export function useColorScheme(): 'light' {
  // Always return 'light' regardless of system theme
  return 'light';
}
