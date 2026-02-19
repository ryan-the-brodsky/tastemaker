/**
 * Full-page mockup review between component groups.
 * Shows a mockup with all component styles applied,
 * a summary of configured components, and navigation actions.
 */
import { Button } from '@/components/ui/shadcn/Button';
import LandingMockup from '@/components/mockups/LandingMockup';
import DashboardMockup from '@/components/mockups/DashboardMockup';
import FormMockup from '@/components/mockups/FormMockup';
import SettingsMockup from '@/components/mockups/SettingsMockup';
import type { CheckpointData } from '@/types';

const COMPONENT_LABELS: Record<string, string> = {
  button: 'Button', input: 'Input', card: 'Card', typography: 'Typography',
  navigation: 'Navigation', form: 'Form', modal: 'Modal', feedback: 'Feedback',
  table: 'Table', badge: 'Badge', tabs: 'Tabs', toggle: 'Toggle',
};

interface MockupCheckpointProps {
  data: CheckpointData;
  sessionName: string;
  onApprove: () => void;
  onGoBack: (componentType: string) => void;
  loading?: boolean;
}

export default function MockupCheckpoint({
  data,
  sessionName,
  onApprove,
  onGoBack,
  loading,
}: MockupCheckpointProps) {
  const colors = data.colors || {};
  const typography = data.typography || {};

  // Build mockup colors in the format mockups expect
  const mockupColors = {
    primary: (colors as Record<string, string>).primary || (colors as { colors?: Record<string, string> }).colors?.primary || '#3b82f6',
    secondary: (colors as Record<string, string>).secondary || (colors as { colors?: Record<string, string> }).colors?.secondary || '#6b7280',
    accent: (colors as Record<string, string>).accent || (colors as { colors?: Record<string, string> }).colors?.accent || '#8b5cf6',
    accentSoft: (colors as Record<string, string>).accentSoft || (colors as { colors?: Record<string, string> }).colors?.accentSoft || '#c4b5fd',
    background: (colors as Record<string, string>).background || (colors as { colors?: Record<string, string> }).colors?.background || '#ffffff',
  };

  const mockupTypo = {
    heading: (typography as Record<string, string>).heading || 'Inter',
    body: (typography as Record<string, string>).body || 'Inter',
    style: (typography as Record<string, string>).style || 'clean',
  };

  const mockupProps = {
    colors: mockupColors,
    typography: mockupTypo,
    sessionName,
    componentStyles: data.component_styles,
  };

  const renderMockup = () => {
    switch (data.mockup_type) {
      case 'landing': return <LandingMockup {...mockupProps} />;
      case 'dashboard': return <DashboardMockup {...mockupProps} />;
      case 'form': return <FormMockup {...mockupProps} />;
      case 'settings': return <SettingsMockup {...mockupProps} />;
      default: return <LandingMockup {...mockupProps} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b py-3 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="font-semibold">{sessionName}</h1>
            <p className="text-sm text-gray-500">{data.label}</p>
          </div>
        </div>
      </header>

      {/* Description */}
      <div className="bg-blue-50 border-b border-blue-100 py-3 px-4">
        <div className="max-w-7xl mx-auto">
          <p className="text-sm text-blue-800">{data.description}</p>
        </div>
      </div>

      {/* Mockup Preview */}
      <main className="flex-1 max-w-5xl mx-auto w-full p-6">
        <div className="bg-white rounded-xl border shadow-sm overflow-hidden mb-6">
          <div className="p-4 border-b bg-gray-50 flex items-center gap-2">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-yellow-400" />
              <div className="w-3 h-3 rounded-full bg-green-400" />
            </div>
            <span className="text-xs text-gray-400 ml-2">
              {data.mockup_type.charAt(0).toUpperCase() + data.mockup_type.slice(1)} Page Preview
            </span>
          </div>
          <div className="overflow-auto" style={{ maxHeight: '600px' }}>
            {renderMockup()}
          </div>
        </div>

        {/* Component Summary */}
        <div className="bg-white rounded-xl border shadow-sm p-6 mb-6">
          <h3 className="font-semibold text-gray-800 mb-3">Components in this group</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {data.components.map(comp => {
              const compStyles = data.component_styles[comp] || {};
              const styleCount = Object.keys(compStyles).length;

              return (
                <div key={comp} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {COMPONENT_LABELS[comp] || comp}
                    </span>
                    <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                      {styleCount} styles
                    </span>
                  </div>
                  <button
                    onClick={() => onGoBack(comp)}
                    className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    Go back & adjust
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t py-4 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Review your component choices and continue when ready
          </div>
          <Button onClick={onApprove} disabled={loading}>
            {loading ? 'Continuing...' : 'Looks good, continue'}
          </Button>
        </div>
      </footer>
    </div>
  );
}
