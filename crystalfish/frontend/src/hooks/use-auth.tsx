import { type ReactNode, createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  use_default_models: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => Promise<void>;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored token and validate
    const token = localStorage.getItem('access_token');
    console.log('[AuthProvider] Initial token check:', token ? 'Token exists' : 'No token');
    if (token) {
      fetchUser(token);
    } else {
      // No token - not authenticated, but stop loading
      console.log('[AuthProvider] No token found, setting isLoading=false');
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (token: string) => {
    console.log('[AuthProvider] Fetching user with token...');
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        console.log('[AuthProvider] User fetched successfully:', userData.email);
        setUser(userData);
      } else if (response.status === 401) {
        console.log('[AuthProvider] Token invalid (401), clearing storage');
        // Token invalid or expired, clear storage silently
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      } else {
        console.log('[AuthProvider] Unexpected response status:', response.status);
      }
    } catch (error) {
      console.log('[AuthProvider] Error fetching user:', error);
      // Silently handle errors - user just isn't authenticated
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      // Always stop loading, even if auth fails
      console.log('[AuthProvider] Setting isLoading=false');
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    console.log('[AuthProvider] Login attempt for:', email);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        console.log('[AuthProvider] Login failed:', error);
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      console.log('[AuthProvider] Login successful, storing tokens');
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      setUser(data.user);
      setIsLoading(false);
      console.log('[AuthProvider] User state set, isLoading=false');
      return data;
    } catch (error) {
      console.log('[AuthProvider] Login error:', error);
      toast.error(error instanceof Error ? error.message : 'Login failed');
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password, 
          full_name: fullName 
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      toast.success('Account created! Please log in.');
      return true;
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Registration failed');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    toast.info('Logged out');
    navigate('/login');
  };

  const getToken = () => {
    return localStorage.getItem('access_token');
  };

  const updateUser = async (data: Partial<User>) => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        toast.success('Profile updated');
      }
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateUser,
        getToken,
      }}
    >
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
