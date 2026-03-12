import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Fish, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await login(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0088CC]/5 via-background to-[#00A3FF]/5" />
      
      {/* Animated orbs */}
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.2, 0.3, 0.2] }}
        transition={{ duration: 8, repeat: Infinity }}
        className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#0088CC]/10 rounded-full blur-3xl"
      />
      <motion.div
        animate={{ scale: [1.2, 1, 1.2], opacity: [0.15, 0.25, 0.15] }}
        transition={{ duration: 10, repeat: Infinity }}
        className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#00A3FF]/10 rounded-full blur-3xl"
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2">
            <Fish className="h-10 w-10 text-[#0088CC]" />
            <span className="text-2xl font-bold bg-gradient-to-r from-[#0088CC] to-[#00A3FF] bg-clip-text text-transparent">
              CrystalFish
            </span>
          </Link>
        </div>

        <Card className="border-border/50 shadow-xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Welcome back</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">Don't have an account? </span>
              <Link to="/register" className="text-[#0088CC] hover:underline font-medium">
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          <Link to="/" className="hover:text-[#0088CC] transition-colors">
            ← Back to home
          </Link>
        </p>
      </motion.div>
    </div>
  );
}