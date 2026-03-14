# CrystalFish

<div align="center">
  <img src="./logo.svg" alt="CrystalFish Logo" width="300"/>
  
  **AI Swarm Intelligence for Stock/Crypto Prediction**
  
  <p>A multi-agent swarm intelligence engine combining hundreds of AI agents with advanced mathematical models to forecast market prices.</p>
  
  <img src="https://img.shields.io/badge/CrystalFish-v1.0.0-blue?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker"/>
</div>

---

## 📸 Dashboard Preview

<div align="center">
  <img src="./screenshot.svg" alt="CrystalFish Dashboard Preview" width="100%"/>
</div>

---

## ✨ Features

### Core Capabilities

- **🤖 Multi-Agent AI Swarm**: Hundreds of intelligent agents with unique personalities analyze markets simultaneously
- **📊 Advanced Math Models**: ARIMA, GARCH, Prophet, and ensemble forecasting for accurate predictions
- **📈 Technical Analysis**: RSI, MACD, Bollinger Bands, and custom indicators
- **⚡ Real-time Updates**: WebSocket-powered live simulation progress tracking
- **🎨 Interactive Dashboard**: Beautiful charts and visualizations with modern UI
- **💬 Agent Chat**: Talk to individual AI agents to understand their trading reasoning
- **🔍 API Test Dashboard**: Built-in API monitoring with intelligent health analysis

### New: API Test Dashboard

CrystalFish now includes a comprehensive API testing and monitoring system:

- **Real-time Health Monitoring**: Continuous API endpoint testing with configurable intervals
- **Performance Metrics**: Track response times, success rates, and error counts
- **Intelligent Agent Analysis**: "API Guardian" agent provides AI-powered insights and recommendations
- **Automated Alerts**: Threshold-based alerting for critical performance issues
- **Chat Interface**: Natural language queries about API performance

---

## 🏗️ Architecture

```
crystalfish/
├── backend/
│   ├── app/
│   │   ├── api/              # REST API routes
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── simulations.py # Simulation management
│   │   │   ├── agents.py     # Agent interactions
│   │   │   └── api_test.py   # API Test Dashboard ⭐ NEW
│   │   ├── core/             # Core configuration
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── agent.py              # AI Agent class
│   │   │   ├── simulation.py         # Simulation engine
│   │   │   ├── math_models.py        # ARIMA, GARCH, Prophet
│   │   │   ├── openrouter.py         # LLM integration
│   │   │   ├── api_test.py           # API Testing Service ⭐ NEW
│   │   │   └── api_dashboard_agent.py # API Guardian Agent ⭐ NEW
│   │   └── worker/           # Celery background tasks
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Application pages
│   │   ├── hooks/            # Custom React hooks
│   │   └── utils/            # Helper utilities
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) OpenRouter API key for advanced AI models

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/crystalfish.git
cd crystalfish
```

2. **Create environment file:**
```bash
cp backend/.env.example backend/.env
```

3. **Configure environment (optional):**
```bash
# Add your OpenRouter API key for better AI models
OPENROUTER_API_KEY=your-key-here
```

4. **Start all services:**
```bash
docker-compose up -d
```

5. **Access the application:**
- 🌐 **Frontend**: http://localhost:5173
- 🔌 **Backend API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs
- 🧪 **API Test Dashboard (No Login Required)**: http://localhost:8000/api-test/dashboard/ui
- 📊 **API Test Dashboard (JSON)**: http://localhost:8000/api-test/dashboard

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **PostgreSQL** - Primary relational database
- **Redis** - Caching and message broker
- **Celery** - Distributed task queue for async processing
- **OpenRouter** - Access to free AI models (Mistral, Llama, etc.)
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation and settings management

### Frontend
- **React 18** - UI library with concurrent features
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-generation build tool
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful UI components
- **Framer Motion** - Animation library
- **Recharts** - Composable charting library

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/auth/me` | Get current user |
| PATCH | `/api/v1/auth/me` | Update user profile |

### Simulations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/simulations` | Create simulation |
| GET | `/api/v1/simulations` | List simulations |
| GET | `/api/v1/simulations/{id}` | Get simulation details |
| GET | `/api/v1/simulations/{id}/results` | Get prediction results |
| DELETE | `/api/v1/simulations/{id}` | Delete simulation |

### Agents
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/simulations/{id}/agents` | List all agents |
| GET | `/api/v1/simulations/{id}/agents/{agent_id}` | Get agent details |
| POST | `/api/v1/simulations/{id}/agents/{agent_id}/chat` | Chat with agent |

### API Test Dashboard ⭐ NEW
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api-test/health` | API health status |
| GET | `/api-test/dashboard` | Complete dashboard data |
| POST | `/api-test/test-all` | Run full test suite |
| POST | `/api-test/test` | Test specific endpoint |
| GET | `/api-test/agent/summary` | Get API Guardian summary |
| POST | `/api-test/agent/chat` | Chat with API Guardian |
| GET | `/api-test/metrics` | Performance metrics |
| POST | `/api-test/monitoring/start` | Start monitoring |

---

## 🐠 Agent Personalities

CrystalFish agents have distinct trading personalities:

| Personality | Style | Characteristics |
|-------------|-------|-----------------|
| 🐂 **Bullish** | Optimistic | Growth-focused, buys dips, believes in long-term gains |
| 🐻 **Bearish** | Cautious | Risk-averse, takes profits early, protects capital |
| ⚖️ **Neutral** | Balanced | Data-driven, waits for clear signals |
| 📈 **Trend Follower** | Technical | Follows momentum, uses moving averages |
| 🔄 **Contrarian** | Counter-crowd | Goes against sentiment, mean-reversion |

---

## 💻 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://postgres:postgres@postgres:5432/crystalfish` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | _Change in production_ |
| `SECRET_KEY` | Application secret key | _Change in production_ |
| `OPENROUTER_API_KEY` | OpenRouter API key | _Optional_ |
| `FRONTEND_URL` | Frontend CORS origin | `http://localhost:5173` |
| `DEBUG` | Debug mode | `false` |

---

## 📊 How It Works

1. **Upload Data**: Import historical prices via CSV or use live feeds (Yahoo Finance, CoinGecko)
2. **Configure Simulation**: Set asset symbol, time horizon, agent count, and confidence level
3. **Run Swarm**: Launch hundreds of AI agents that analyze and predict price movements
4. **Monitor Progress**: Watch real-time simulation progress via WebSocket
5. **Get Results**: View predictions, sentiment analysis, charts, and key factors
6. **Chat with Agents**: Understand individual agent reasoning through natural language

---

## 🌐 Deployment

For production deployment instructions, see [deploy.md](crystalfish/deploy.md)

### Production Checklist

- [ ] Change all default passwords and secret keys
- [ ] Configure SSL/HTTPS with Let's Encrypt
- [ ] Set up firewall rules (UFW)
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Disable debug mode

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas We'd Love Help With:
- Additional AI agent personalities
- More technical indicators
- Frontend UI improvements
- API test coverage
- Documentation improvements

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Inspired by [MiroFish](https://github.com/666ghj/MiroFish) and swarm intelligence research
- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), and modern web technologies
- Uses free AI models via [OpenRouter](https://openrouter.ai/)
- Agent avatars and UI components from [shadcn/ui](https://ui.shadcn.com/)

---

## 📬 Contact

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and community support

<div align="center">
  <sub>Built with ❤️ using AI Swarm Intelligence</sub>
  <br/>
  <sub>CrystalFish v0.0.1 - Predicting the future, one agent at a time</sub>
</div>
