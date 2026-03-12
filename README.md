# CrystalFish

**AI Swarm Intelligence for Stock/Crypto Prediction**

CrystalFish is a multi-agent swarm intelligence engine that combines hundreds of AI agents with advanced mathematical models to forecast stock market and cryptocurrency prices.

![CrystalFish](https://img.shields.io/badge/CrystalFish-v1.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6)

## Features

- **Multi-Agent AI Swarm**: Hundreds of intelligent agents with unique personalities analyze markets
- **Advanced Math Models**: ARIMA, GARCH, Prophet, and ensemble forecasting
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and custom indicators
- **Real-time Updates**: WebSocket-powered live simulation progress
- **Interactive Dashboard**: Beautiful charts and visualizations
- **Agent Chat**: Talk to individual agents to understand their reasoning

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Async task processing
- **OpenRouter** - Free AI model access (Mistral, Llama)

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Framer Motion** - Animations
- **Recharts** - Data visualization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) OpenRouter API key for AI models

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crystalfish.git
cd crystalfish
```

2. Create environment file:
```bash
cp backend/.env.example backend/.env
```

3. Edit `backend/.env` with your settings (optional):
```bash
# Add your OpenRouter API key for better AI models
OPENROUTER_API_KEY=your-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
crystalfish/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   │   ├── agent.py      # Agent class
│   │   │   ├── simulation.py # Simulation runner
│   │   │   ├── math_models.py # ARIMA, GARCH, etc.
│   │   │   └── openrouter.py  # LLM client
│   │   └── worker/       # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   └── utils/        # Utilities
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## How It Works

1. **Upload Data**: Import historical prices or use live feeds
2. **Configure Simulation**: Set asset, time horizon, agent count
3. **Run Swarm**: Hundreds of AI agents analyze and predict
4. **Get Results**: View predictions, sentiment, and key factors

## Agent Personalities

- **Bullish**: Optimistic, growth-focused
- **Bearish**: Cautious, risk-averse
- **Neutral**: Balanced, data-driven
- **Trend Follower**: Technical, momentum-based
- **Contrarian**: Counter-crowd, mean-reversion

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Simulations
- `POST /api/v1/simulations` - Create simulation
- `GET /api/v1/simulations` - List simulations
- `GET /api/v1/simulations/{id}` - Get simulation
- `GET /api/v1/simulations/{id}/results` - Get results
- `DELETE /api/v1/simulations/{id}` - Delete simulation

### Agents
- `GET /api/v1/simulations/{id}/agents` - List agents
- `GET /api/v1/simulations/{id}/agents/{agent_id}` - Get agent
- `POST /api/v1/simulations/{id}/agents/{agent_id}/chat` - Chat with agent

## Deployment

See [deploy.md](deploy.md) for production deployment instructions.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@postgres:5432/crystalfish` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | Change in production |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by MiroFish and swarm intelligence research
- Built with FastAPI, React, and modern web technologies
- Uses free AI models via OpenRouter