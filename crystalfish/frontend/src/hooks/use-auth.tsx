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
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for stored token and validate
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token invalid, clear storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
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
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      setUser(data.user);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
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
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      toast.success('Account created! Please log in.');
      navigate('/login');
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
    navigate('/');
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