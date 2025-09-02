# ZenGlow Mobile

A beautiful React Native mobile application for ZenGlow AI, built with Expo and
featuring custom button components.

## Features

- **Custom Button Component**: Beautiful, customizable buttons with multiple
  variants (primary, secondary, outline, gradient)
- **Chat Interface**: AI chat with real-time messaging and typing indicators
- **JustJarvis Control Center**: AI model management with system metrics and
  live updates
- **Model Router**: Swipeable model selection with audio controls
- **Dark Theme**: Professional dark theme with gradient accents
- **Haptic Feedback**: Tactile feedback for button interactions

## Setup

1. **Install dependencies:**

   ```bash
   cd frontend/mobile
   npm install
   ```

2. **Start the development server:**

   ```bash
   npm start
   ```

3. **Run on device/emulator:**
   - For iOS: `npm run ios`
   - For Android: `npm run android`
   - For Web: `npm run web`

## Custom Button Component

The app features a highly customizable `CustomButton` component that you can use
throughout your React Native applications:

```tsx
import CustomButton from './src/components/CustomButton';

// Basic usage
<CustomButton
  title="Press Me"
  onPress={() => console.log('Pressed!')}
/>

// With different variants
<CustomButton
  title="Primary Button"
  onPress={handlePress}
  variant="primary"
/>

<CustomButton
  title="Gradient Button"
  onPress={handlePress}
  variant="gradient"
/>

// With loading state
<CustomButton
  title="Submit"
  onPress={handleSubmit}
  loading={isLoading}
  variant="gradient"
/>

// With custom styling
<CustomButton
  title="Custom Styled"
  onPress={handlePress}
  style={{ margin: 10 }}
  textStyle={{ fontSize: 18 }}
/>
```

### Button Props

- `title`: The button text
- `onPress`: Function called when pressed
- `variant`: 'primary' | 'secondary' | 'outline' | 'gradient'
- `size`: 'small' | 'medium' | 'large'
- `loading`: Shows loading spinner
- `disabled`: Disables interactions
- `style`: Custom container styles
- `textStyle`: Custom text styles
- `accessibilityLabel`: Accessibility label

## Project Structure

```
frontend/mobile/
├── src/
│   ├── components/
│   │   ├── CustomButton.tsx      # Reusable button component
│   │   └── CustomTabBar.tsx      # Bottom navigation
│   └── screens/
│       ├── ChatScreen.tsx        # AI chat interface
│       ├── JarvisScreen.tsx      # AI control center
│       └── ModelRouterScreen.tsx # Model selection
├── App.tsx                       # Main app component
├── app.json                      # Expo configuration
└── package.json                  # Dependencies
```

## Key Features

### CustomButton Component

- Multiple variants: primary, secondary, outline, gradient
- Loading states with ActivityIndicator
- Haptic feedback on press
- Accessibility support
- Customizable styling

### Navigation

- Bottom tab navigation with custom styling
- Smooth transitions between screens
- Active state indicators

### UI Components

- Linear gradients for modern look
- Consistent dark theme
- Responsive design
- Professional typography

## Technologies Used

- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and tools
- **TypeScript**: Type-safe development
- **React Navigation**: Navigation between screens
- **Expo Linear Gradient**: Beautiful gradient backgrounds
- **Expo Haptics**: Tactile feedback
- **Expo Vector Icons**: Consistent icon library

## Building for Production

```bash
# Build for production
npm run build

# Build for specific platforms
expo build:ios
expo build:android
```

## Inspiration for Custom Buttons

As mentioned in the React Native documentation, when the default Button
component doesn't meet your needs, you can build your own using Pressable. This
implementation demonstrates:

- Custom styling with gradients
- Loading states
- Accessibility features
- Haptic feedback
- Multiple variants for different use cases
- TypeScript support for better development experience

The CustomButton component serves as a perfect example of how to create
beautiful, accessible, and highly customizable button components for React
Native applications.
