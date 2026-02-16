/**
 * Types for mockup components that use extracted user preferences.
 */

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  accentSoft: string;
  background: string;
}

export interface Typography {
  heading: string;
  body: string;
  style: string;
}

export interface MockupProps {
  colors: ColorPalette;
  typography: Typography;
  sessionName?: string;
  componentStyles?: Record<string, Record<string, string>>;
}

export type MockupType = 'landing' | 'dashboard' | 'form' | 'settings';
