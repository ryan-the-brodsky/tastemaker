/**
 * Live preview panel showing the current component with all accumulated styles
 * and the user's color palette / typography applied.
 */
import type { CSSProperties } from 'react';

interface ComponentPreviewProps {
  componentType: string;
  styles: Record<string, string>;
  colors?: {
    primary?: string;
    secondary?: string;
    accent?: string;
    accentSoft?: string;
    background?: string;
    colors?: Record<string, string>;
  } | null;
  typography?: {
    heading?: string;
    body?: string;
  } | null;
  compact?: boolean;
}

function getColor(colors: ComponentPreviewProps['colors'], key: string, fallback: string): string {
  if (!colors) return fallback;
  // Support nested {colors: {primary: ...}} format from exploration
  const nested = colors.colors;
  if (nested && nested[key]) return nested[key];
  return (colors as Record<string, string>)[key] || fallback;
}

export default function ComponentPreview({
  componentType,
  styles,
  colors,
  typography,
  compact = false,
}: ComponentPreviewProps) {
  const primary = getColor(colors, 'primary', '#3b82f6');
  const secondary = getColor(colors, 'secondary', '#6b7280');
  const accent = getColor(colors, 'accent', '#8b5cf6');
  const background = getColor(colors, 'background', '#ffffff');
  const headingFont = typography?.heading || 'Inter, sans-serif';
  const bodyFont = typography?.body || 'Inter, sans-serif';

  const renderers: Record<string, () => React.ReactNode> = {
    button: () => <ButtonPreview styles={styles} primary={primary} background={background} bodyFont={bodyFont} compact={compact} />,
    input: () => <InputPreview styles={styles} primary={primary} secondary={secondary} bodyFont={bodyFont} compact={compact} />,
    card: () => <CardPreview styles={styles} primary={primary} secondary={secondary} accent={accent} headingFont={headingFont} bodyFont={bodyFont} compact={compact} />,
    typography: () => <TypographyPreview styles={styles} primary={primary} secondary={secondary} headingFont={headingFont} bodyFont={bodyFont} compact={compact} />,
    navigation: () => <NavigationPreview styles={styles} primary={primary} secondary={secondary} bodyFont={bodyFont} compact={compact} />,
    form: () => <FormPreview styles={styles} primary={primary} secondary={secondary} bodyFont={bodyFont} compact={compact} />,
    modal: () => <ModalPreview styles={styles} primary={primary} secondary={secondary} headingFont={headingFont} bodyFont={bodyFont} compact={compact} />,
    feedback: () => <FeedbackPreview styles={styles} primary={primary} accent={accent} bodyFont={bodyFont} compact={compact} />,
    table: () => <TablePreview styles={styles} primary={primary} secondary={secondary} bodyFont={bodyFont} compact={compact} />,
    badge: () => <BadgePreview styles={styles} primary={primary} accent={accent} bodyFont={bodyFont} compact={compact} />,
    tabs: () => <TabsPreview styles={styles} primary={primary} secondary={secondary} bodyFont={bodyFont} compact={compact} />,
    toggle: () => <TogglePreview styles={styles} primary={primary} accent={accent} bodyFont={bodyFont} compact={compact} />,
  };

  const renderer = renderers[componentType];
  if (!renderer) {
    return <div className="text-gray-400 text-sm">Unknown component: {componentType}</div>;
  }

  return (
    <div className={`flex items-center justify-center ${compact ? 'p-2' : 'p-6'}`} style={{ backgroundColor: background, minHeight: compact ? 60 : 200 }}>
      {renderer()}
    </div>
  );
}

// ============================================================================
// Individual component preview renderers
// ============================================================================

interface PreviewProps {
  styles: Record<string, string>;
  primary: string;
  secondary?: string;
  accent?: string;
  background?: string;
  headingFont?: string;
  bodyFont: string;
  compact: boolean;
}

function ButtonPreview({ styles, primary, background, bodyFont, compact }: PreviewProps) {
  const bgStyle = styles.backgroundStyle || 'solid';
  const isSolid = bgStyle === 'solid';
  const isOutline = bgStyle === 'outline';

  const buttonStyle: CSSProperties = {
    borderRadius: styles.borderRadius || '8px',
    boxShadow: styles.boxShadow !== 'none' ? styles.boxShadow : undefined,
    padding: styles.padding || '10px 20px',
    fontWeight: styles.fontWeight || '500',
    fontSize: styles.fontSize || '15px',
    textTransform: (styles.textTransform as CSSProperties['textTransform']) || 'none',
    border: isOutline ? `2px solid ${primary}` : (styles.border !== 'none' ? styles.border : 'none'),
    backgroundColor: isSolid ? primary : 'transparent',
    color: isSolid ? (background || '#ffffff') : primary,
    fontFamily: bodyFont,
    cursor: 'pointer',
    transition: 'all 0.2s',
  };

  return (
    <div className={`flex ${compact ? 'gap-2' : 'gap-4'} items-center`}>
      <button style={buttonStyle}>{compact ? 'Button' : 'Get Started'}</button>
      {!compact && (
        <button style={{ ...buttonStyle, backgroundColor: 'transparent', color: primary, border: `1px solid ${primary}40` }}>
          Learn More
        </button>
      )}
    </div>
  );
}

function InputPreview({ styles, primary, secondary, bodyFont, compact }: PreviewProps) {
  const inputStyle: CSSProperties = {
    borderRadius: styles.borderRadius || '6px',
    borderWidth: styles.borderWidth || '1px',
    borderStyle: 'solid',
    borderColor: '#d1d5db',
    padding: styles.padding || '10px 14px',
    fontSize: styles.fontSize || '15px',
    fontFamily: bodyFont,
    backgroundColor: styles.inputBackground || '#ffffff',
    outline: 'none',
    width: compact ? '160px' : '280px',
    color: '#111827',
  };

  const labelPos = styles.labelPosition || 'above';

  return (
    <div className={compact ? '' : 'space-y-1'}>
      {labelPos === 'above' && (
        <label style={{ fontSize: '13px', fontWeight: 500, color: secondary, fontFamily: bodyFont, display: 'block', marginBottom: '4px' }}>
          Email address
        </label>
      )}
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          readOnly
          placeholder={labelPos === 'floating' ? '' : 'you@example.com'}
          style={inputStyle}
          onFocus={() => {}}
        />
        {labelPos === 'floating' && (
          <span style={{ position: 'absolute', top: '-8px', left: '10px', fontSize: '11px', color: primary, backgroundColor: styles.inputBackground || '#ffffff', padding: '0 4px', fontFamily: bodyFont }}>
            Email address
          </span>
        )}
      </div>
    </div>
  );
}

function CardPreview({ styles, primary, secondary, headingFont, bodyFont, compact }: PreviewProps) {
  const cardStyle: CSSProperties = {
    borderRadius: styles.borderRadius || '8px',
    boxShadow: styles.boxShadow !== 'none' ? styles.boxShadow : undefined,
    border: styles.border !== 'none' ? styles.border : undefined,
    padding: styles.padding || '24px',
    backgroundColor: styles.backgroundColor || '#ffffff',
    width: compact ? '180px' : '320px',
  };

  return (
    <div style={cardStyle}>
      <h3 style={{ fontFamily: headingFont, fontWeight: 600, fontSize: compact ? '14px' : '18px', color: primary, marginBottom: '8px' }}>
        Feature Card
      </h3>
      <p style={{ fontFamily: bodyFont, fontSize: compact ? '12px' : '14px', color: secondary, lineHeight: 1.5 }}>
        {compact ? 'Card content preview.' : 'Showcase your product features with clean, organized cards.'}
      </p>
    </div>
  );
}

function TypographyPreview({ styles, primary, secondary, headingFont, bodyFont, compact }: PreviewProps) {
  const scale = parseFloat(styles.headingSizeScale || '1.25');
  const baseSize = compact ? 14 : 16;

  return (
    <div className={compact ? 'space-y-1' : 'space-y-3'} style={{ maxWidth: compact ? '200px' : '400px' }}>
      <h1 style={{
        fontFamily: headingFont,
        fontWeight: styles.headingFontWeight || '700',
        fontSize: `${baseSize * scale * scale}px`,
        letterSpacing: styles.letterSpacing || '0',
        color: primary,
        lineHeight: 1.2,
      }}>
        Heading One
      </h1>
      {!compact && (
        <h2 style={{
          fontFamily: headingFont,
          fontWeight: styles.headingFontWeight || '700',
          fontSize: `${baseSize * scale}px`,
          letterSpacing: styles.letterSpacing || '0',
          color: secondary,
          lineHeight: 1.3,
        }}>
          Heading Two
        </h2>
      )}
      <p style={{
        fontFamily: bodyFont,
        fontSize: `${baseSize}px`,
        lineHeight: styles.lineHeight || '1.6',
        letterSpacing: styles.letterSpacing || '0',
        color: '#374151',
        marginBottom: styles.paragraphSpacing || '1em',
      }}>
        {compact ? 'Body text sample.' : 'This is body text demonstrating your typography choices. Good typography makes content readable and professional.'}
      </p>
    </div>
  );
}

function NavigationPreview({ styles, primary, secondary, bodyFont, compact }: PreviewProps) {
  const navStyle = styles.navStyle || 'horizontal';
  const isHorizontal = navStyle === 'horizontal';
  const items = compact ? ['Home', 'About'] : ['Home', 'About', 'Services', 'Contact'];
  const activeIdx = 0;

  const indicator = styles.activeIndicator || 'underline';

  const getItemStyle = (isActive: boolean): CSSProperties => ({
    padding: styles.navItemPadding || '8px 16px',
    fontWeight: isActive ? '600' : (styles.fontWeight || '400'),
    color: isActive ? primary : secondary,
    fontFamily: bodyFont,
    fontSize: compact ? '13px' : '14px',
    borderBottom: isActive && indicator === 'underline' ? `2px solid ${primary}` : 'none',
    backgroundColor: isActive && indicator === 'background' ? `${primary}15` : 'transparent',
    borderLeft: isActive && indicator === 'border_left' ? `3px solid ${primary}` : 'none',
    cursor: 'pointer',
    borderRadius: indicator === 'background' ? '6px' : '0',
  });

  return (
    <nav style={{
      display: 'flex',
      flexDirection: isHorizontal ? 'row' : 'column',
      gap: styles.navSeparator === 'dot' ? '0' : '0',
      borderBottom: isHorizontal ? '1px solid #e5e7eb' : 'none',
      borderRight: !isHorizontal ? '1px solid #e5e7eb' : 'none',
      paddingRight: !isHorizontal ? '8px' : '0',
    }}>
      {items.map((item, i) => (
        <span key={item}>
          <span style={getItemStyle(i === activeIdx)}>{item}</span>
          {styles.navSeparator === 'dot' && i < items.length - 1 && isHorizontal && (
            <span style={{ color: '#d1d5db', padding: '0 4px' }}>·</span>
          )}
        </span>
      ))}
    </nav>
  );
}

function FormPreview({ styles, secondary, bodyFont, compact }: PreviewProps) {
  const spacing = styles.fieldSpacing || '20px';
  const labelStyle = styles.labelStyle || 'default';
  const requiredIndicator = styles.requiredIndicator || 'asterisk';

  const getLabelStyle = (): CSSProperties => ({
    fontSize: '13px',
    fontWeight: labelStyle === 'bold' ? 600 : 500,
    textTransform: labelStyle === 'uppercase' ? 'uppercase' : labelStyle === 'small_caps' ? ('small-caps' as CSSProperties['textTransform']) : 'none',
    color: secondary,
    fontFamily: bodyFont,
    letterSpacing: labelStyle === 'uppercase' ? '0.05em' : '0',
    marginBottom: '4px',
    display: 'block',
  });

  const getRequired = () => {
    if (requiredIndicator === 'asterisk') return <span style={{ color: '#ef4444' }}> *</span>;
    if (requiredIndicator === 'text') return <span style={{ fontSize: '11px', color: secondary }}> (required)</span>;
    return null;
  };

  const inputStyle: CSSProperties = {
    borderRadius: '6px', border: '1px solid #d1d5db', padding: '8px 12px',
    fontSize: '14px', fontFamily: bodyFont, width: '100%', boxSizing: 'border-box',
  };

  const groupStyle = styles.groupStyle || 'none';

  const wrapper: CSSProperties = groupStyle === 'card'
    ? { border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px' }
    : groupStyle === 'divider'
    ? { borderBottom: '1px solid #e5e7eb', paddingBottom: spacing }
    : {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing, width: compact ? '180px' : '300px', ...wrapper }}>
      <div>
        <label style={getLabelStyle()}>Full Name{getRequired()}</label>
        <input readOnly placeholder="John Doe" style={inputStyle} />
      </div>
      {!compact && (
        <>
          <div>
            <label style={getLabelStyle()}>Email{getRequired()}</label>
            <input readOnly placeholder="john@example.com" style={inputStyle} />
          </div>
          {styles.errorStyle === 'below' && (
            <div style={{ fontSize: '12px', color: '#ef4444', marginTop: '-8px' }}>Please enter a valid email</div>
          )}
        </>
      )}
    </div>
  );
}

function ModalPreview({ styles, primary, secondary, headingFont, bodyFont, compact }: PreviewProps) {
  const overlayOpacity = parseFloat(styles.overlayOpacity || '0.5');

  return (
    <div style={{ position: 'relative', width: compact ? '200px' : '400px', height: compact ? '140px' : '260px', borderRadius: '8px', overflow: 'hidden' }}>
      {/* Fake background */}
      <div style={{ position: 'absolute', inset: 0, backgroundColor: '#f3f4f6' }}>
        <div style={{ padding: '12px', opacity: 0.5 }}>
          <div style={{ height: '8px', width: '60%', backgroundColor: '#d1d5db', borderRadius: '4px', marginBottom: '8px' }} />
          <div style={{ height: '8px', width: '40%', backgroundColor: '#d1d5db', borderRadius: '4px' }} />
        </div>
      </div>
      {/* Overlay */}
      <div style={{ position: 'absolute', inset: 0, backgroundColor: `rgba(0,0,0,${overlayOpacity})` }} />
      {/* Modal */}
      <div style={{
        position: 'absolute',
        top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        width: compact ? '160px' : (styles.modalWidth || '320px'),
        maxWidth: '90%',
        backgroundColor: '#ffffff',
        borderRadius: styles.borderRadius || '12px',
        boxShadow: styles.boxShadow || '0 10px 40px rgba(0,0,0,0.2)',
        padding: styles.padding || '24px',
      }}>
        <h3 style={{ fontFamily: headingFont, fontWeight: 600, fontSize: compact ? '13px' : '16px', color: primary, marginBottom: '8px' }}>
          Confirm Action
        </h3>
        <p style={{ fontFamily: bodyFont, fontSize: compact ? '11px' : '13px', color: secondary, marginBottom: compact ? '8px' : '16px' }}>
          {compact ? 'Are you sure?' : 'Are you sure you want to proceed with this action?'}
        </p>
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button style={{ padding: '4px 12px', fontSize: '12px', border: '1px solid #d1d5db', borderRadius: '6px', cursor: 'pointer', backgroundColor: 'transparent', color: secondary }}>Cancel</button>
          <button style={{ padding: '4px 12px', fontSize: '12px', backgroundColor: primary, color: '#ffffff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Confirm</button>
        </div>
      </div>
    </div>
  );
}

function FeedbackPreview({ styles, primary, accent, bodyFont, compact }: PreviewProps) {
  const feedbackStyle = styles.feedbackStyle || 'toast';
  const isToast = feedbackStyle === 'toast';
  const isBanner = feedbackStyle === 'banner';
  const iconStyle = styles.iconStyle || 'outline';

  const icon = iconStyle === 'none' ? null : (
    <span style={{ fontSize: compact ? '14px' : '18px', marginRight: '8px' }}>
      {iconStyle === 'filled' ? '✅' : '✓'}
    </span>
  );

  const containerStyle: CSSProperties = {
    borderRadius: styles.borderRadius || '8px',
    padding: compact ? '8px 12px' : '12px 16px',
    fontFamily: bodyFont,
    fontSize: compact ? '12px' : '14px',
    display: 'flex',
    alignItems: 'center',
    width: isBanner ? (compact ? '200px' : '360px') : 'auto',
    maxWidth: '360px',
    backgroundColor: `${accent || primary}12`,
    border: `1px solid ${accent || primary}30`,
    color: '#374151',
  };

  if (isToast) {
    containerStyle.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    containerStyle.backgroundColor = '#ffffff';
  }

  return (
    <div className={compact ? '' : 'space-y-3'}>
      <div style={containerStyle}>
        {icon}
        <span>Changes saved successfully</span>
      </div>
      {!compact && (
        <div style={{ ...containerStyle, backgroundColor: '#fef2f2', borderColor: '#fecaca', color: '#991b1b' }}>
          {iconStyle !== 'none' && <span style={{ fontSize: '18px', marginRight: '8px' }}>{iconStyle === 'filled' ? '❌' : '✗'}</span>}
          <span>Something went wrong</span>
        </div>
      )}
    </div>
  );
}

function TablePreview({ styles, primary, secondary, bodyFont, compact }: PreviewProps) {
  const borderStyle = styles.tableBorderStyle || 'horizontal';
  const striping = styles.rowStriping || 'none';
  const headerStyle = styles.tableHeaderStyle || 'bold';
  const cellPad = styles.cellPadding || '12px 16px';

  const headers = compact ? ['Name', 'Role'] : ['Name', 'Role', 'Status', 'Actions'];
  const rows = compact
    ? [['Alice', 'Admin'], ['Bob', 'User']]
    : [['Alice Johnson', 'Admin', 'Active', 'Edit'], ['Bob Smith', 'Editor', 'Active', 'Edit'], ['Carol Davis', 'Viewer', 'Inactive', 'Edit']];

  const getBorder = () => {
    if (borderStyle === 'full') return '1px solid #e5e7eb';
    return 'none';
  };

  const getRowBg = (i: number) => {
    if (striping === 'even' && i % 2 === 0) return '#f9fafb';
    if (striping === 'odd' && i % 2 === 1) return '#f9fafb';
    return 'transparent';
  };

  return (
    <table style={{ borderCollapse: 'collapse', fontFamily: bodyFont, fontSize: compact ? '12px' : '14px', width: compact ? '200px' : '100%', maxWidth: '500px', border: getBorder() }}>
      <thead>
        <tr style={{
          borderBottom: '2px solid #e5e7eb',
          backgroundColor: headerStyle === 'shaded' ? '#f3f4f6' : 'transparent',
        }}>
          {headers.map(h => (
            <th key={h} style={{ padding: cellPad, textAlign: 'left', fontWeight: headerStyle !== 'plain' ? 600 : 400, color: primary, fontSize: compact ? '11px' : '13px' }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} style={{
            borderBottom: borderStyle !== 'none' ? '1px solid #e5e7eb' : 'none',
            backgroundColor: getRowBg(i),
          }}>
            {row.map((cell, j) => (
              <td key={j} style={{ padding: cellPad, color: j === 0 ? '#111827' : secondary }}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function BadgePreview({ styles, primary, accent, bodyFont, compact }: PreviewProps) {
  const badgeStyle = styles.badgeStyle || 'solid';
  const badges = compact
    ? [{ label: 'Active', color: '#16a34a' }, { label: 'Error', color: '#dc2626' }]
    : [
        { label: 'Active', color: '#16a34a' },
        { label: 'Warning', color: '#d97706' },
        { label: 'Error', color: '#dc2626' },
        { label: 'Info', color: accent || primary },
      ];

  const getBadgeStyle = (color: string): CSSProperties => {
    const base: CSSProperties = {
      borderRadius: styles.borderRadius || '9999px',
      padding: styles.padding || '4px 10px',
      fontSize: styles.fontSize || '13px',
      fontWeight: styles.fontWeight || '500',
      fontFamily: bodyFont,
      display: 'inline-block',
    };

    if (badgeStyle === 'solid') {
      base.backgroundColor = color;
      base.color = '#ffffff';
    } else if (badgeStyle === 'outline') {
      base.backgroundColor = 'transparent';
      base.color = color;
      base.border = `1.5px solid ${color}`;
    } else {
      // subtle
      base.backgroundColor = `${color}15`;
      base.color = color;
    }

    return base;
  };

  return (
    <div style={{ display: 'flex', gap: compact ? '6px' : '10px', flexWrap: 'wrap' }}>
      {badges.map(b => (
        <span key={b.label} style={getBadgeStyle(b.color)}>{b.label}</span>
      ))}
    </div>
  );
}

function TabsPreview({ styles, primary, secondary, bodyFont, compact }: PreviewProps) {
  const tabStyle = styles.tabStyle || 'underline';
  const spacing = styles.tabSpacing || '8px';
  const tabs = compact ? ['Tab 1', 'Tab 2'] : ['Overview', 'Settings', 'Billing', 'Team'];
  const activeIdx = 0;

  const indicatorStyle = styles.tabIndicatorStyle || 'thin';

  const getTabStyle = (isActive: boolean): CSSProperties => {
    const base: CSSProperties = {
      padding: tabStyle === 'pill' ? '6px 16px' : '8px 16px',
      fontWeight: isActive ? (styles.fontWeight || '500') : '400',
      color: isActive ? primary : secondary,
      fontFamily: bodyFont,
      fontSize: compact ? '13px' : '14px',
      cursor: 'pointer',
      border: 'none',
      backgroundColor: 'transparent',
      transition: 'all 0.2s',
    };

    if (tabStyle === 'underline') {
      const thickness = indicatorStyle === 'thick' ? '3px' : indicatorStyle === 'thin' ? '2px' : '2px';
      base.borderBottom = isActive ? `${thickness} solid ${primary}` : '2px solid transparent';
    } else if (tabStyle === 'boxed') {
      if (isActive) {
        base.backgroundColor = '#ffffff';
        base.border = '1px solid #e5e7eb';
        base.borderBottom = '1px solid #ffffff';
        base.borderRadius = '6px 6px 0 0';
        base.marginBottom = '-1px';
      }
    } else if (tabStyle === 'pill') {
      if (isActive) {
        base.backgroundColor = `${primary}15`;
        base.borderRadius = '9999px';
      }
    }

    return base;
  };

  return (
    <div style={{
      display: 'flex',
      gap: spacing,
      borderBottom: tabStyle === 'boxed' ? '1px solid #e5e7eb' : tabStyle === 'underline' ? '1px solid #e5e7eb' : 'none',
      paddingBottom: tabStyle === 'pill' ? '0' : '0',
    }}>
      {tabs.map((tab, i) => (
        <button key={tab} style={getTabStyle(i === activeIdx)}>{tab}</button>
      ))}
    </div>
  );
}

function TogglePreview({ styles, primary, accent, bodyFont, compact }: PreviewProps) {
  const size = styles.toggleSize || 'medium';
  const labelPos = styles.toggleLabelPosition || 'right';

  const sizes: Record<string, { track: { w: number; h: number }; thumb: number }> = {
    small: { track: { w: 36, h: 20 }, thumb: 16 },
    medium: { track: { w: 44, h: 24 }, thumb: 20 },
    large: { track: { w: 56, h: 30 }, thumb: 26 },
  };

  const s = sizes[size] || sizes.medium;
  const br = styles.borderRadius || '9999px';
  const thumbBr = br === '4px' ? '2px' : '9999px';

  const renderToggle = (isOn: boolean) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexDirection: labelPos === 'left' ? 'row-reverse' : 'row' }}>
      <div style={{
        width: s.track.w, height: s.track.h,
        borderRadius: br,
        backgroundColor: isOn ? (accent || primary) : '#d1d5db',
        position: 'relative',
        transition: 'background-color 0.2s',
        cursor: 'pointer',
        flexShrink: 0,
      }}>
        <div style={{
          width: s.thumb, height: s.thumb,
          borderRadius: thumbBr,
          backgroundColor: '#ffffff',
          position: 'absolute',
          top: (s.track.h - s.thumb) / 2,
          left: isOn ? s.track.w - s.thumb - (s.track.h - s.thumb) / 2 : (s.track.h - s.thumb) / 2,
          transition: 'left 0.2s',
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
        }} />
      </div>
      <span style={{ fontFamily: bodyFont, fontSize: compact ? '12px' : '14px', color: '#374151' }}>
        {isOn ? 'Enabled' : 'Disabled'}
      </span>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: compact ? '8px' : '16px' }}>
      {renderToggle(true)}
      {!compact && renderToggle(false)}
    </div>
  );
}
