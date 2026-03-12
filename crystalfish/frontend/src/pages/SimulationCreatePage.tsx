import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Fish, 
  ArrowLeft, 
  Loader2, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Activity,
  RotateCcw
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const PERSONALITIES = [
  { key: 'bullish', label: 'Bullish', icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-500/10' },
  { key: 'bearish', label: 'Bearish', icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-500/10' },
  { key: 'neutral', label: 'Neutral', icon: Minus, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { key: 'trend_follower', label: 'Trend Follower', icon: Activity, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { key: 'contrarian', label: 'Contrarian', icon: RotateCcw, color: 'text-orange-500', bg: 'bg-orange-500/10' },
];

export default function SimulationCreatePage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  
  // Form state
  const [name, setName] = useState('');
  const [assetSymbol, setAssetSymbol] = useState('');
  const [assetType, setAssetType] = useState<'crypto' | 'stock'>('crypto');
  const [timeHorizon, setTimeHorizon] = useState(7);
  const [agentsCount, setAgentsCount] = useState(100);
  const [confidenceLevel, setConfidenceLevel] = useState(0.95);
  const [dataSource, setDataSource] = useState<'yahoo' | 'coingecko'>('yahoo');
  
  // Personality distribution
  const [personalityDist, setPersonalityDist] = useState({
    bullish: 25,
    bearish: 25,
    neutral: 25,
    trend_follower: 15,
    contrarian: 10,
  });

  const updatePersonality = (key: string, value: number) => {
    setPersonalityDist(prev => ({ ...prev, [key]: value }));
  };

  const normalizeDistribution = () => {
    const total = Object.values(personalityDist).reduce((a, b) => a + b, 0);
    if (total === 0) return;
    
    const normalized: { [key: string]: number } = {};
    Object.entries(personalityDist).forEach(([key, value]) => {
      normalized[key] = Math.round((value / total) * 100);
    });
    setPersonalityDist(normalized as any);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      
      // Normalize distribution to ensure it sums to 100
      const normalizedDist: { [key: string]: number } = {};
      Object.entries(personalityDist).forEach(([key, value]) => {
        normalizedDist[key] = value / 100;
      });

      const response = await fetch(`${API_URL}/simulations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name,
          asset_symbol: assetSymbol.toUpperCase(),
          asset_type: assetType,
          time_horizon_days: timeHorizon,
          agents_count: agentsCount,
          confidence_level: confidenceLevel,
          personality_distribution: normalizedDist,
          data_source: dataSource,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create simulation');
      }

      const data = await response.json();
      toast.success('Simulation created successfully!');
      navigate(`/simulations/${data.id}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create simulation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">New Simulation</h1>
          <p className="text-muted-foreground">Configure your AI swarm prediction</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Basic Settings</CardTitle>
              <CardDescription>Configure the asset and prediction parameters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Simulation Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Bitcoin 7-Day Forecast"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="assetSymbol">Asset Symbol</Label>
                  <Input
                    id="assetSymbol"
                    placeholder="e.g., BTC, ETH, AAPL"
                    value={assetSymbol}
                    onChange={(e) => setAssetSymbol(e.target.value.toUpperCase())}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Asset Type</Label>
                  <Select value={assetType} onValueChange={(v) => setAssetType(v as 'crypto' | 'stock')}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="crypto">Cryptocurrency</SelectItem>
                      <SelectItem value="stock">Stock</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Data Source</Label>
                  <Select value={dataSource} onValueChange={(v) => setDataSource(v as 'yahoo' | 'coingecko')}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yahoo">Yahoo Finance</SelectItem>
                      <SelectItem value="coingecko">CoinGecko</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Time Horizon (days)</Label>
                  <div className="flex items-center gap-4">
                    <Slider
                      value={[timeHorizon]}
                      onValueChange={(v) => setTimeHorizon(v[0])}
                      min={1}
                      max={90}
                      step={1}
                      className="flex-1"
                    />
                    <span className="w-12 text-right font-medium">{timeHorizon}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Agent Configuration */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Agent Configuration</CardTitle>
              <CardDescription>Customize your AI swarm</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Number of Agents: {agentsCount}</Label>
                <Slider
                  value={[agentsCount]}
                  onValueChange={(v) => setAgentsCount(v[0])}
                  min={10}
                  max={500}
                  step={10}
                />
                <p className="text-xs text-muted-foreground">
                  More agents provide better coverage but take longer to run
                </p>
              </div>

              <div className="space-y-2">
                <Label>Confidence Level: {(confidenceLevel * 100).toFixed(0)}%</Label>
                <Slider
                  value={[confidenceLevel * 100]}
                  onValueChange={(v) => setConfidenceLevel(v[0] / 100)}
                  min={50}
                  max={99}
                  step={1}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Personality Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Personality Distribution</CardTitle>
                  <CardDescription>Define the mix of agent personalities</CardDescription>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={normalizeDistribution}>
                  Normalize
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {PERSONALITIES.map((p) => (
                <div key={p.key} className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg ${p.bg} flex items-center justify-center`}>
                    <p.icon className={`w-5 h-5 ${p.color}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{p.label}</span>
                      <span className="text-sm text-muted-foreground">{personalityDist[p.key as keyof typeof personalityDist]}%</span>
                    </div>
                    <Slider
                      value={[personalityDist[p.key as keyof typeof personalityDist]]}
                      onValueChange={(v) => updatePersonality(p.key, v[0])}
                      min={0}
                      max={100}
                      step={5}
                    />
                  </div>
                </div>
              ))}
              
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Total Distribution</span>
                  <Badge 
                    variant={Object.values(personalityDist).reduce((a, b) => a + b, 0) === 100 ? 'default' : 'secondary'}
                  >
                    {Object.values(personalityDist).reduce((a, b) => a + b, 0)}%
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Submit */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          className="flex justify-end gap-4"
        >
          <Button type="button" variant="outline" onClick={() => navigate('/dashboard')}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            className="bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Fish className="mr-2 h-4 w-4" />
                Start Simulation
              </>
            )}
          </Button>
        </motion.div>
      </form>
    </div>
  );
}