/**
 * Component Generator Page - Generate styled components using AI.
 */
import { useState, useEffect } from 'react';
import { useSession } from '@/contexts/SessionContext';
import { Button } from '@/components/ui/shadcn/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/shadcn/Card';
import { api } from '@/services/api';
import NavBar from '@/components/NavBar';

const COMPONENT_TYPES = [
  { value: 'button', label: 'Button', description: 'Primary, secondary, or destructive buttons' },
  { value: 'input', label: 'Input', description: 'Text inputs, selects, and form fields' },
  { value: 'card', label: 'Card', description: 'Content cards and containers' },
  { value: 'modal', label: 'Modal', description: 'Dialogs and overlays' },
  { value: 'navigation', label: 'Navigation', description: 'Nav bars and menus' },
  { value: 'form', label: 'Form', description: 'Complete form layouts' },
  { value: 'feedback', label: 'Feedback', description: 'Toasts, alerts, notifications' },
];

const VARIANTS = {
  button: ['primary', 'secondary', 'destructive', 'ghost', 'outline'],
  input: ['default', 'with-label', 'with-error', 'textarea', 'select'],
  card: ['default', 'with-header', 'interactive', 'pricing'],
  modal: ['alert', 'confirm', 'form', 'fullscreen'],
  navigation: ['horizontal', 'vertical', 'sidebar', 'mobile'],
  form: ['login', 'signup', 'contact', 'settings'],
  feedback: ['toast', 'alert', 'banner', 'loading'],
};

const OUTPUT_FORMATS = [
  { value: 'react', label: 'React + Tailwind' },
  { value: 'html', label: 'Plain HTML + CSS' },
  { value: 'vue', label: 'Vue 3' },
];

export default function GeneratorPage() {
  const { sessions, loadSessions } = useSession();
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [componentType, setComponentType] = useState<string>('button');
  const [variant, setVariant] = useState<string>('primary');
  const [outputFormat, setOutputFormat] = useState<string>('react');
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedCode, setGeneratedCode] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const handleGenerate = async () => {
    if (!selectedSession) {
      setError('Please select a style profile');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.generateComponent({
        session_id: selectedSession,
        component_type: componentType,
        variant,
        output_format: outputFormat,
        custom_prompt: customPrompt || undefined,
      });
      setGeneratedCode(response.code);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (generatedCode) {
      await navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const availableVariants = VARIANTS[componentType as keyof typeof VARIANTS] || ['default'];

  // Extract inline styles from generated code for preview
  const extractStylesForPreview = (): { style: React.CSSProperties; className: string } | null => {
    if (!generatedCode) return null;

    // Try to extract style={{ ... }} object
    const styleMatch = generatedCode.match(/style=\{\{([^}]+)\}\}/);
    const classMatch = generatedCode.match(/className="([^"]+)"/);

    let style: React.CSSProperties = {};
    if (styleMatch) {
      try {
        // Parse the style object (it's already JS object notation)
        const styleStr = styleMatch[1]
          .replace(/'/g, '"')
          .replace(/,\s*}/g, '}')
          .replace(/(\w+):/g, '"$1":');
        style = JSON.parse(`{${styleStr}}`);
      } catch {
        // If parsing fails, extract individual properties
        const bgMatch = generatedCode.match(/backgroundColor:\s*['"]([^'"]+)['"]/);
        const colorMatch = generatedCode.match(/color:\s*['"]([^'"]+)['"]/);
        const fontMatch = generatedCode.match(/fontFamily:\s*['"]([^'"]+)['"]/);
        if (bgMatch) style.backgroundColor = bgMatch[1];
        if (colorMatch) style.color = colorMatch[1];
        if (fontMatch) style.fontFamily = fontMatch[1];
      }
    }

    return {
      style,
      className: classMatch?.[1] || '',
    };
  };

  const previewStyles = extractStylesForPreview();

  // Render preview based on component type
  const renderPreview = () => {
    if (!previewStyles) {
      return (
        <div className="text-gray-400 text-center">
          <p>Generate a component to see the preview</p>
        </div>
      );
    }

    const { style, className } = previewStyles;
    const baseClassName = className.split(' ').filter(c =>
      c.includes('px-') || c.includes('py-') || c.includes('rounded') ||
      c.includes('font-') || c.includes('text-') || c.includes('shadow') ||
      c.includes('border') || c.includes('transition')
    ).join(' ');

    switch (componentType) {
      case 'button':
        return (
          <button className={baseClassName} style={style}>
            {variant === 'destructive' ? 'Delete Item' : 'Click Me'}
          </button>
        );
      case 'input':
        return (
          <div className="w-full max-w-sm">
            <label className="block text-sm font-medium mb-1" style={{ color: style.color }}>
              Email Address
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              className={baseClassName + ' w-full'}
              style={style}
            />
          </div>
        );
      case 'card':
        return (
          <div className={baseClassName + ' p-6 max-w-sm'} style={style}>
            <h3 className="font-semibold mb-2" style={{ fontFamily: style.fontFamily }}>
              Card Title
            </h3>
            <p className="text-sm opacity-80">
              This is a preview of your generated card component with your style applied.
            </p>
          </div>
        );
      case 'feedback':
        return (
          <div className={baseClassName + ' px-4 py-3 max-w-sm'} style={style}>
            <span className="mr-2">✓</span>
            <span>Operation completed successfully!</span>
          </div>
        );
      default:
        return (
          <div className={baseClassName + ' p-4'} style={style}>
            Preview: {componentType} ({variant})
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />

      {/* Page Header */}
      <div className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="font-semibold text-lg">Component Generator</h1>
          <p className="text-sm text-gray-500">
            Generate styled components using your TasteMaker profile
          </p>
        </div>
      </div>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Configuration Section */}
          <div className="space-y-6">
            {/* Session Selector */}
            <Card>
              <CardHeader>
                <CardTitle>1. Select Style Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  className="w-full px-3 py-2 border rounded-lg"
                  value={selectedSession || ''}
                  onChange={(e) => setSelectedSession(e.target.value || null)}
                  agent-handle="generator-select-session"
                >
                  <option value="">Select a session...</option>
                  {sessions.map((session) => (
                    <option key={session.id} value={session.id}>
                      {session.name}
                    </option>
                  ))}
                </select>
              </CardContent>
            </Card>

            {/* Component Type */}
            <Card>
              <CardHeader>
                <CardTitle>2. Choose Component</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {COMPONENT_TYPES.map((comp) => (
                    <button
                      key={comp.value}
                      className={`p-3 text-left rounded-lg border transition-colors ${
                        componentType === comp.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setComponentType(comp.value);
                        setVariant(VARIANTS[comp.value as keyof typeof VARIANTS]?.[0] || 'default');
                      }}
                      agent-handle={`generator-type-${comp.value}`}
                    >
                      <p className="font-medium">{comp.label}</p>
                      <p className="text-xs text-gray-500">{comp.description}</p>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Variant Selector */}
            <Card>
              <CardHeader>
                <CardTitle>3. Select Variant</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {availableVariants.map((v) => (
                    <button
                      key={v}
                      className={`px-4 py-2 rounded-lg border transition-colors capitalize ${
                        variant === v
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setVariant(v)}
                      agent-handle={`generator-variant-${v}`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Output Format */}
            <Card>
              <CardHeader>
                <CardTitle>4. Output Format</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  {OUTPUT_FORMATS.map((fmt) => (
                    <button
                      key={fmt.value}
                      className={`px-4 py-2 rounded-lg border transition-colors ${
                        outputFormat === fmt.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setOutputFormat(fmt.value)}
                      agent-handle={`generator-format-${fmt.value}`}
                    >
                      {fmt.label}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Custom Prompt */}
            <Card>
              <CardHeader>
                <CardTitle>5. Custom Instructions (Optional)</CardTitle>
                <CardDescription>
                  Add specific requirements for the generated component
                </CardDescription>
              </CardHeader>
              <CardContent>
                <textarea
                  className="w-full px-3 py-2 border rounded-lg h-24 resize-none"
                  placeholder="e.g., Include an icon on the left, add hover animation..."
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  agent-handle="generator-custom-prompt"
                />
              </CardContent>
            </Card>

            {/* Generate Button */}
            <Button
              className="w-full"
              size="lg"
              onClick={handleGenerate}
              disabled={loading || !selectedSession}
              agent-handle="generator-button-generate"
            >
              {loading ? 'Generating...' : 'Generate Component'}
            </Button>

            {error && (
              <div className="p-4 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}
          </div>

          {/* Output Section */}
          <div className="space-y-4">
            {/* Preview Card */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Live Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div
                  className="flex items-center justify-center min-h-[120px] bg-gray-100 rounded-lg p-8 border-2 border-dashed border-gray-200"
                  style={{
                    backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
                    backgroundSize: '16px 16px',
                  }}
                >
                  {renderPreview()}
                </div>
              </CardContent>
            </Card>

            {/* Code Card */}
            <Card className="flex-1">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Generated Code</CardTitle>
                  {generatedCode && (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopy}
                        agent-handle="generator-button-copy"
                      >
                        {copied ? 'Copied!' : 'Copy'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleGenerate}
                        disabled={loading}
                        agent-handle="generator-button-regenerate"
                      >
                        Regenerate
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {generatedCode ? (
                  <pre
                    className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm h-[400px] overflow-y-auto"
                    agent-handle="generator-code-output"
                  >
                    <code>{generatedCode}</code>
                  </pre>
                ) : (
                  <div className="flex items-center justify-center h-[200px] text-gray-400 bg-gray-100 rounded-lg">
                    <div className="text-center">
                      <p className="text-lg mb-2">No code generated yet</p>
                      <p className="text-sm">
                        Configure your component and click Generate
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
