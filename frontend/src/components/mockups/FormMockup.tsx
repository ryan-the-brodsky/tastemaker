/**
 * Form mockup using extracted user preferences.
 * Demonstrates multi-step form wizard with inputs, selects, and validation states.
 */
import { MockupProps } from './types';

export default function FormMockup({ colors, typography }: MockupProps) {
  const headingFont = typography.heading || 'Inter';
  const bodyFont = typography.body || 'Inter';

  const steps = ['Personal Info', 'Contact', 'Preferences', 'Review'];
  const currentStep = 1; // 0-indexed

  return (
    <div
      className="w-full min-h-[800px] flex flex-col"
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
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <h1
            className="text-xl font-bold"
            style={{ color: colors.primary, fontFamily: headingFont }}
          >
            Account Setup
          </h1>
          <span className="text-sm" style={{ color: colors.secondary }}>
            Step {currentStep + 1} of {steps.length}
          </span>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="px-8 py-6" style={{ backgroundColor: `${colors.primary}05` }}>
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          {steps.map((step, i) => (
            <div key={step} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center font-semibold"
                  style={{
                    backgroundColor:
                      i <= currentStep ? colors.primary : `${colors.primary}20`,
                    color: i <= currentStep ? colors.background : colors.primary,
                  }}
                >
                  {i < currentStep ? '✓' : i + 1}
                </div>
                <span
                  className="text-xs mt-2"
                  style={{
                    color: i <= currentStep ? colors.primary : colors.secondary,
                    fontWeight: i === currentStep ? 600 : 400,
                  }}
                >
                  {step}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className="w-24 h-1 mx-4 rounded"
                  style={{
                    backgroundColor:
                      i < currentStep ? colors.primary : `${colors.primary}20`,
                  }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <main className="flex-1 px-8 py-12">
        <div className="max-w-2xl mx-auto">
          <h2
            className="text-2xl font-bold mb-2"
            style={{ color: colors.primary, fontFamily: headingFont }}
          >
            Contact Information
          </h2>
          <p className="mb-8" style={{ color: colors.secondary }}>
            Please provide your contact details so we can reach you.
          </p>

          <form className="space-y-6">
            {/* Email Field */}
            <div>
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: colors.primary }}
              >
                Email Address *
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-3 rounded-lg outline-none transition-all"
                style={{
                  backgroundColor: colors.background,
                  border: `2px solid ${colors.primary}30`,
                  color: colors.primary,
                }}
              />
            </div>

            {/* Phone Field */}
            <div>
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: colors.primary }}
              >
                Phone Number
              </label>
              <input
                type="tel"
                placeholder="+1 (555) 000-0000"
                className="w-full px-4 py-3 rounded-lg outline-none transition-all"
                style={{
                  backgroundColor: colors.background,
                  border: `2px solid ${colors.primary}30`,
                  color: colors.primary,
                }}
              />
              <p className="text-sm mt-1" style={{ color: colors.secondary }}>
                Optional - for SMS notifications
              </p>
            </div>

            {/* Location Field */}
            <div>
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: colors.primary }}
              >
                Country *
              </label>
              <select
                className="w-full px-4 py-3 rounded-lg outline-none transition-all cursor-pointer"
                style={{
                  backgroundColor: colors.background,
                  border: `2px solid ${colors.primary}30`,
                  color: colors.primary,
                }}
              >
                <option>Select a country...</option>
                <option>United States</option>
                <option>Canada</option>
                <option>United Kingdom</option>
                <option>Australia</option>
              </select>
            </div>

            {/* Error Example */}
            <div>
              <label
                className="block text-sm font-medium mb-2"
                style={{ color: colors.primary }}
              >
                Company Website
              </label>
              <input
                type="url"
                placeholder="https://example.com"
                defaultValue="invalid-url"
                className="w-full px-4 py-3 rounded-lg outline-none"
                style={{
                  backgroundColor: colors.background,
                  border: `2px solid ${colors.accentSoft}`,
                  color: colors.primary,
                }}
              />
              <p className="text-sm mt-1" style={{ color: colors.accentSoft }}>
                Please enter a valid URL starting with http:// or https://
              </p>
            </div>

            {/* Checkbox */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                className="mt-1 w-5 h-5 rounded cursor-pointer"
                style={{ accentColor: colors.accent }}
                defaultChecked
              />
              <label style={{ color: colors.secondary }}>
                I agree to receive updates and marketing communications.
                You can unsubscribe at any time.
              </label>
            </div>

            {/* Buttons */}
            <div className="flex items-center justify-between pt-6">
              <button
                type="button"
                className="px-6 py-3 rounded-lg font-medium transition-all"
                style={{
                  backgroundColor: 'transparent',
                  color: colors.secondary,
                  border: `2px solid ${colors.secondary}40`,
                }}
              >
                Back
              </button>
              <button
                type="submit"
                className="px-8 py-3 rounded-lg font-semibold shadow-md transition-all hover:shadow-lg"
                style={{
                  backgroundColor: colors.primary,
                  color: colors.background,
                }}
              >
                Continue
              </button>
            </div>
          </form>
        </div>
      </main>

      {/* Help Footer */}
      <footer
        className="px-8 py-4 text-center"
        style={{
          backgroundColor: `${colors.primary}05`,
          borderTop: `1px solid ${colors.primary}15`,
        }}
      >
        <p style={{ color: colors.secondary }}>
          Need help?{' '}
          <span
            className="cursor-pointer underline"
            style={{ color: colors.accent }}
          >
            Contact support
          </span>
        </p>
      </footer>
    </div>
  );
}
