/**
 * Landing page mockup using extracted user preferences.
 * Demonstrates hero section, CTA buttons, feature cards, and testimonials.
 */
import { MockupProps } from './types';

export default function LandingMockup({ colors, typography }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

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
          <button
            className="px-4 py-2 rounded-lg font-medium transition-all"
            style={{
              backgroundColor: colors.primary,
              color: colors.background,
            }}
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-8 py-20 text-center">
        <h1
          className="text-5xl font-bold mb-6 leading-tight"
          style={{ color: colors.primary, fontFamily: headingFont }}
        >
          Build Something
          <br />
          <span style={{ color: colors.accent }}>Amazing</span> Today
        </h1>
        <p
          className="text-xl mb-8 max-w-2xl mx-auto"
          style={{ color: colors.secondary }}
        >
          The modern platform for creators, builders, and dreamers.
          Start your journey with us and transform your ideas into reality.
        </p>
        <div className="flex justify-center gap-4">
          <button
            className="px-8 py-4 rounded-lg font-semibold text-lg shadow-lg transition-all hover:shadow-xl"
            style={{
              backgroundColor: colors.accent,
              color: colors.background,
            }}
          >
            Start Free Trial
          </button>
          <button
            className="px-8 py-4 rounded-lg font-semibold text-lg transition-all"
            style={{
              backgroundColor: 'transparent',
              color: colors.primary,
              border: `2px solid ${colors.primary}`,
            }}
          >
            Watch Demo
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-8 py-16">
        <h2
          className="text-3xl font-bold text-center mb-12"
          style={{ color: colors.primary, fontFamily: headingFont }}
        >
          Why Choose Us?
        </h2>
        <div className="grid grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { title: 'Lightning Fast', desc: 'Optimized for speed and performance' },
            { title: 'Secure by Default', desc: 'Enterprise-grade security built in' },
            { title: 'Scale Effortlessly', desc: 'Grow without limits or constraints' },
          ].map((feature, i) => (
            <div
              key={i}
              className="p-6 rounded-xl shadow-md"
              style={{
                backgroundColor: colors.background,
                border: `1px solid ${colors.primary}15`,
              }}
            >
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                style={{ backgroundColor: `${colors.accent}20` }}
              >
                <span style={{ color: colors.accent, fontSize: '24px' }}>
                  {['⚡', '🔒', '📈'][i]}
                </span>
              </div>
              <h3
                className="text-xl font-semibold mb-2"
                style={{ color: colors.primary, fontFamily: headingFont }}
              >
                {feature.title}
              </h3>
              <p style={{ color: colors.secondary }}>{feature.desc}</p>
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
          className="text-3xl font-bold mb-4"
          style={{ color: colors.primary, fontFamily: headingFont }}
        >
          Ready to Get Started?
        </h2>
        <p className="mb-8" style={{ color: colors.secondary }}>
          Join thousands of happy customers today.
        </p>
        <button
          className="px-8 py-4 rounded-lg font-semibold text-lg shadow-lg"
          style={{
            backgroundColor: colors.primary,
            color: colors.background,
          }}
        >
          Sign Up Now - It's Free
        </button>
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
