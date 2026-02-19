/**
 * Landing page mockup using extracted user preferences.
 * Demonstrates hero section, CTA buttons, feature cards, signup form, and footer.
 * Applies componentStyles for buttons, cards, inputs, and typography.
 */
import { useState, useRef } from 'react';
import { MockupProps } from './types';

function HoverButton({
  baseStyle,
  hoverEffect,
  onClick,
  children,
}: {
  baseStyle: React.CSSProperties;
  hoverEffect: string;
  onClick?: () => void;
  children: React.ReactNode;
}) {
  const [hovered, setHovered] = useState(false);

  const getHoverStyles = (): React.CSSProperties => {
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

export default function LandingMockup({ colors, typography, componentStyles }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  const signupRef = useRef<HTMLDivElement>(null);

  const buttonStyles = componentStyles?.button || {};
  const cardStyles = componentStyles?.card || {};
  const inputStyles = componentStyles?.input || {};
  const typographyStyles = componentStyles?.typography || {};

  const scrollToSignup = () => {
    signupRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Resolve button base styles from componentStyles
  const resolveButtonStyle = (bgColor: string, textColor: string): React.CSSProperties => {
    const style: React.CSSProperties = {
      backgroundColor: bgColor,
      color: textColor,
    };
    if (buttonStyles.borderRadius) style.borderRadius = buttonStyles.borderRadius;
    if (buttonStyles.padding) style.padding = buttonStyles.padding;
    if (buttonStyles.boxShadow) style.boxShadow = buttonStyles.boxShadow;
    if (buttonStyles.fontWeight) style.fontWeight = buttonStyles.fontWeight;
    if (buttonStyles.fontSize) style.fontSize = buttonStyles.fontSize;
    if (buttonStyles.textTransform) style.textTransform = buttonStyles.textTransform as React.CSSProperties['textTransform'];
    return style;
  };

  const resolveOutlineButtonStyle = (borderColor: string, textColor: string): React.CSSProperties => {
    const style: React.CSSProperties = {
      backgroundColor: 'transparent',
      color: textColor,
      border: `2px solid ${borderColor}`,
    };
    if (buttonStyles.borderRadius) style.borderRadius = buttonStyles.borderRadius;
    if (buttonStyles.padding) style.padding = buttonStyles.padding;
    if (buttonStyles.fontWeight) style.fontWeight = buttonStyles.fontWeight;
    if (buttonStyles.fontSize) style.fontSize = buttonStyles.fontSize;
    if (buttonStyles.textTransform) style.textTransform = buttonStyles.textTransform as React.CSSProperties['textTransform'];
    return style;
  };

  const hoverEffect = buttonStyles.hoverEffect || 'darken';

  // Card styles
  const resolveCardStyle = (): React.CSSProperties => {
    const style: React.CSSProperties = {
      backgroundColor: cardStyles.backgroundColor || colors.background,
      border: cardStyles.border || `1px solid ${colors.primary}15`,
    };
    if (cardStyles.borderRadius) style.borderRadius = cardStyles.borderRadius;
    if (cardStyles.boxShadow) style.boxShadow = cardStyles.boxShadow;
    if (cardStyles.padding) style.padding = cardStyles.padding;
    return style;
  };

  // Input styles
  const resolveInputStyle = (): React.CSSProperties => {
    const style: React.CSSProperties = {
      width: '100%',
      outline: 'none',
      color: colors.primary,
      backgroundColor: inputStyles.inputBackground || colors.background,
      border: `${inputStyles.borderWidth || '1px'} solid ${colors.primary}30`,
    };
    if (inputStyles.borderRadius) style.borderRadius = inputStyles.borderRadius;
    if (inputStyles.padding) style.padding = inputStyles.padding;
    if (inputStyles.fontSize) style.fontSize = inputStyles.fontSize;
    return style;
  };

  const labelPosition = inputStyles.labelPosition || 'above';

  // Typography styles
  const resolveHeadingStyle = (baseSizePx: number): React.CSSProperties => {
    const scale = typographyStyles.headingSizeScale ? parseFloat(typographyStyles.headingSizeScale) : 1;
    const style: React.CSSProperties = {
      color: colors.primary,
      fontFamily: headingFont,
      fontSize: `${Math.round(baseSizePx * scale)}px`,
    };
    if (typographyStyles.headingFontWeight) style.fontWeight = typographyStyles.headingFontWeight;
    if (typographyStyles.letterSpacing) style.letterSpacing = typographyStyles.letterSpacing;
    if (typographyStyles.lineHeight) style.lineHeight = typographyStyles.lineHeight;
    return style;
  };

  const resolveParagraphStyle = (): React.CSSProperties => {
    const style: React.CSSProperties = {
      color: colors.secondary,
    };
    if (typographyStyles.lineHeight) style.lineHeight = typographyStyles.lineHeight;
    if (typographyStyles.paragraphSpacing) style.marginBottom = typographyStyles.paragraphSpacing;
    return style;
  };

  return (
    <div
      className="w-full min-h-[800px] overflow-hidden"
      style={{
        backgroundColor: colors.background,
        fontFamily: bodyFont,
      }}
    >
      {/* Navigation */}
      <nav
        className="flex items-center justify-between px-8 py-4"
        style={{ borderBottom: `1px solid ${colors.primary}20` }}
      >
        <div
          className="text-xl font-bold"
          style={{ color: colors.primary, fontFamily: headingFont }}
        >
          YourBrand
        </div>
        <div className="flex items-center gap-6">
          <span style={{ color: colors.secondary }} className="cursor-pointer hover:opacity-80">
            Features
          </span>
          <span style={{ color: colors.secondary }} className="cursor-pointer hover:opacity-80">
            Pricing
          </span>
          <span style={{ color: colors.secondary }} className="cursor-pointer hover:opacity-80">
            About
          </span>
          <HoverButton
            baseStyle={resolveButtonStyle(colors.primary, colors.background)}
            hoverEffect={hoverEffect}
            onClick={scrollToSignup}
          >
            Get Started
          </HoverButton>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-8 py-20 text-center">
        <h1
          className="mb-6 leading-tight"
          style={resolveHeadingStyle(48)}
        >
          Build Something
          <br />
          <span style={{ color: colors.accent }}>Amazing</span> Today
        </h1>
        <p
          className="text-xl mb-8 max-w-2xl mx-auto"
          style={resolveParagraphStyle()}
        >
          The modern platform for creators, builders, and dreamers.
          Start your journey with us and transform your ideas into reality.
        </p>
        <div className="flex justify-center gap-4">
          <HoverButton
            baseStyle={resolveButtonStyle(colors.accent, colors.background)}
            hoverEffect={hoverEffect}
            onClick={scrollToSignup}
          >
            Start Free Trial
          </HoverButton>
          <HoverButton
            baseStyle={resolveOutlineButtonStyle(colors.primary, colors.primary)}
            hoverEffect={hoverEffect}
          >
            Watch Demo
          </HoverButton>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-8 py-16">
        <h2
          className="text-center mb-12"
          style={resolveHeadingStyle(30)}
        >
          Why Choose Us?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { title: 'Lightning Fast', desc: 'Optimized for speed and performance', icon: '⚡' },
            { title: 'Secure by Default', desc: 'Enterprise-grade security built in', icon: '🔒' },
            { title: 'Scale Effortlessly', desc: 'Grow without limits or constraints', icon: '📈' },
          ].map((feature, i) => (
            <div
              key={i}
              className="p-6 rounded-xl shadow-md"
              style={resolveCardStyle()}
            >
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                style={{ backgroundColor: `${colors.accent}20` }}
              >
                <span style={{ color: colors.accent, fontSize: '24px' }}>
                  {feature.icon}
                </span>
              </div>
              <h3
                className="mb-2"
                style={resolveHeadingStyle(20)}
              >
                {feature.title}
              </h3>
              <p style={resolveParagraphStyle()}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section
        className="px-8 py-16 text-center"
        style={{ backgroundColor: `${colors.primary}10` }}
      >
        <h2
          className="mb-4"
          style={resolveHeadingStyle(30)}
        >
          Ready to Get Started?
        </h2>
        <p className="mb-8" style={resolveParagraphStyle()}>
          Join thousands of happy customers today.
        </p>
        <HoverButton
          baseStyle={resolveButtonStyle(colors.primary, colors.background)}
          hoverEffect={hoverEffect}
          onClick={scrollToSignup}
        >
          Sign Up Now
        </HoverButton>
      </section>

      {/* Signup Form Section */}
      <section
        id="signup"
        ref={signupRef}
        className="px-8 py-16"
        style={{ backgroundColor: colors.background }}
      >
        <div className="max-w-md mx-auto">
          <h2
            className="text-center mb-8"
            style={resolveHeadingStyle(28)}
          >
            Create Your Account
          </h2>
          <form
            className="flex flex-col gap-5"
            onSubmit={(e) => e.preventDefault()}
          >
            <div className={labelPosition === 'inline' ? 'flex items-center gap-3' : 'flex flex-col gap-1'}>
              <label
                style={{ color: colors.primary, fontFamily: headingFont, fontWeight: 600, fontSize: '14px' }}
              >
                Name
              </label>
              <input
                type="text"
                placeholder="Your full name"
                style={resolveInputStyle()}
              />
            </div>
            <div className={labelPosition === 'inline' ? 'flex items-center gap-3' : 'flex flex-col gap-1'}>
              <label
                style={{ color: colors.primary, fontFamily: headingFont, fontWeight: 600, fontSize: '14px' }}
              >
                Email
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                style={resolveInputStyle()}
              />
            </div>
            <HoverButton
              baseStyle={{
                ...resolveButtonStyle(colors.accent, colors.background),
                width: '100%',
                marginTop: '8px',
              }}
              hoverEffect={hoverEffect}
            >
              Create Account
            </HoverButton>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="px-8 py-8 text-center"
        style={{ backgroundColor: colors.primary, color: colors.background }}
      >
        <p style={{ opacity: 0.8 }}>
          &copy; 2026 YourBrand. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
