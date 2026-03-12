import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { 
  User, 
  Key, 
  Save, 
  Loader2,
  ExternalLink
} from 'lucide-react';

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [openrouterKey, setOpenrouterKey] = useState('');
  const [useDefaultModels, setUseDefaultModels] = useState(user?.use_default_models ?? true);

  const handleSave = async () => {
    setIsLoading(true);
    try {
      await updateUser({
        full_name: fullName,
        use_default_models: useDefaultModels,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground">Manage your account settings</p>
      </div>

      {/* Profile Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5" />
              Profile Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Avatar and Name */}
            <div className="flex items-center gap-4">
              <Avatar className="h-20 w-20 border-2 border-[#0088CC]/20">
                <AvatarFallback className="bg-[#0088CC]/10 text-[#0088CC] text-2xl">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold text-lg">{user?.full_name || 'User'}</h3>
                <p className="text-muted-foreground">{user?.email}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Member since {new Date(user?.created_at || '').toLocaleDateString()}
                </p>
              </div>
            </div>

            <Separator />

            {/* Edit Form */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <Input
                  id="fullName"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* API Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5" />
              API Configuration
            </CardTitle>
            <CardDescription>
              Configure your OpenRouter API key for custom AI models
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Use Default Models</Label>
                <p className="text-sm text-muted-foreground">
                  Use CrystalFish's free OpenRouter models
                </p>
              </div>
              <Switch
                checked={useDefaultModels}
                onCheckedChange={setUseDefaultModels}
              />
            </div>

            {!useDefaultModels && (
              <div className="space-y-2">
                <Label htmlFor="openrouterKey">OpenRouter API Key</Label>
                <Input
                  id="openrouterKey"
                  type="password"
                  value={openrouterKey}
                  onChange={(e) => setOpenrouterKey(e.target.value)}
                  placeholder="sk-or-..."
                />
                <p className="text-xs text-muted-foreground">
                  Get your API key from{' '}
                  <a 
                    href="https://openrouter.ai/keys" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-[#0088CC] hover:underline inline-flex items-center gap-1"
                  >
                    openrouter.ai
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
        className="flex justify-between"
      >
        <Button variant="outline" onClick={logout} className="text-red-500 hover:text-red-600">
          Log Out
        </Button>
        <Button 
          onClick={handleSave}
          className="bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </motion.div>
    </div>
  );
}