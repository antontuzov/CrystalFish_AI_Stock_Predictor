import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
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

// Particle background component
function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      opacity: number;
    }> = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createParticles = () => {
      particles = [];
      const count = Math.min(50, Math.floor(window.innerWidth / 30));
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.5 + 0.2,
        });
      }
    };

    const drawParticles = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, i) => {
        // Update position
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 136, 204, ${p.opacity})`;
        ctx.fill();

        // Draw connections
        particles.slice(i + 1).forEach((p2) => {
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 100) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 136, 204, ${0.1 * (1 - dist / 100)})`;
            ctx.stroke();
          }
        });
      });

      animationId = requestAnimationFrame(drawParticles);
    };

    resize();
    createParticles();
    drawParticles();

    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  );
}

// Feature card component
function FeatureCard({ 
  icon: Icon, 
  title, 
  description, 
  delay 
}: { 
  icon: React.ElementType; 
  title: string; 
  description: string; 
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="group relative p-6 rounded-2xl bg-card/50 border border-border/50 hover:border-[#0088CC]/30 transition-all duration-300"
    >
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#0088CC]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative">
        <div className="w-12 h-12 rounded-xl bg-[#0088CC]/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
          <Icon className="w-6 h-6 text-[#0088CC]" />
        </div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground text-sm">{description}</p>
      </div>
    </motion.div>
  );
}

// Step card component
function StepCard({ 
  number, 
  title, 
  description, 
  delay 
}: { 
  number: string; 
  title: string; 
  description: string; 
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="flex gap-4 items-start"
    >
      <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-[#0088CC] to-[#00A3FF] flex items-center justify-center text-white font-bold text-lg">
        {number}
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-muted-foreground">{description}</p>
      </div>
    </motion.div>
  );
}

export default function LandingPage() {
  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 500], [0, 150]);
  const heroOpacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#0088CC]/5 via-background to-background" />
        
        {/* Particle background */}
        <ParticleBackground />
        
        {/* Animated gradient orbs */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#0088CC]/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#00A3FF]/20 rounded-full blur-3xl"
        />

        {/* Hero content */}
        <motion.div 
          style={{ y: heroY, opacity: heroOpacity }}
          className="relative z-10 container mx-auto px-4 text-center"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#0088CC]/10 border border-[#0088CC]/20 mb-8"
          >
            <Sparkles className="w-4 h-4 text-[#0088CC]" />
            <span className="text-sm text-[#0088CC] font-medium">AI-Powered Market Prediction</span>
          </motion.div>

          {/* Main heading */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
          >
            <span className="bg-gradient-to-r from-[#0088CC] via-[#00A3FF] to-[#0088CC] bg-clip-text text-transparent">
              Predict the Markets
            </span>
            <br />
            <span className="text-foreground">with Swarm Intelligence</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
          >
            CrystalFish combines hundreds of AI agents with advanced mathematical models 
            to forecast stock and cryptocurrency prices with unprecedented accuracy.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
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
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto"
          >
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
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-6 h-10 rounded-full border-2 border-[#0088CC]/30 flex justify-center pt-2"
          >
            <motion.div className="w-1.5 h-1.5 rounded-full bg-[#0088CC]" />
          </motion.div>
        </motion.div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Three simple steps to harness the power of AI swarm intelligence for your trades
            </p>
          </motion.div>

          <div className="max-w-2xl mx-auto space-y-12">
            <StepCard
              number="1"
              title="Upload Your Data"
              description="Import historical price data, market news, or connect to live feeds from Yahoo Finance or CoinGecko."
              delay={0}
            />
            <StepCard
              number="2"
              title="Run Swarm Simulation"
              description="Launch hundreds of AI agents with different personalities to analyze the market and make predictions."
              delay={0.1}
            />
            <StepCard
              number="3"
              title="Get Predictions"
              description="Receive detailed forecasts with confidence intervals, sentiment analysis, and actionable insights."
              delay={0.2}
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative bg-muted/30">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Advanced tools and algorithms working together for accurate predictions
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={Brain}
              title="Multi-Agent AI"
              description="Hundreds of intelligent agents with unique personalities analyze the market from every angle."
              delay={0}
            />
            <FeatureCard
              icon={BarChart3}
              title="Math Models"
              description="ARIMA, GARCH, Prophet, and Prophet ensembles provide statistical baselines."
              delay={0.1}
            />
            <FeatureCard
              icon={TrendingUp}
              title="Technical Analysis"
              description="RSI, MACD, Bollinger Bands, and custom indicators inform agent decisions."
              delay={0.2}
            />
            <FeatureCard
              icon={Zap}
              title="Real-time Updates"
              description="Watch simulations progress live with WebSocket updates and detailed logs."
              delay={0.3}
            />
            <FeatureCard
              icon={Shield}
              title="Risk Management"
              description="Confidence intervals and risk metrics help you make informed decisions."
              delay={0.4}
            />
            <FeatureCard
              icon={Globe}
              title="Multi-Asset Support"
              description="Analyze stocks, cryptocurrencies, and forex pairs from global markets."
              delay={0.5}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0088CC] to-[#00A3FF] p-12 text-center"
          >
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
          </motion.div>
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