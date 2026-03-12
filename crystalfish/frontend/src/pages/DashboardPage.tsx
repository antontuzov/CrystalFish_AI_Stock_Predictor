import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  PlusCircle, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Clock,
  Fish,
  BarChart3,
  Activity
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Simulation {
  id: number;
  name: string;
  asset_symbol: string;
  asset_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress_percent: number;
  created_at: string;
  completed_at?: string;
}

const fetchSimulations = async (): Promise<Simulation[]> => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/simulations`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error('Failed to fetch simulations');
  return response.json();
};

function StatusBadge({ status }: { status: Simulation['status'] }) {
  const variants = {
    pending: { bg: 'bg-yellow-500/10', text: 'text-yellow-500', icon: Clock },
    running: { bg: 'bg-blue-500/10', text: 'text-blue-500', icon: Activity },
    completed: { bg: 'bg-green-500/10', text: 'text-green-500', icon: TrendingUp },
    failed: { bg: 'bg-red-500/10', text: 'text-red-500', icon: TrendingDown },
    cancelled: { bg: 'bg-gray-500/10', text: 'text-gray-500', icon: Minus },
  };
  
  const variant = variants[status];
  const Icon = variant.icon;
  
  return (
    <Badge variant="secondary" className={`${variant.bg} ${variant.text} border-0`}>
      <Icon className="w-3 h-3 mr-1" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}

function SimulationCard({ simulation, index }: { simulation: Simulation; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
    >
      <Link to={`/simulations/${simulation.id}`}>
        <Card className="hover:border-[#0088CC]/30 transition-colors cursor-pointer group">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold group-hover:text-[#0088CC] transition-colors">
                  {simulation.name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {simulation.asset_symbol} • {simulation.asset_type === 'crypto' ? 'Crypto' : 'Stock'}
                </p>
              </div>
              <StatusBadge status={simulation.status} />
            </div>
            
            {simulation.status === 'running' && (
              <div className="space-y-2">
                <Progress value={simulation.progress_percent} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  {simulation.progress_percent.toFixed(0)}% complete
                </p>
              </div>
            )}
            
            <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
              <span>Created {new Date(simulation.created_at).toLocaleDateString()}</span>
              {simulation.completed_at && (
                <span>Completed {new Date(simulation.completed_at).toLocaleDateString()}</span>
              )}
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}

function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend 
}: { 
  title: string; 
  value: string; 
  icon: React.ElementType; 
  trend?: string;
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {trend && (
              <p className="text-xs text-green-500 mt-1">{trend}</p>
            )}
          </div>
          <div className="w-12 h-12 rounded-xl bg-[#0088CC]/10 flex items-center justify-center">
            <Icon className="w-6 h-6 text-[#0088CC]" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: simulations, isLoading } = useQuery({
    queryKey: ['simulations'],
    queryFn: fetchSimulations,
    refetchInterval: 5000, // Refetch every 5 seconds for live updates
  });

  const runningSimulations = simulations?.filter(s => s.status === 'running') || [];
  const completedSimulations = simulations?.filter(s => s.status === 'completed') || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Manage your predictions and simulations</p>
        </div>
        <Link to="/simulations/new">
          <Button className="bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90">
            <PlusCircle className="mr-2 h-4 w-4" />
            New Simulation
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-4">
        <StatCard
          title="Total Simulations"
          value={String(simulations?.length || 0)}
          icon={BarChart3}
          trend="+12% this month"
        />
        <StatCard
          title="Running"
          value={String(runningSimulations.length)}
          icon={Activity}
        />
        <StatCard
          title="Completed"
          value={String(completedSimulations.length)}
          icon={Fish}
        />
      </div>

      {/* Running Simulations */}
      {runningSimulations.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            Running Simulations
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {runningSimulations.map((sim, index) => (
              <SimulationCard key={sim.id} simulation={sim} index={index} />
            ))}
          </div>
        </div>
      )}

      {/* Recent Simulations */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Simulations</h2>
        {isLoading ? (
          <div className="grid md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-4 h-32" />
              </Card>
            ))}
          </div>
        ) : simulations && simulations.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-4">
            {simulations
              .filter(s => s.status !== 'running')
              .slice(0, 6)
              .map((sim, index) => (
                <SimulationCard key={sim.id} simulation={sim} index={index} />
              ))}
          </div>
        ) : (
          <Card className="text-center py-12">
            <CardContent>
              <Fish className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No simulations yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first simulation to start predicting market movements
              </p>
              <Link to="/simulations/new">
                <Button className="bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90">
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Create Simulation
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}