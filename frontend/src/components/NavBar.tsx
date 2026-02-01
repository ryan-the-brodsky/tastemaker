/**
 * Shared navigation bar component used across all authenticated pages.
 */
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/shadcn/Button';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Sessions' },
  { path: '/generate', label: 'Generate' },
  { path: '/audit', label: 'Audit' },
  { path: '/docs/tml', label: 'Docs' },
];

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname.startsWith('/session/');
    }
    if (path === '/docs/tml') {
      return location.pathname.startsWith('/docs');
    }
    return location.pathname === path;
  };

  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center gap-8">
          <h1
            className="text-xl font-bold cursor-pointer"
            onClick={() => navigate('/dashboard')}
          >
            TasteMaker
          </h1>
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <Button
                key={item.path}
                variant="ghost"
                size="sm"
                onClick={() => navigate(item.path)}
                className={isActive(item.path) ? 'text-gray-900 font-medium' : 'text-gray-600'}
              >
                {item.label}
              </Button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-600">
            {user?.first_name} {user?.last_name}
          </span>
          <Button variant="outline" size="sm" onClick={logout}>
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
}
