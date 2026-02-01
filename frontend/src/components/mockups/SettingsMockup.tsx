/**
 * Settings mockup using extracted user preferences.
 * Demonstrates modals, toggles, cards, and feedback notifications.
 */
import { MockupProps } from './types';

export default function SettingsMockup({ colors, typography }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  const settingSections = [
    {
      title: 'Profile',
      items: [
        { label: 'Display Name', value: 'Alex Johnson', type: 'text' },
        { label: 'Email', value: 'alex@example.com', type: 'text' },
        { label: 'Avatar', value: '', type: 'avatar' },
      ],
    },
    {
      title: 'Notifications',
      items: [
        { label: 'Email notifications', value: true, type: 'toggle' },
        { label: 'Push notifications', value: false, type: 'toggle' },
        { label: 'Weekly digest', value: true, type: 'toggle' },
      ],
    },
    {
      title: 'Privacy',
      items: [
        { label: 'Profile visibility', value: 'Public', type: 'select' },
        { label: 'Show activity status', value: true, type: 'toggle' },
      ],
    },
  ];

  return (
    <div
      className="w-full min-h-[800px] relative"
      style={{ backgroundColor: colors.background, fontFamily: bodyFont }}
    >
      {/* Header */}
      <header
        className="px-8 py-4 shadow-sm"
        style={{
          backgroundColor: colors.background,
          borderBottom: `1px solid ${colors.primary}15`,
        }}
      >
        <div className="max-w-4xl mx-auto">
          <h1
            className="text-2xl font-bold"
            style={{ color: colors.primary, fontFamily: headingFont }}
          >
            Settings
          </h1>
        </div>
      </header>

      {/* Success Toast */}
      <div className="absolute top-4 right-4 z-10">
        <div
          className="px-4 py-3 rounded-lg shadow-lg flex items-center gap-3"
          style={{
            backgroundColor: colors.accent,
            color: colors.background,
          }}
        >
          <span>✓</span>
          <span className="font-medium">Settings saved successfully!</span>
        </div>
      </div>

      {/* Main Content */}
      <main className="px-8 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Settings Sections */}
          <div className="space-y-6">
            {settingSections.map((section) => (
              <div
                key={section.title}
                className="rounded-xl shadow-sm overflow-hidden"
                style={{
                  backgroundColor: colors.background,
                  border: `1px solid ${colors.primary}15`,
                }}
              >
                <div
                  className="px-6 py-4 border-b"
                  style={{ borderColor: `${colors.primary}15` }}
                >
                  <h2
                    className="font-semibold"
                    style={{ color: colors.primary, fontFamily: headingFont }}
                  >
                    {section.title}
                  </h2>
                </div>
                <div className="divide-y" style={{ borderColor: `${colors.primary}10` }}>
                  {section.items.map((item, i) => (
                    <div
                      key={i}
                      className="px-6 py-4 flex items-center justify-between"
                    >
                      <span style={{ color: colors.secondary }}>{item.label}</span>
                      {item.type === 'text' && (
                        <span style={{ color: colors.primary }} className="font-medium">
                          {item.value as string}
                        </span>
                      )}
                      {item.type === 'toggle' && (
                        <div
                          className="w-12 h-7 rounded-full p-1 cursor-pointer transition-all"
                          style={{
                            backgroundColor: item.value
                              ? colors.accent
                              : `${colors.primary}30`,
                          }}
                        >
                          <div
                            className="w-5 h-5 rounded-full transition-all"
                            style={{
                              backgroundColor: colors.background,
                              transform: item.value
                                ? 'translateX(20px)'
                                : 'translateX(0)',
                            }}
                          />
                        </div>
                      )}
                      {item.type === 'select' && (
                        <select
                          className="px-3 py-1 rounded-lg outline-none cursor-pointer"
                          defaultValue={item.value as string}
                          style={{
                            backgroundColor: `${colors.primary}10`,
                            color: colors.primary,
                            border: 'none',
                          }}
                        >
                          <option>Public</option>
                          <option>Private</option>
                          <option>Friends Only</option>
                        </select>
                      )}
                      {item.type === 'avatar' && (
                        <div
                          className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg"
                          style={{
                            backgroundColor: colors.primary,
                            color: colors.background,
                          }}
                        >
                          AJ
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Danger Zone */}
          <div
            className="mt-8 rounded-xl overflow-hidden"
            style={{
              border: `1px solid ${colors.accentSoft}50`,
            }}
          >
            <div
              className="px-6 py-4 border-b"
              style={{
                backgroundColor: `${colors.accentSoft}10`,
                borderColor: `${colors.accentSoft}30`,
              }}
            >
              <h2
                className="font-semibold"
                style={{ color: colors.accentSoft, fontFamily: headingFont }}
              >
                Danger Zone
              </h2>
            </div>
            <div className="p-6 flex items-center justify-between">
              <div>
                <p style={{ color: colors.primary }} className="font-medium">
                  Delete Account
                </p>
                <p className="text-sm" style={{ color: colors.secondary }}>
                  Permanently remove your account and all data
                </p>
              </div>
              <button
                className="px-4 py-2 rounded-lg font-medium"
                style={{
                  backgroundColor: `${colors.accentSoft}20`,
                  color: colors.accentSoft,
                  border: `1px solid ${colors.accentSoft}`,
                }}
              >
                Delete Account
              </button>
            </div>
          </div>

          {/* Modal Preview (positioned in document) */}
          <div
            className="mt-8 p-8 rounded-xl"
            style={{
              backgroundColor: `${colors.primary}10`,
              border: `2px dashed ${colors.primary}30`,
            }}
          >
            <p
              className="text-sm text-center mb-4"
              style={{ color: colors.secondary }}
            >
              Modal Preview
            </p>
            <div
              className="rounded-xl shadow-2xl max-w-md mx-auto overflow-hidden"
              style={{ backgroundColor: colors.background }}
            >
              <div
                className="px-6 py-4 border-b flex items-center justify-between"
                style={{ borderColor: `${colors.primary}15` }}
              >
                <h3
                  className="font-semibold"
                  style={{ color: colors.primary, fontFamily: headingFont }}
                >
                  Confirm Changes
                </h3>
                <button
                  className="text-2xl leading-none"
                  style={{ color: colors.secondary }}
                >
                  ×
                </button>
              </div>
              <div className="px-6 py-6">
                <p style={{ color: colors.secondary }}>
                  Are you sure you want to save these changes? This action cannot be
                  undone.
                </p>
              </div>
              <div
                className="px-6 py-4 flex justify-end gap-3 border-t"
                style={{
                  borderColor: `${colors.primary}15`,
                  backgroundColor: `${colors.primary}05`,
                }}
              >
                <button
                  className="px-4 py-2 rounded-lg font-medium"
                  style={{
                    backgroundColor: 'transparent',
                    color: colors.secondary,
                    border: `1px solid ${colors.secondary}40`,
                  }}
                >
                  Cancel
                </button>
                <button
                  className="px-4 py-2 rounded-lg font-medium"
                  style={{
                    backgroundColor: colors.primary,
                    color: colors.background,
                  }}
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
