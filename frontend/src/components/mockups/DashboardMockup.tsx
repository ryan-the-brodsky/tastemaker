/**
 * Dashboard mockup using extracted user preferences.
 * Demonstrates sidebar navigation, stats cards, tables, modal, form validation,
 * and feedback toasts — all styled via componentStyles.
 */
import { useState } from 'react';
import type { CSSProperties } from 'react';
import { MockupProps } from './types';

/* ------------------------------------------------------------------ */
/*  HoverButton                                                       */
/* ------------------------------------------------------------------ */
function HoverButton({
  baseStyle,
  hoverEffect,
  onClick,
  children,
}: {
  baseStyle: CSSProperties;
  hoverEffect: string;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const [hovered, setHovered] = useState(false);
  const getHoverStyles = (): CSSProperties => {
    if (!hovered) return {};
    switch (hoverEffect) {
      case 'darken':
        return { filter: 'brightness(0.85)' };
      case 'lighten':
        return { filter: 'brightness(1.15)' };
      case 'lift':
        return { transform: 'translateY(-2px)', boxShadow: '0 4px 12px rgba(0,0,0,0.15)' };
      case 'scale':
        return { transform: 'scale(1.05)' };
      default:
        return {};
    }
  };
  return (
    <button
      style={{ ...baseStyle, ...getHoverStyles(), transition: 'all 0.2s', cursor: 'pointer' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

/* ------------------------------------------------------------------ */
/*  DashboardMockup                                                   */
/* ------------------------------------------------------------------ */
export default function DashboardMockup({ colors, typography, componentStyles }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  /* ---- extract component style maps ---- */
  const btnS = componentStyles?.button ?? {};
  const inpS = componentStyles?.input ?? {};
  const cardS = componentStyles?.card ?? {};
  const typoS = componentStyles?.typography ?? {};
  const navS = componentStyles?.navigation ?? {};
  const formS = componentStyles?.form ?? {};
  const modalS = componentStyles?.modal ?? {};
  const fbS = componentStyles?.feedback ?? {};

  /* ---- state ---- */
  const [activeNav, setActiveNav] = useState('Overview');
  const [modalOpen, setModalOpen] = useState(false);
  const [formValues, setFormValues] = useState({ name: '', description: '' });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [showFeedback, setShowFeedback] = useState(false);

  /* ---- data ---- */
  const stats = [
    { label: 'Total Users', value: '12,847', change: '+12%' },
    { label: 'Revenue', value: '$48,352', change: '+8%' },
    { label: 'Active Projects', value: '164', change: '+24%' },
    { label: 'Conversion', value: '3.2%', change: '+2%' },
  ];

  const recentItems = [
    { name: 'Project Alpha', status: 'Active', progress: 75 },
    { name: 'Beta Launch', status: 'Pending', progress: 45 },
    { name: 'Marketing Campaign', status: 'Active', progress: 90 },
    { name: 'User Research', status: 'Complete', progress: 100 },
  ];

  const navItems = ['Overview', 'Analytics', 'Projects', 'Team', 'Settings'];

  /* ---- helpers: typography ---- */
  const headingSizeScale = parseFloat(typoS.headingSizeScale || '1');
  const headingFontWeight = typoS.headingFontWeight || '700';
  const letterSpacing = typoS.letterSpacing || 'normal';
  const lineHeight = typoS.lineHeight || '1.5';
  const paragraphSpacing = typoS.paragraphSpacing || '0.5rem';

  const baseTextStyle: CSSProperties = {
    letterSpacing,
    lineHeight,
  };

  const headingStyle = (baseSizeRem: number): CSSProperties => ({
    fontFamily: headingFont,
    fontWeight: headingFontWeight as CSSProperties['fontWeight'],
    fontSize: `${baseSizeRem * headingSizeScale}rem`,
    letterSpacing,
    lineHeight,
  });

  /* ---- helpers: card ---- */
  const cardStyle: CSSProperties = {
    borderRadius: cardS.borderRadius || '0.75rem',
    boxShadow: cardS.boxShadow || '0 1px 3px rgba(0,0,0,0.08)',
    border: cardS.border || `1px solid ${colors.primary}15`,
    padding: cardS.padding || '1.5rem',
    backgroundColor: cardS.backgroundColor || colors.background,
  };

  /* ---- helpers: button ---- */
  const isOutline = btnS.backgroundStyle === 'outline';
  const buttonBaseStyle: CSSProperties = {
    borderRadius: btnS.borderRadius || '0.5rem',
    padding: btnS.padding || '0.5rem 1rem',
    boxShadow: btnS.boxShadow || 'none',
    fontWeight: (btnS.fontWeight || '500') as CSSProperties['fontWeight'],
    fontSize: btnS.fontSize || '0.875rem',
    textTransform: (btnS.textTransform || 'none') as CSSProperties['textTransform'],
    backgroundColor: isOutline ? 'transparent' : colors.accent,
    color: isOutline ? colors.accent : colors.background,
    border: isOutline ? `2px solid ${colors.accent}` : 'none',
  };
  const hoverEffect = btnS.hoverEffect || 'darken';

  /* ---- helpers: input ---- */
  const inputStyle: CSSProperties = {
    borderRadius: inpS.borderRadius || '0.375rem',
    borderWidth: inpS.borderWidth || '1px',
    borderStyle: 'solid',
    borderColor: `${colors.primary}30`,
    padding: inpS.padding || '0.5rem 0.75rem',
    fontSize: inpS.fontSize || '0.875rem',
    backgroundColor: inpS.inputBackground || colors.background,
    color: colors.primary,
    width: '100%',
    outline: 'none',
    fontFamily: bodyFont,
  };
  const labelPosition = inpS.labelPosition || 'above';

  /* ---- helpers: navigation ---- */
  const activeIndicator = navS.activeIndicator || 'background';
  const navItemPadding = navS.navItemPadding || '0.75rem 1rem';
  const navFontWeight = navS.fontWeight || '400';
  const navSeparator = navS.navSeparator || 'none';

  const getNavItemStyle = (item: string): CSSProperties => {
    const isActive = item === activeNav;
    const base: CSSProperties = {
      padding: navItemPadding,
      fontWeight: (isActive ? '600' : navFontWeight) as CSSProperties['fontWeight'],
      color: colors.background,
      cursor: 'pointer',
      transition: 'all 0.15s',
      opacity: isActive ? 1 : 0.7,
      borderBottom: navSeparator === 'line' ? `1px solid ${colors.background}20` : 'none',
    };
    if (!isActive) return base;
    switch (activeIndicator) {
      case 'underline':
        return { ...base, borderBottom: `2px solid ${colors.background}` };
      case 'background':
        return { ...base, backgroundColor: `${colors.background}20`, borderRadius: '0.5rem' };
      case 'border_left':
        return { ...base, borderLeft: `3px solid ${colors.background}`, paddingLeft: '0.75rem' };
      default:
        return { ...base, backgroundColor: `${colors.background}20`, borderRadius: '0.5rem' };
    }
  };

  /* ---- helpers: form ---- */
  const fieldSpacing = formS.fieldSpacing || '1rem';
  const labelStyle = formS.labelStyle || 'default';
  const requiredIndicator = formS.requiredIndicator || 'asterisk';
  const errorStyle = formS.errorStyle || 'below';
  const groupStyle = formS.groupStyle || 'none';

  const getLabelStyle = (): CSSProperties => {
    const base: CSSProperties = { color: colors.primary, marginBottom: '0.25rem', display: 'block', fontSize: '0.875rem' };
    switch (labelStyle) {
      case 'bold':
        return { ...base, fontWeight: 700 };
      case 'uppercase':
        return { ...base, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em', fontWeight: 600 };
      case 'small_caps':
        return { ...base, fontVariant: 'small-caps', fontWeight: 600 };
      default:
        return { ...base, fontWeight: 500 };
    }
  };

  const getRequiredMark = () => {
    switch (requiredIndicator) {
      case 'asterisk':
        return <span style={{ color: '#ef4444', marginLeft: '0.15rem' }}>*</span>;
      case 'text':
        return <span style={{ color: '#ef4444', fontSize: '0.75rem', marginLeft: '0.25rem' }}>(required)</span>;
      case 'none':
        return null;
      default:
        return <span style={{ color: '#ef4444', marginLeft: '0.15rem' }}>*</span>;
    }
  };

  const getInputErrorStyle = (field: string): CSSProperties => {
    if (!formErrors[field]) return {};
    switch (errorStyle) {
      case 'border':
        return { borderColor: '#ef4444' };
      case 'inline':
        return { borderColor: '#ef4444', backgroundColor: '#fef2f2' };
      default:
        return {};
    }
  };

  /* ---- helpers: modal ---- */
  const modalBorderRadius = modalS.borderRadius || '0.75rem';
  const modalBoxShadow = modalS.boxShadow || '0 25px 50px rgba(0,0,0,0.25)';
  const modalPadding = modalS.padding || '1.5rem';
  const overlayOpacity = parseFloat(modalS.overlayOpacity || '0.5');
  const closeButtonStyle = modalS.closeButtonStyle || 'icon';
  const modalWidth = modalS.modalWidth || '28rem';

  /* ---- helpers: feedback ---- */
  const feedbackStyle = fbS.feedbackStyle || 'toast';
  const fbBorderRadius = fbS.borderRadius || '0.5rem';
  const iconStyle = fbS.iconStyle || 'outline';

  const getFeedbackIcon = () => {
    switch (iconStyle) {
      case 'filled':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '1.25rem',
              height: '1.25rem',
              borderRadius: '50%',
              backgroundColor: colors.accent,
              color: colors.background,
              fontSize: '0.75rem',
              fontWeight: 700,
              marginRight: '0.5rem',
              flexShrink: 0,
            }}
          >
            ✓
          </span>
        );
      case 'outline':
        return (
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '1.25rem',
              height: '1.25rem',
              borderRadius: '50%',
              border: `2px solid ${colors.accent}`,
              color: colors.accent,
              fontSize: '0.75rem',
              fontWeight: 700,
              marginRight: '0.5rem',
              flexShrink: 0,
            }}
          >
            ✓
          </span>
        );
      case 'none':
        return null;
      default:
        return null;
    }
  };

  /* ---- handlers ---- */
  const handleSubmit = () => {
    const errors: Record<string, string> = {};
    if (!formValues.name.trim()) {
      errors.name = 'Project name is required';
    }
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    setFormErrors({});
    setFormValues({ name: '', description: '' });
    setModalOpen(false);
    setShowFeedback(true);
    setTimeout(() => setShowFeedback(false), 3000);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setFormErrors({});
    setFormValues({ name: '', description: '' });
  };

  /* ---- render helpers: form group wrapper ---- */
  const FormGroupWrapper = ({ children }: { children: React.ReactNode }) => {
    const base: CSSProperties = { marginBottom: fieldSpacing };
    switch (groupStyle) {
      case 'card':
        return (
          <div style={{ ...base, ...cardStyle, padding: '1rem' }}>
            {children}
          </div>
        );
      case 'divider':
        return (
          <div style={{ ...base, borderBottom: `1px solid ${colors.primary}15`, paddingBottom: fieldSpacing }}>
            {children}
          </div>
        );
      default:
        return <div style={base}>{children}</div>;
    }
  };

  /* ---- render helpers: labelled input ---- */
  const renderLabelledInput = (
    label: string,
    field: 'name' | 'description',
    required: boolean,
  ) => {
    const hasError = !!formErrors[field];
    const floatingLabel = labelPosition === 'floating';
    const value = formValues[field];

    return (
      <FormGroupWrapper>
        <div style={{ position: 'relative' }}>
          {/* label above */}
          {!floatingLabel && (
            <label style={getLabelStyle()}>
              {label}
              {required && getRequiredMark()}
            </label>
          )}
          {/* floating label */}
          {floatingLabel && (
            <label
              style={{
                position: 'absolute',
                left: inpS.padding ? inpS.padding.split(' ')[0] : '0.75rem',
                top: value ? '0.15rem' : '50%',
                transform: value ? 'none' : 'translateY(-50%)',
                fontSize: value ? '0.65rem' : '0.875rem',
                color: hasError ? '#ef4444' : colors.secondary,
                transition: 'all 0.15s',
                pointerEvents: 'none',
              }}
            >
              {label}
              {required && getRequiredMark()}
            </label>
          )}
          <input
            style={{
              ...inputStyle,
              ...getInputErrorStyle(field),
              paddingTop: floatingLabel && value ? '1.1rem' : undefined,
            }}
            value={value}
            placeholder={floatingLabel ? '' : `Enter ${label.toLowerCase()}`}
            onChange={(e) => {
              setFormValues((v) => ({ ...v, [field]: e.target.value }));
              if (formErrors[field]) {
                setFormErrors((prev) => {
                  const next = { ...prev };
                  delete next[field];
                  return next;
                });
              }
            }}
          />
          {/* inline warning icon */}
          {hasError && errorStyle === 'inline' && (
            <span
              style={{
                position: 'absolute',
                right: '0.75rem',
                top: floatingLabel ? '50%' : 'calc(50% + 0.6rem)',
                transform: 'translateY(-50%)',
                color: '#ef4444',
                fontSize: '1rem',
              }}
            >
              ⚠
            </span>
          )}
        </div>
        {/* error below */}
        {hasError && errorStyle === 'below' && (
          <p style={{ color: '#ef4444', fontSize: '0.75rem', marginTop: '0.25rem' }}>
            {formErrors[field]}
          </p>
        )}
      </FormGroupWrapper>
    );
  };

  /* ================================================================ */
  /*  RENDER                                                          */
  /* ================================================================ */
  return (
    <div
      className="w-full min-h-[800px] flex"
      style={{ backgroundColor: colors.background, fontFamily: bodyFont, ...baseTextStyle, position: 'relative' }}
    >
      {/* ---------------------------------------------------------- */}
      {/*  Sidebar                                                    */}
      {/* ---------------------------------------------------------- */}
      <aside
        className="w-64 min-h-full p-4 flex flex-col"
        style={{ backgroundColor: colors.primary }}
      >
        <div
          className="mb-8 px-2"
          style={{ ...headingStyle(1.25), color: colors.background }}
        >
          Dashboard
        </div>
        <nav className="flex-1">
          {navItems.map((item) => (
            <div
              key={item}
              style={getNavItemStyle(item)}
              onClick={() => setActiveNav(item)}
            >
              {item}
            </div>
          ))}
        </nav>
        <div
          style={{
            padding: navItemPadding,
            color: colors.background,
            opacity: 0.7,
            cursor: 'pointer',
          }}
        >
          Logout
        </div>
      </aside>

      {/* ---------------------------------------------------------- */}
      {/*  Main Content                                               */}
      {/* ---------------------------------------------------------- */}
      <main className="flex-1 p-8" style={{ minWidth: 0 }}>
        {/* Header */}
        <div className="flex items-center justify-between mb-8" style={{ marginBottom: paragraphSpacing }}>
          <div>
            <h1 style={{ ...headingStyle(1.5), color: colors.primary, marginBottom: '0.25rem' }}>
              Welcome back, Alex
            </h1>
            <p style={{ color: colors.secondary, marginBottom: paragraphSpacing }}>
              Here's what's happening with your projects today.
            </p>
          </div>
          <HoverButton
            baseStyle={buttonBaseStyle}
            hoverEffect={hoverEffect}
            onClick={() => setModalOpen(true)}
          >
            + New Project
          </HoverButton>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, i) => (
            <div key={i} style={cardStyle}>
              <p className="text-sm mb-1" style={{ color: colors.secondary }}>
                {stat.label}
              </p>
              <div className="flex items-end justify-between min-w-0">
                <span
                  style={{ ...headingStyle(1.5), color: colors.primary, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                >
                  {stat.value}
                </span>
                <span className="text-sm font-medium" style={{ color: colors.accent, flexShrink: 0 }}>
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Projects Table */}
          <div className="col-span-1 md:col-span-2" style={{ ...cardStyle, padding: 0, overflow: 'hidden' }}>
            <div
              className="px-6 py-4 border-b"
              style={{ borderColor: `${colors.primary}15` }}
            >
              <h2 style={{ ...headingStyle(1), color: colors.primary }}>
                Recent Projects
              </h2>
            </div>
            <div style={{ padding: cardS.padding || '1rem' }}>
              {recentItems.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-3 border-b last:border-0"
                  style={{ borderColor: `${colors.primary}10` }}
                >
                  <div>
                    <p style={{ color: colors.primary, fontWeight: 500 }}>{item.name}</p>
                    <p className="text-sm" style={{ color: colors.secondary }}>
                      {item.status}
                    </p>
                  </div>
                  <div className="w-32">
                    <div
                      className="h-2 rounded-full overflow-hidden"
                      style={{ backgroundColor: `${colors.primary}20` }}
                    >
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${item.progress}%`,
                          backgroundColor: item.progress === 100 ? colors.accent : colors.primary,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Feed */}
          <div style={{ ...cardStyle, padding: 0, overflow: 'hidden' }}>
            <div
              className="px-6 py-4 border-b"
              style={{ borderColor: `${colors.primary}15` }}
            >
              <h2 style={{ ...headingStyle(1), color: colors.primary }}>
                Recent Activity
              </h2>
            </div>
            <div style={{ padding: cardS.padding || '1rem' }}>
              {[
                'New user signed up',
                'Project completed',
                'Payment received',
                'Comment added',
              ].map((activity, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 py-3 border-b last:border-0"
                  style={{ borderColor: `${colors.primary}10` }}
                >
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: colors.accent, flexShrink: 0 }}
                  />
                  <span style={{ color: colors.secondary }} className="text-sm">
                    {activity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* ---------------------------------------------------------- */}
      {/*  Modal Overlay                                              */}
      {/* ---------------------------------------------------------- */}
      {modalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 50,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* overlay backdrop */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: `rgba(0,0,0,${overlayOpacity})`,
            }}
            onClick={handleCloseModal}
          />

          {/* modal panel */}
          <div
            style={{
              position: 'relative',
              width: modalWidth,
              maxWidth: '90vw',
              backgroundColor: colors.background,
              borderRadius: modalBorderRadius,
              boxShadow: modalBoxShadow,
              padding: modalPadding,
              zIndex: 51,
            }}
          >
            {/* close button */}
            {closeButtonStyle === 'outside' ? (
              <button
                onClick={handleCloseModal}
                style={{
                  position: 'absolute',
                  top: '-2rem',
                  right: '-2rem',
                  background: 'none',
                  border: 'none',
                  color: colors.background,
                  fontSize: '1.25rem',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            ) : closeButtonStyle === 'text' ? (
              <button
                onClick={handleCloseModal}
                style={{
                  position: 'absolute',
                  top: modalPadding,
                  right: modalPadding,
                  background: 'none',
                  border: 'none',
                  color: colors.secondary,
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  fontFamily: bodyFont,
                }}
              >
                Close
              </button>
            ) : (
              <button
                onClick={handleCloseModal}
                style={{
                  position: 'absolute',
                  top: '0.75rem',
                  right: '0.75rem',
                  background: 'none',
                  border: 'none',
                  color: colors.secondary,
                  fontSize: '1.25rem',
                  cursor: 'pointer',
                  lineHeight: 1,
                }}
              >
                ✕
              </button>
            )}

            <h2 style={{ ...headingStyle(1.25), color: colors.primary, marginBottom: '1.25rem' }}>
              New Project
            </h2>

            {renderLabelledInput('Project Name', 'name', true)}
            {renderLabelledInput('Description', 'description', false)}

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
              <HoverButton
                baseStyle={{
                  ...buttonBaseStyle,
                  backgroundColor: 'transparent',
                  color: colors.secondary,
                  border: `1px solid ${colors.primary}20`,
                }}
                hoverEffect="darken"
                onClick={handleCloseModal}
              >
                Cancel
              </HoverButton>
              <HoverButton
                baseStyle={buttonBaseStyle}
                hoverEffect={hoverEffect}
                onClick={handleSubmit}
              >
                Create Project
              </HoverButton>
            </div>
          </div>
        </div>
      )}

      {/* ---------------------------------------------------------- */}
      {/*  Feedback Toast / Banner                                    */}
      {/* ---------------------------------------------------------- */}
      {showFeedback && (
        feedbackStyle === 'banner' ? (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              zIndex: 60,
              backgroundColor: colors.accent,
              color: colors.background,
              padding: '0.75rem 1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 500,
              fontSize: '0.875rem',
              borderRadius: 0,
            }}
          >
            {getFeedbackIcon()}
            Project created successfully!
          </div>
        ) : (
          <div
            style={{
              position: 'fixed',
              bottom: '1.5rem',
              right: '1.5rem',
              zIndex: 60,
              backgroundColor: colors.accent,
              color: colors.background,
              padding: '0.75rem 1.25rem',
              borderRadius: fbBorderRadius,
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              display: 'flex',
              alignItems: 'center',
              fontWeight: 500,
              fontSize: '0.875rem',
            }}
          >
            {getFeedbackIcon()}
            Project created successfully!
          </div>
        )
      )}
    </div>
  );
}
