/**
 * EcoMatrix Color Theme - Greenish and White
 */

// Main tint/accent color (green)
const primaryGreen = '#4CAF50';
const secondaryGreen = '#388E3C';
const lightGreen = '#A5D6A7';
const successGreen = '#43A047';
const errorRed = '#E53935';
const warningYellow = '#FFC107';

export const Colors = {
  light: {
    text: '#2E3A2F', // Dark green-gray for text
    background: '#FFFFFF', // White background
    tint: primaryGreen, // Primary green as tint color
    icon: '#6B9E76', // Medium green for icons
    tabIconDefault: '#A8BFA6', // Light gray-green for inactive tabs
    tabIconSelected: primaryGreen, // Primary green for selected tabs
    border: '#E8F5E9', // Very light green for borders
    card: '#FFFFFF', // White for cards
    placeholder: '#A8BFA6', // Light gray-green for placeholders
    shadow: 'rgba(0, 0, 0, 0.1)', // Light shadow
    primary: primaryGreen,
    secondary: secondaryGreen,
    success: successGreen,
    error: errorRed,
    warning: warningYellow,
    lightGreen: lightGreen,
  },
  // Maintain the same structure for dark mode, but we'll only use light mode
  dark: {
    text: '#2E3A2F',
    background: '#FFFFFF',
    tint: primaryGreen,
    icon: '#6B9E76',
    tabIconDefault: '#A8BFA6',
    tabIconSelected: primaryGreen,
    border: '#E8F5E9',
    card: '#FFFFFF',
    placeholder: '#A8BFA6',
    shadow: 'rgba(0, 0, 0, 0.1)',
    primary: primaryGreen,
    secondary: secondaryGreen,
    success: successGreen,
    error: errorRed,
    warning: warningYellow,
    lightGreen: lightGreen,
  },
};
