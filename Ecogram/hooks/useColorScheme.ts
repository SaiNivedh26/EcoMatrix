/**
 * Custom hook that always returns 'light' for the EcoMatrix green and white theme
 * Ignores system color scheme
 */
export function useColorScheme(): 'light' {
  // Always return 'light' regardless of system theme
  return 'light';
}
