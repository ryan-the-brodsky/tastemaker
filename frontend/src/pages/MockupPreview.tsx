/**
 * MockupPreview page - displays all 4 mockup templates using user's extracted styles.
 * Route: /session/:sessionId/mockups
 */
import { useEffect, useState, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/shadcn/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/shadcn/Card';
import {
  LandingMockup,
  DashboardMockup,
  FormMockup,
  SettingsMockup,
  ColorPalette,
  Typography,
  MockupType,
} from '@/components/mockups';

// Default colors if none extracted
const DEFAULT_COLORS: ColorPalette = {
  primary: '#1a365d',
  secondary: '#115e59',
  accent: '#d97706',
  accentSoft: '#f87171',
  background: '#faf5f0',
};

// Default typography if none extracted
const DEFAULT_TYPOGRAPHY: Typography = {
  heading: 'Inter',
  body: 'Inter',
  style: 'modern-clean',
};

const MOCKUP_TYPES: { type: MockupType; label: string; description: string }[] = [
  { type: 'landing', label: 'Landing Page', description: 'Hero, features, and CTA sections' },
  { type: 'dashboard', label: 'Dashboard', description: 'Navigation, stats, and data tables' },
  { type: 'form', label: 'Form Page', description: 'Multi-step form with inputs and validation' },
  { type: 'settings', label: 'Settings', description: 'Toggles, modals, and notifications' },
];

export default function MockupPreview() {
  const navigate = useNavigate();
  const { sessionId } = useParams<{ sessionId: string }>();
  const { currentSession, selectSession } = useSession();
  const [activeTab, setActiveTab] = useState<MockupType>('landing');
  const [colors, setColors] = useState<ColorPalette>(DEFAULT_COLORS);
  const [typography, setTypography] = useState<Typography>(DEFAULT_TYPOGRAPHY);
  const initialized = useRef(false);

  useEffect(() => {
    if (sessionId && !initialized.current) {
      initialized.current = true;
      selectSession(parseInt(sessionId));
    }
  }, [sessionId, selectSession]);

  useEffect(() => {
    if (currentSession) {
      // Parse chosen_colors from session
      if (currentSession.chosen_colors) {
        const parsed = typeof currentSession.chosen_colors === 'string'
          ? JSON.parse(currentSession.chosen_colors)
          : currentSession.chosen_colors;
        setColors({
          primary: parsed.primary || DEFAULT_COLORS.primary,
          secondary: parsed.secondary || DEFAULT_COLORS.secondary,
          accent: parsed.accent || DEFAULT_COLORS.accent,
          accentSoft: parsed.accentSoft || DEFAULT_COLORS.accentSoft,
          background: parsed.background || DEFAULT_COLORS.background,
        });
      }

      // Parse chosen_typography from session
      if (currentSession.chosen_typography) {
        const parsed = typeof currentSession.chosen_typography === 'string'
          ? JSON.parse(currentSession.chosen_typography)
          : currentSession.chosen_typography;
        setTypography({
          heading: parsed.heading || DEFAULT_TYPOGRAPHY.heading,
          body: parsed.body || DEFAULT_TYPOGRAPHY.body,
          style: parsed.style || DEFAULT_TYPOGRAPHY.style,
        });
      }
    }
  }, [currentSession]);

  const renderMockup = () => {
    const props = { colors, typography, sessionName: currentSession?.name };
    switch (activeTab) {
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

  if (!currentSession) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Loading session...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="font-semibold text-lg" agent-handle="mockup-preview-title">
              Style Mockups: {currentSession.name}
            </h1>
            <p className="text-sm text-gray-500">
              Preview your extracted style applied to real page layouts
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => navigate(`/session/${sessionId}/review`)}
            >
              Back to Review
            </Button>
            <Button
              onClick={() => navigate(`/session/${sessionId}/download`)}
              agent-handle="mockup-proceed-download"
            >
              Proceed to Download
            </Button>
          </div>
        </div>
      </header>

      {/* Style Summary */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-8">
            {/* Color Swatches */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500 mr-2">Colors:</span>
              {Object.entries(colors).map(([key, value]) => (
                <div
                  key={key}
                  className="w-8 h-8 rounded-md shadow-sm border border-gray-200"
                  style={{ backgroundColor: value }}
                  title={`${key}: ${value}`}
                />
              ))}
            </div>
            {/* Typography */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Typography:</span>
              <span className="font-medium" style={{ fontFamily: typography.heading }}>
                {typography.heading}
              </span>
              <span className="text-gray-400">/</span>
              <span style={{ fontFamily: typography.body }}>{typography.body}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1" agent-handle="mockup-tab-navigation">
            {MOCKUP_TYPES.map(({ type, label }) => (
              <button
                key={type}
                onClick={() => setActiveTab(type)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === type
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
                agent-handle={`mockup-tab-${type}`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Mockup Display */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Card className="overflow-hidden">
          <CardHeader className="bg-gray-50 border-b">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {MOCKUP_TYPES.find((m) => m.type === activeTab)?.label}
                </CardTitle>
                <CardDescription>
                  {MOCKUP_TYPES.find((m) => m.type === activeTab)?.description}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span className="w-3 h-3 rounded-full bg-red-400" />
                <span className="w-3 h-3 rounded-full bg-yellow-400" />
                <span className="w-3 h-3 rounded-full bg-green-400" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div
              className="border rounded-b-lg overflow-hidden"
              style={{ maxHeight: '800px', overflowY: 'auto' }}
              agent-handle={`mockup-content-${activeTab}`}
            >
              {renderMockup()}
            </div>
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">About These Mockups</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              These mockups demonstrate how your extracted style preferences would look
              when applied to common page layouts. The colors, typography, and spacing
              are all derived from your A/B comparison choices.
            </p>
            <p className="text-gray-600">
              When you download your skill package, AI coding tools will use these
              same rules to generate consistent, on-brand components for your projects.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
