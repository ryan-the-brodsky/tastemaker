/**
 * Documentation layout with sidebar navigation.
 */
import { Outlet, Link, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/docs/tml', label: 'TML Specification' },
  { path: '/docs/claude-code', label: 'Claude Code Integration' },
  { path: '/docs/cursor', label: 'Cursor Integration' },
];

export default function DocsLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="text-gray-500 hover:text-gray-700">
              &larr; Back
            </Link>
            <h1 className="font-semibold text-lg">TasteMaker Documentation</h1>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8 flex gap-8">
        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0">
          <nav className="sticky top-8 space-y-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-4 py-2 rounded-lg transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>

        {/* Content */}
        <main className="flex-1 bg-white rounded-xl shadow-sm p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
