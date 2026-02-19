/**
 * Settings mockup using extracted user preferences.
 * Demonstrates tabs, toggles, tables, badges, and feedback.
 */
import { useState } from 'react';
import type { CSSProperties } from 'react';
import { MockupProps } from './types';

const TABS = ['Profile', 'Notifications', 'Privacy', 'Danger Zone'] as const;
type TabName = (typeof TABS)[number];

interface ToggleState {
  email: boolean;
  push: boolean;
  weekly: boolean;
  activity: boolean;
}

const TOGGLE_SIZES = {
  small: { trackW: 36, trackH: 20, thumb: 16 },
  medium: { trackW: 44, trackH: 24, thumb: 20 },
  large: { trackW: 56, trackH: 30, thumb: 26 },
} as const;

export default function SettingsMockup({ colors, typography, componentStyles }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  const [activeTab, setActiveTab] = useState<TabName>('Profile');
  const [toggles, setToggles] = useState<ToggleState>({
    email: true,
    push: false,
    weekly: true,
    activity: true,
  });
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const [saved, setSaved] = useState(false);

  // Extract component styles with defaults
  const tableStyles = componentStyles?.table ?? {};
  const tableBorderStyle = tableStyles.tableBorderStyle ?? 'horizontal';
  const rowStriping = tableStyles.rowStriping ?? 'none';
  const tableHeaderStyle = tableStyles.tableHeaderStyle ?? 'bold';
  const cellPadding = tableStyles.cellPadding ?? '12px 16px';

  const badgeStyles = componentStyles?.badge ?? {};
  const badgeStyle = badgeStyles.badgeStyle ?? 'solid';
  const badgeBorderRadius = badgeStyles.borderRadius ?? '9999px';
  const badgePadding = badgeStyles.padding ?? '2px 10px';
  const badgeFontSize = badgeStyles.fontSize ?? '12px';
  const badgeFontWeight = badgeStyles.fontWeight ?? '600';

  const tabStyles = componentStyles?.tabs ?? {};
  const tabStyle = tabStyles.tabStyle ?? 'underline';
  const tabSpacing = tabStyles.tabSpacing ?? '0px';
  const tabIndicatorStyle = tabStyles.tabIndicatorStyle ?? 'thin';
  const tabFontWeight = tabStyles.fontWeight ?? '500';

  const toggleStyles = componentStyles?.toggle ?? {};
  const toggleSize = (toggleStyles.toggleSize ?? 'medium') as keyof typeof TOGGLE_SIZES;
  const toggleLabelPosition = toggleStyles.toggleLabelPosition ?? 'left';
  const toggleBorderRadius = toggleStyles.borderRadius ?? '9999px';

  const buttonStyles = componentStyles?.button ?? {};

  // Toggle size dimensions
  const { trackW, trackH, thumb } = TOGGLE_SIZES[toggleSize] ?? TOGGLE_SIZES.medium;
  const thumbOffset = trackW - thumb - (trackH - thumb);

  // Helpers
  function handleToggle(key: keyof ToggleState) {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function getBadgeColor(type: 'active' | 'pro' | 'verified'): string {
    if (type === 'active') return '#16a34a';
    if (type === 'pro') return colors.accent;
    return colors.primary;
  }

  function buildBadgeStyle(color: string): CSSProperties {
    const base: CSSProperties = {
      display: 'inline-block',
      borderRadius: badgeBorderRadius,
      padding: badgePadding,
      fontSize: badgeFontSize,
      fontWeight: badgeFontWeight,
      lineHeight: '1.4',
    };
    if (badgeStyle === 'outline') {
      return { ...base, color, border: `1.5px solid ${color}`, backgroundColor: 'transparent' };
    }
    if (badgeStyle === 'subtle') {
      return { ...base, color, backgroundColor: `${color}20` };
    }
    // solid
    return { ...base, color: colors.background, backgroundColor: color };
  }

  // Tab bar styles
  function getTabBarStyle(): CSSProperties {
    const base: CSSProperties = {
      display: 'flex',
      gap: tabSpacing,
      borderBottom: tabStyle === 'underline' ? `1px solid ${colors.primary}20` : 'none',
      marginBottom: '24px',
    };
    return base;
  }

  function getTabStyle(tab: TabName): CSSProperties {
    const isActive = activeTab === tab;
    const indicatorWidth = tabIndicatorStyle === 'thick' ? '3px' : '2px';

    const base: CSSProperties = {
      padding: '10px 20px',
      cursor: 'pointer',
      fontWeight: isActive ? tabFontWeight : '400',
      fontFamily: bodyFont,
      fontSize: '14px',
      color: isActive ? colors.primary : colors.secondary,
      backgroundColor: 'transparent',
      border: 'none',
      transition: 'all 0.15s ease',
      position: 'relative',
    };

    if (tabStyle === 'underline') {
      return {
        ...base,
        borderBottom: isActive ? `${indicatorWidth} solid ${colors.primary}` : `${indicatorWidth} solid transparent`,
        marginBottom: '-1px',
        borderRadius: '0',
      };
    }

    if (tabStyle === 'boxed') {
      if (isActive) {
        return {
          ...base,
          backgroundColor: colors.background,
          border: `1px solid ${colors.primary}25`,
          borderBottom: `1px solid ${colors.background}`,
          borderTopLeftRadius: '8px',
          borderTopRightRadius: '8px',
          marginBottom: '-1px',
        };
      }
      return {
        ...base,
        border: '1px solid transparent',
        borderTopLeftRadius: '8px',
        borderTopRightRadius: '8px',
      };
    }

    if (tabStyle === 'pill') {
      return {
        ...base,
        borderRadius: '9999px',
        backgroundColor: isActive ? `${colors.primary}26` : 'transparent',
        fontWeight: isActive ? tabFontWeight : '400',
      };
    }

    return base;
  }

  // Table row style
  function getRowStyle(index: number): CSSProperties {
    const isHovered = hoveredRow === index;
    let bg = 'transparent';
    if (rowStriping === 'even' && index % 2 === 0) bg = `${colors.primary}06`;
    if (rowStriping === 'odd' && index % 2 === 1) bg = `${colors.primary}06`;
    if (isHovered) bg = `${colors.primary}10`;

    const style: CSSProperties = {
      padding: cellPadding,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      backgroundColor: bg,
      transition: 'background-color 0.15s ease',
      cursor: 'default',
    };

    if (tableBorderStyle === 'horizontal') {
      style.borderBottom = `1px solid ${colors.primary}12`;
    } else if (tableBorderStyle === 'full') {
      style.border = `1px solid ${colors.primary}12`;
      if (index > 0) style.borderTop = 'none';
    }

    return style;
  }

  function getTableHeaderStyle(): CSSProperties {
    const style: CSSProperties = {
      padding: cellPadding,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      color: colors.secondary,
      fontSize: '12px',
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
    };

    if (tableHeaderStyle === 'bold') {
      style.fontWeight = '700';
    } else if (tableHeaderStyle === 'shaded') {
      style.backgroundColor = `${colors.primary}08`;
      style.fontWeight = '600';
    } else {
      style.fontWeight = '400';
    }

    if (tableBorderStyle === 'horizontal' || tableBorderStyle === 'full') {
      style.borderBottom = `1px solid ${colors.primary}20`;
    }

    return style;
  }

  // Toggle component
  function renderToggle(key: keyof ToggleState, label: string) {
    const isOn = toggles[key];
    const trackStyle: CSSProperties = {
      width: trackW,
      height: trackH,
      borderRadius: toggleBorderRadius,
      backgroundColor: isOn ? colors.accent : `${colors.primary}30`,
      padding: (trackH - thumb) / 2,
      cursor: 'pointer',
      transition: 'background-color 0.2s ease',
      flexShrink: 0,
      position: 'relative',
    };
    const thumbStyle: CSSProperties = {
      width: thumb,
      height: thumb,
      borderRadius: toggleBorderRadius,
      backgroundColor: colors.background,
      transition: 'transform 0.2s ease',
      transform: isOn ? `translateX(${thumbOffset}px)` : 'translateX(0)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.15)',
    };

    const labelEl = (
      <span style={{ color: colors.secondary, fontSize: '14px' }}>{label}</span>
    );
    const toggleEl = (
      <div style={trackStyle} onClick={() => handleToggle(key)}>
        <div style={thumbStyle} />
      </div>
    );

    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 0',
        }}
      >
        {toggleLabelPosition === 'right' ? (
          <>
            {toggleEl}
            {labelEl}
          </>
        ) : (
          <>
            {labelEl}
            {toggleEl}
          </>
        )}
      </div>
    );
  }

  // Save button style
  function getSaveButtonStyle(): CSSProperties {
    const base: CSSProperties = {
      padding: buttonStyles.padding ?? '10px 24px',
      borderRadius: buttonStyles.borderRadius ?? '8px',
      fontSize: buttonStyles.fontSize ?? '14px',
      fontWeight: buttonStyles.fontWeight ?? '600',
      cursor: 'pointer',
      border: 'none',
      backgroundColor: colors.primary,
      color: colors.background,
      transition: 'opacity 0.15s ease',
      fontFamily: bodyFont,
    };
    return base;
  }

  // Save section at bottom of each tab
  function renderSaveSection() {
    return (
      <div style={{ marginTop: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button style={getSaveButtonStyle()} onClick={handleSave}>
          Save Changes
        </button>
        {saved && (
          <span
            style={{
              color: '#16a34a',
              fontSize: '14px',
              fontWeight: '500',
              animation: 'fadeIn 0.2s ease',
            }}
          >
            Settings saved successfully!
          </span>
        )}
      </div>
    );
  }

  // Profile tab
  const profileRows = [
    { label: 'Name', value: 'Alex Johnson', badge: null },
    { label: 'Email', value: 'alex@example.com', badge: { text: 'Verified', type: 'verified' as const } },
    { label: 'Plan', value: 'Professional', badge: { text: 'Pro', type: 'pro' as const } },
    { label: 'Account', value: 'Since Jan 2024', badge: { text: 'Active', type: 'active' as const } },
  ];

  function renderProfileTab() {
    return (
      <div>
        <div
          style={{
            borderRadius: '12px',
            overflow: 'hidden',
            border: tableBorderStyle === 'full' ? `1px solid ${colors.primary}12` : 'none',
          }}
        >
          <div style={getTableHeaderStyle()}>
            <span style={{ flex: 1 }}>Field</span>
            <span style={{ flex: 2, textAlign: 'left' }}>Value</span>
            <span style={{ width: '100px', textAlign: 'right' }}>Status</span>
          </div>
          {profileRows.map((row, index) => (
            <div
              key={row.label}
              style={getRowStyle(index)}
              onMouseEnter={() => setHoveredRow(index)}
              onMouseLeave={() => setHoveredRow(null)}
            >
              <span style={{ flex: 1, color: colors.secondary, fontSize: '14px' }}>
                {row.label}
              </span>
              <span style={{ flex: 2, color: colors.primary, fontSize: '14px', fontWeight: '500', textAlign: 'left' }}>
                {row.value}
              </span>
              <span style={{ width: '100px', textAlign: 'right' }}>
                {row.badge && (
                  <span style={buildBadgeStyle(getBadgeColor(row.badge.type))}>
                    {row.badge.text}
                  </span>
                )}
              </span>
            </div>
          ))}
        </div>
        {renderSaveSection()}
      </div>
    );
  }

  function renderNotificationsTab() {
    return (
      <div>
        <p style={{ color: colors.secondary, fontSize: '14px', marginBottom: '16px' }}>
          Choose how you want to be notified about updates and activity.
        </p>
        <div
          style={{
            borderRadius: '12px',
            border: `1px solid ${colors.primary}12`,
            padding: '8px 20px',
          }}
        >
          {renderToggle('email', 'Email notifications')}
          <div style={{ borderTop: `1px solid ${colors.primary}10` }} />
          {renderToggle('push', 'Push notifications')}
          <div style={{ borderTop: `1px solid ${colors.primary}10` }} />
          {renderToggle('weekly', 'Weekly digest')}
        </div>
        {renderSaveSection()}
      </div>
    );
  }

  function renderPrivacyTab() {
    return (
      <div>
        <p style={{ color: colors.secondary, fontSize: '14px', marginBottom: '16px' }}>
          Control who can see your profile and activity.
        </p>
        <div
          style={{
            borderRadius: '12px',
            border: `1px solid ${colors.primary}12`,
            padding: '8px 20px',
          }}
        >
          {renderToggle('activity', 'Show activity status')}
          <div style={{ borderTop: `1px solid ${colors.primary}10` }} />
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 0',
            }}
          >
            <span style={{ color: colors.secondary, fontSize: '14px' }}>Profile visibility</span>
            <select
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                backgroundColor: `${colors.primary}08`,
                color: colors.primary,
                border: `1px solid ${colors.primary}20`,
                fontSize: '14px',
                outline: 'none',
                cursor: 'pointer',
                fontFamily: bodyFont,
              }}
              defaultValue="Public"
            >
              <option>Public</option>
              <option>Private</option>
              <option>Friends Only</option>
            </select>
          </div>
        </div>
        {renderSaveSection()}
      </div>
    );
  }

  function renderDangerZoneTab() {
    return (
      <div>
        <div
          style={{
            borderRadius: '12px',
            border: '1px solid #ef444440',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '16px 20px',
              backgroundColor: '#ef444408',
              borderBottom: '1px solid #ef444425',
            }}
          >
            <h3
              style={{
                color: '#ef4444',
                fontFamily: headingFont,
                fontWeight: '600',
                fontSize: '16px',
                margin: 0,
              }}
            >
              Delete Account
            </h3>
          </div>
          <div style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: colors.primary, fontWeight: '500', fontSize: '14px', margin: '0 0 4px 0' }}>
                Permanently delete your account
              </p>
              <p style={{ color: colors.secondary, fontSize: '13px', margin: 0 }}>
                This action cannot be undone. All your data will be removed.
              </p>
            </div>
            <button
              style={{
                padding: '8px 20px',
                borderRadius: buttonStyles.borderRadius ?? '8px',
                fontWeight: '600',
                fontSize: '14px',
                cursor: 'pointer',
                backgroundColor: '#ef444418',
                color: '#ef4444',
                border: '1px solid #ef4444',
                fontFamily: bodyFont,
                flexShrink: 0,
                marginLeft: '20px',
              }}
            >
              Delete Account
            </button>
          </div>
        </div>
        {renderSaveSection()}
      </div>
    );
  }

  function renderTabContent() {
    switch (activeTab) {
      case 'Profile':
        return renderProfileTab();
      case 'Notifications':
        return renderNotificationsTab();
      case 'Privacy':
        return renderPrivacyTab();
      case 'Danger Zone':
        return renderDangerZoneTab();
    }
  }

  return (
    <div
      className="w-full min-h-[800px] relative"
      style={{ backgroundColor: colors.background, fontFamily: bodyFont }}
    >
      {/* Header */}
      <header
        style={{
          padding: '16px 32px',
          borderBottom: `1px solid ${colors.primary}15`,
          backgroundColor: colors.background,
        }}
      >
        <div style={{ maxWidth: '896px', margin: '0 auto' }}>
          <h1
            style={{
              fontSize: '24px',
              fontWeight: '700',
              color: colors.primary,
              fontFamily: headingFont,
              margin: 0,
            }}
          >
            Settings
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ padding: '32px' }}>
        <div style={{ maxWidth: '896px', margin: '0 auto' }}>
          {/* Tab Bar */}
          <div style={getTabBarStyle()}>
            {TABS.map((tab) => (
              <button key={tab} style={getTabStyle(tab)} onClick={() => setActiveTab(tab)}>
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content Panel */}
          <div
            style={{
              padding: '8px 0',
              minHeight: '400px',
            }}
          >
            {renderTabContent()}
          </div>
        </div>
      </main>
    </div>
  );
}
