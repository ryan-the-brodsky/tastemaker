import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { User } from '../types';
import { api } from '../services/api';

interface HealthResponse {
  status: string;
  config: {
    single_user_mode: boolean;
    database_type: string;
    anthropic_api: string;
    background_jobs: string;
  };
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  singleUserMode: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [singleUserMode, setSingleUserMode] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        // First check if we're in single-user mode
        const healthResponse = await fetch('/health');
        if (healthResponse.ok) {
          const health: HealthResponse = await healthResponse.json();
          const isSingleUser = health.config?.single_user_mode ?? false;
          setSingleUserMode(isSingleUser);

          if (isSingleUser) {
            // In single-user mode, try to get user info directly (no auth required)
            try {
              const userData = await api.getMe();
              setUser(userData);
            } catch {
              // If getMe fails, create a synthetic user for display
              // The backend will handle creating the actual user
              setUser({
                id: 'local-user',
                email: 'local@tastemaker.local',
                first_name: 'Local',
                last_name: 'User',
                subscription_tier: 'free',
              });
            }
            setLoading(false);
            return;
          }
        }
      } catch (error) {
        // Health check failed, continue with normal auth flow
        console.warn('Health check failed, using normal auth flow');
      }

      // Normal auth flow (multi-user mode)
      const token = api.getToken();
      if (token) {
        api.getMe()
          .then(setUser)
          .catch(() => {
            api.logout();
          })
          .finally(() => setLoading(false));
      } else {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    setUser(response.user);
  };

  const register = async (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }) => {
    const response = await api.register(data);
    setUser(response.user);
  };

  const logout = () => {
    // In single-user mode, logout doesn't do much
    if (!singleUserMode) {
      api.logout();
    }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, singleUserMode, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
