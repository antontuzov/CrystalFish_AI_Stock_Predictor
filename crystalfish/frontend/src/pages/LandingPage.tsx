import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Fish,
  Brain,
  TrendingUp,
  BarChart3,
  Zap,
  Shield,
  Globe,
  ChevronRight,
  Sparkles,
  Cpu
} from 'lucide-react';

// Feature card component
function FeatureCard({
  icon: Icon,
  title,
  description
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) {
  return (
    <div className="group relative p-6 rounded-2xl bg-card/50 border border-border/50 hover:border-[#0088CC]/30 transition-all duration-300">
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#0088CC]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative">
        <div className="w-12 h-12 rounded-xl bg-[#0088CC]/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
          <Icon className="w-6 h-6 text-[#0088CC]" />
        </div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground text-sm">{description}</p>
      </div>
    </div>
  );
}

// Step card component
function StepCard({
  number,
  title,
  description
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-4 items-start">
      <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-[#0088CC] to-[#00A3FF] flex items-center justify-center text-white font-bold text-lg">
        {number}
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#0088CC]/5 via-background to-background" />

        {/* Hero content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#0088CC]/10 border border-[#0088CC]/20 mb-8">
            <Sparkles className="w-4 h-4 text-[#0088CC]" />
            <span className="text-sm text-[#0088CC] font-medium">AI-Powered Market Prediction</span>
          </div>

          {/* Main heading */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-[#0088CC] via-[#00A3FF] to-[#0088CC] bg-clip-text text-transparent">
              Predict the Markets
            </span>
            <br />
            <span className="text-foreground">with Swarm Intelligence</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            CrystalFish combines hundreds of AI agents with advanced mathematical models
            to forecast stock and cryptocurrency prices with unprecedented accuracy.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button
                size="lg"
                className="bg-gradient-to-r from-[#0088CC] to-[#00A3FF] hover:opacity-90 text-white px-8 py-6 text-lg rounded-xl"
              >
                Start Predicting
                <ChevronRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button
                size="lg"
                variant="outline"
                className="border-[#0088CC]/30 hover:bg-[#0088CC]/10 px-8 py-6 text-lg rounded-xl"
              >
                Sign In
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
            <div>
              <div className="text-3xl font-bold text-[#0088CC]">500+</div>
              <div className="text-sm text-muted-foreground">AI Agents</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-[#0088CC]">95%</div>
              <div className="text-sm text-muted-foreground">Accuracy</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-[#0088CC]">24/7</div>
              <div className="text-sm text-muted-foreground">Monitoring</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Three simple steps to harness the power of AI swarm intelligence for your trades
            </p>
          </div>

          <div className="max-w-2xl mx-auto space-y-12">
            <StepCard
              number="1"
              title="Upload Your Data"
              description="Import historical price data, market news, or connect to live feeds from Yahoo Finance or CoinGecko."
            />
            <StepCard
              number="2"
              title="Run Swarm Simulation"
              description="Launch hundreds of AI agents with different personalities to analyze the market and make predictions."
            />
            <StepCard
              number="3"
              title="Get Predictions"
              description="Receive detailed forecasts with confidence intervals, sentiment analysis, and actionable insights."
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Advanced tools and algorithms working together for accurate predictions
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={Brain}
              title="Multi-Agent AI"
              description="Hundreds of intelligent agents with unique personalities analyze the market from every angle."
            />
            <FeatureCard
              icon={BarChart3}
              title="Math Models"
              description="ARIMA, GARCH, Prophet, and Prophet ensembles provide statistical baselines."
            />
            <FeatureCard
              icon={TrendingUp}
              title="Technical Analysis"
              description="RSI, MACD, Bollinger Bands, and custom indicators inform agent decisions."
            />
            <FeatureCard
              icon={Zap}
              title="Real-time Updates"
              description="Watch simulations progress live with WebSocket updates and detailed logs."
            />
            <FeatureCard
              icon={Shield}
              title="Risk Management"
              description="Confidence intervals and risk metrics help you make informed decisions."
            />
            <FeatureCard
              icon={Globe}
              title="Multi-Asset Support"
              description="Analyze stocks, cryptocurrencies, and forex pairs from global markets."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0088CC] to-[#00A3FF] p-12 text-center">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-64 h-64 bg-white rounded-full blur-3xl" />
              <div className="absolute bottom-0 right-0 w-64 h-64 bg-white rounded-full blur-3xl" />
            </div>

            <div className="relative z-10">
              <Cpu className="w-16 h-16 text-white/80 mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Ready to Start Predicting?
              </h2>
              <p className="text-white/80 max-w-xl mx-auto mb-8">
                Join thousands of traders using CrystalFish to make smarter investment decisions.
                Start your first simulation in minutes.
              </p>
              <Link to="/register">
                <Button
                  size="lg"
                  variant="secondary"
                  className="bg-white text-[#0088CC] hover:bg-white/90 px-8 py-6 text-lg rounded-xl"
                >
                  Create Free Account
                  <ChevronRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Fish className="h-8 w-8 text-[#0088CC]" />
              <span className="text-xl font-bold">CrystalFish</span>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground">
              <Link to="/" className="hover:text-[#0088CC] transition-colors">Home</Link>
              <Link to="/login" className="hover:text-[#0088CC] transition-colors">Login</Link>
              <Link to="/register" className="hover:text-[#0088CC] transition-colors">Register</Link>
            </div>
            <div className="text-sm text-muted-foreground">
              © 2024 CrystalFish. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}