import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  ArrowLeft, 
  Loader2, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  Brain,
  BarChart3
} from 'lucide-react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  Line,
} from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Simulation {
  id: number;
  name: string;
  asset_symbol: string;
  asset_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress_percent: number;
  current_step: number;
  total_steps: number;
  created_at: string;
  error_message?: string;
  results?: {
    predictions: Array<{
      date: string;
      predicted_price: number;
      lower_bound: number;
      upper_bound: number;
      math_model_prediction?: number;
    }>;
    sentiment_history: Array<{
      step: number;
      bullish_percent: number;
      bearish_percent: number;
      neutral_percent: number;
    }>;
    final_price_prediction: number;
    price_change_percent: number;
    key_factors: string[];
    top_agents: Array<{
      id: number;
      name: string;
      avatar_type: string;
      personality: string;
      current_decision: string;
      current_confidence: number;
      total_return: number;
    }>;
  };
}

const fetchSimulation = async (id: string): Promise<Simulation> => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/simulations/${id}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Failed to fetch simulation');
  return response.json();
};

function StatusBadge({ status, progress }: { status: Simulation['status']; progress: number }) {
  const configs = {
    pending: { icon: Clock, color: 'text-yellow-500', bg: 'bg-yellow-500/10', label: 'Pending' },
    running: { icon: Activity, color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'Running' },
    completed: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10', label: 'Completed' },
    failed: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10', label: 'Failed' },
    cancelled: { icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-500/10', label: 'Cancelled' },
  };
  
  const config = configs[status];
  const Icon = config.icon;
  
  return (
    <div className="flex items-center gap-2">
      <Badge variant="secondary" className={`${config.bg} ${config.color} border-0`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
      {status === 'running' && (
        <span className="text-sm text-muted-foreground">{progress.toFixed(0)}%</span>
      )}
    </div>
  );
}

function AgentAvatar({ type }: { type: string }) {
  const colors: Record<string, string> = {
    fish: 'bg-blue-500',
    dolphin: 'bg-cyan-500',
    whale: 'bg-indigo-500',
    octopus: 'bg-purple-500',
    turtle: 'bg-green-500',
    seahorse: 'bg-pink-500',
  };
  
  return (
    <Avatar className="h-10 w-10">
      <AvatarFallback className={`${colors[type] || 'bg-blue-500'} text-white text-xs`}>
        {type.charAt(0).toUpperCase()}
      </AvatarFallback>
    </Avatar>
  );
}

export default function SimulationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: simulation, isLoading, refetch } = useQuery({
    queryKey: ['simulation', id],
    queryFn: () => fetchSimulation(id!),
    refetchInterval: (query) => 
      query.state.data?.status === 'running' ? 2000 : false,
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!id) return;
    
    const wsUrl = API_URL.replace('http', 'ws');
    const socket = new WebSocket(`${wsUrl}/simulations/${id}/ws`);
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === 'completed') {
        refetch();
        toast.success('Simulation completed!');
      }
    };
    
    return () => {
      socket.close();
    };
  }, [id, refetch]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-[#0088CC]" />
      </div>
    );
  }

  if (!simulation) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Simulation not found</p>
        <Button onClick={() => navigate('/dashboard')} className="mt-4">
          Back to Dashboard
        </Button>
      </div>
    );
  }

  const isRunning = simulation.status === 'running';
  const isCompleted = simulation.status === 'completed';
  const results = simulation.results;

  // Prepare chart data
  const predictionData = results?.predictions.map(p => ({
    date: new Date(p.date).toLocaleDateString(),
    predicted: p.predicted_price,
    lower: p.lower_bound,
    upper: p.upper_bound,
    math: p.math_model_prediction,
  })) || [];

  const sentimentData = results?.sentiment_history.map(s => ({
    step: s.step,
    bullish: s.bullish_percent,
    bearish: s.bearish_percent,
    neutral: s.neutral_percent,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{simulation.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-muted-foreground">
                {simulation.asset_symbol} • {simulation.asset_type === 'crypto' ? 'Crypto' : 'Stock'}
              </span>
              <StatusBadge status={simulation.status} progress={simulation.progress_percent} />
            </div>
          </div>
        </div>
      </div>

      {/* Progress */}
      {isRunning && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Simulation Progress</span>
                <span>{simulation.progress_percent.toFixed(1)}%</span>
              </div>
              <Progress value={simulation.progress_percent} className="h-2" />
              <p className="text-sm text-muted-foreground">
                Step {simulation.current_step} of {simulation.total_steps}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {isCompleted && results && (
        <Tabs defaultValue="predictions" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto">
            <TabsTrigger value="predictions">Predictions</TabsTrigger>
            <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
            <TabsTrigger value="agents">Top Agents</TabsTrigger>
            <TabsTrigger value="factors">Key Factors</TabsTrigger>
          </TabsList>

          {/* Predictions Tab */}
          <TabsContent value="predictions" className="space-y-6">
            {/* Summary Cards */}
            <div className="grid md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-6">
                  <p className="text-sm text-muted-foreground">Final Prediction</p>
                  <p className="text-2xl font-bold mt-1">
                    ${results.final_price_prediction.toFixed(2)}
                  </p>
                  <p className={`text-sm mt-1 ${results.price_change_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {results.price_change_percent >= 0 ? '+' : ''}{results.price_change_percent.toFixed(2)}%
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <p className="text-sm text-muted-foreground">Confidence Range</p>
                  <p className="text-lg font-medium mt-1">
                    ${results.predictions[results.predictions.length - 1]?.lower_bound.toFixed(2)} - 
                    ${results.predictions[results.predictions.length - 1]?.upper_bound.toFixed(2)}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <p className="text-sm text-muted-foreground">Prediction Days</p>
                  <p className="text-2xl font-bold mt-1">{results.predictions.length}</p>
                </CardContent>
              </Card>
            </div>

            {/* Price Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Price Prediction
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={predictionData}>
                      <defs>
                        <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#0088CC" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#0088CC" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="upper"
                        stroke="none"
                        fill="url(#colorConfidence)"
                      />
                      <Area
                        type="monotone"
                        dataKey="lower"
                        stroke="none"
                        fill="transparent"
                      />
                      <Line
                        type="monotone"
                        dataKey="predicted"
                        stroke="#0088CC"
                        strokeWidth={2}
                        dot={false}
                      />
                      {predictionData[0]?.math && (
                        <Line
                          type="monotone"
                          dataKey="math"
                          stroke="#00A3FF"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                      )}
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sentiment Tab */}
          <TabsContent value="sentiment">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Agent Sentiment Over Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={sentimentData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis dataKey="step" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="bullish"
                        stackId="1"
                        stroke="#22c55e"
                        fill="#22c55e"
                        fillOpacity={0.6}
                      />
                      <Area
                        type="monotone"
                        dataKey="neutral"
                        stackId="1"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.6}
                      />
                      <Area
                        type="monotone"
                        dataKey="bearish"
                        stackId="1"
                        stroke="#ef4444"
                        fill="#ef4444"
                        fillOpacity={0.6}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Agents Tab */}
          <TabsContent value="agents">
            <div className="grid md:grid-cols-2 gap-4">
              {results.top_agents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover:border-[#0088CC]/30 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-4">
                        <AgentAvatar type={agent.avatar_type} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{agent.name}</h3>
                            <Badge variant="secondary" className="text-xs">
                              {agent.personality}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                            <span className={agent.total_return >= 0 ? 'text-green-500' : 'text-red-500'}>
                              {agent.total_return >= 0 ? '+' : ''}{agent.total_return.toFixed(2)}%
                            </span>
                            <span>Confidence: {(agent.current_confidence * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {agent.current_decision === 'buy' && (
                            <TrendingUp className="w-5 h-5 text-green-500" />
                          )}
                          {agent.current_decision === 'sell' && (
                            <TrendingDown className="w-5 h-5 text-red-500" />
                          )}
                          {agent.current_decision === 'hold' && (
                            <Minus className="w-5 h-5 text-blue-500" />
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </TabsContent>

          {/* Factors Tab */}
          <TabsContent value="factors">
            <Card>
              <CardHeader>
                <CardTitle>Key Influencing Factors</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {results.key_factors.map((factor, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
                    >
                      <div className="w-6 h-6 rounded-full bg-[#0088CC]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs text-[#0088CC] font-medium">{index + 1}</span>
                      </div>
                      <span>{factor}</span>
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Pending/Failed States */}
      {!isRunning && !isCompleted && (
        <Card className="text-center py-12">
          <CardContent>
            {simulation.status === 'pending' ? (
              <>
                <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Simulation Pending</h3>
                <p className="text-muted-foreground">
                  Your simulation is queued and will start shortly...
                </p>
              </>
            ) : simulation.status === 'failed' ? (
              <>
                <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Simulation Failed</h3>
                <p className="text-muted-foreground mb-4">
                  {simulation.error_message || 'An error occurred during the simulation'}
                </p>
                <Button onClick={() => navigate('/simulations/new')}>
                  Try Again
                </Button>
              </>
            ) : null}
          </CardContent>
        </Card>
      )}
    </div>
  );
}