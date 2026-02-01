import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/shadcn/Button';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            TasteMaker
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Extract your UI/UX preferences through simple A/B comparisons.
            Generate style guides that AI coding tools can use to make
            consistent design decisions.
          </p>
          <div className="flex gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate('/register')}
              agent-handle="landing-hero-button-getstarted"
            >
              Get Started
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => navigate('/login')}
              agent-handle="landing-hero-button-login"
            >
              Login
            </Button>
          </div>
        </div>
      </div>

      {/* How it Works Section */}
      <div className="bg-white py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Compare</h3>
              <p className="text-gray-600">
                View pairs of UI components and pick the one you prefer
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary">2</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Extract</h3>
              <p className="text-gray-600">
                Your preferences are analyzed to identify patterns
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary">3</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Refine</h3>
              <p className="text-gray-600">
                Add explicit rules and review extracted preferences
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary">4</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Download</h3>
              <p className="text-gray-600">
                Get a skill package for Claude Code, Cursor, and more
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Features
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-2">Multi-Library Support</h3>
              <p className="text-gray-600">
                Compare components from shadcn/ui, Material UI, and Radix
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-2">Accessibility Built-in</h3>
              <p className="text-gray-600">
                WCAG and Nielsen heuristic rules included by default
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-2">AI-Ready Output</h3>
              <p className="text-gray-600">
                Export as Agent Skills for seamless AI tool integration
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-500">
          <p>TasteMaker v1.0 - Extract your taste, empower your AI</p>
        </div>
      </footer>
    </div>
  );
}
