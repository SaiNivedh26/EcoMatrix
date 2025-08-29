/**
 * EcoMatrix green theme color hook
 */

import { Colors } from '@/constants/Colors';

export function useThemeColor(
  props: { light?: string; dark?: string },
  colorName: keyof typeof Colors.light
) {
  const theme = 'light'; // Always use light theme
  const colorFromProps = props[theme];

  if (colorFromProps) {
    return colorFromProps;
  } else {
    return Colors[theme][colorName];
  }
}
