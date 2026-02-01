/**
 * Standalone mockup render page - no auth required.
 * Used by Puppeteer to capture mockups as PNGs.
 * Route: /mockup-render/:sessionId/:mockupType
 */
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  LandingMockup,
  DashboardMockup,
  FormMockup,
  SettingsMockup,
  ColorPalette,
  Typography,
  MockupType,
} from '@/components/mockups';

// Default colors if none provided
const DEFAULT_COLORS: ColorPalette = {
  primary: '#1a365d',
  secondary: '#115e59',
  accent: '#d97706',
  accentSoft: '#f87171',
  background: '#faf5f0',
};

const DEFAULT_TYPOGRAPHY: Typography = {
  heading: 'Inter',
  body: 'Inter',
  style: 'modern-clean',
};

export default function MockupRender() {
  const { sessionId, mockupType } = useParams<{ sessionId: string; mockupType: string }>();
  const [colors, setColors] = useState<ColorPalette>(DEFAULT_COLORS);
  const [typography, setTypography] = useState<Typography>(DEFAULT_TYPOGRAPHY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessionData = async () => {
      if (!sessionId) {
        setError('No session ID provided');
        setLoading(false);
        return;
      }

      try {
        // Fetch session data without auth (public endpoint for mockup rendering)
        const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/public-style`);

        if (!response.ok) {
          // Use defaults if session not found
          console.warn('Could not fetch session style, using defaults');
          setLoading(false);
          return;
        }

        const data = await response.json();

        if (data.chosen_colors) {
          setColors({
            primary: data.chosen_colors.primary || DEFAULT_COLORS.primary,
            secondary: data.chosen_colors.secondary || DEFAULT_COLORS.secondary,
            accent: data.chosen_colors.accent || DEFAULT_COLORS.accent,
            accentSoft: data.chosen_colors.accentSoft || DEFAULT_COLORS.accentSoft,
            background: data.chosen_colors.background || DEFAULT_COLORS.background,
          });
        }

        if (data.chosen_typography) {
          setTypography({
            heading: data.chosen_typography.heading || DEFAULT_TYPOGRAPHY.heading,
            body: data.chosen_typography.body || DEFAULT_TYPOGRAPHY.body,
            style: data.chosen_typography.style || DEFAULT_TYPOGRAPHY.style,
          });
        }
      } catch (err) {
        console.warn('Error fetching session:', err);
        // Continue with defaults
      } finally {
        setLoading(false);
      }
    };

    fetchSessionData();
  }, [sessionId]);

  const renderMockup = () => {
    const props = { colors, typography };
    const type = mockupType as MockupType;

    switch (type) {
      case 'landing':
        return <LandingMockup {...props} />;
      case 'dashboard':
        return <DashboardMockup {...props} />;
      case 'form':
        return <FormMockup {...props} />;
      case 'settings':
        return <SettingsMockup {...props} />;
      default:
        return <LandingMockup {...props} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  // Render mockup at fixed dimensions for consistent PNG output
  return (
    <div
      id="mockup-container"
      style={{
        width: '1200px',
        minHeight: '800px',
        backgroundColor: colors.background,
      }}
    >
      {renderMockup()}
    </div>
  );
}
