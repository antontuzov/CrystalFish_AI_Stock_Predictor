import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/use-auth';
import { Spinner } from '@/components/ui/spinner';

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Spinner className="text-[#0088CC]" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}