# NetworkMemory Backend

Node.js + Express + PostgreSQL backend for NetworkMemory AI - Smart networking contact management with AI-powered audio processing.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with your values

# Setup database
npm run db:push

# Start development server
npm run dev
```

Server runs on: `http://localhost:3000`

---

## 📚 Documentation

### For Backend Developers (You)
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Complete backend setup guide
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Quick integration overview

### For Frontend Developers (Your Friend)
- **[FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)** - Complete API reference with React Native examples
- **[CLERK_INTEGRATION_GUIDE.md](CLERK_INTEGRATION_GUIDE.md)** - Detailed Clerk authentication guide

---

## 🎯 What This Backend Does

### Core Features
✅ **User Profile Management** - Complete user profiles with networking preferences
✅ **Contact Management** - CRUD operations for networking contacts
✅ **Audio Processing** - Upload & extract contact info from conversations
✅ **AI Chat (TalkBot)** - Find collaborators from your network using AI
✅ **Semantic Search** - Vector-based contact search using embeddings
✅ **Real-time Updates** - WebSocket support via Socket.io

### Tech Stack
- **Runtime**: Node.js with TypeScript
- **Framework**: Express.js
- **Database**: PostgreSQL with Drizzle ORM
- **Auth**: JWT (Clerk/Auth0 compatible)
- **Vector Search**: pgvector for semantic search
- **Real-time**: Socket.io
- **AI Integration**: Python AI service for audio processing

---

## 🔑 Authentication

### 🏆 Auth0 Complete Implementation (Recommended for Hackathon)

**Full Auth0 ecosystem with user authentication + M2M + freemium + RBAC!**

**Quick Start Guides:**
- 📘 **[AUTH0_IMPLEMENTATION_SUMMARY.md](AUTH0_IMPLEMENTATION_SUMMARY.md)** - Start here! Overview & next steps
- 📗 **[AUTH0_COMPLETE_GUIDE.md](AUTH0_COMPLETE_GUIDE.md)** - Complete setup (Dashboard + Backend + Frontend + M2M)
- 📙 **[FRONTEND_AUTH0_QUICKSTART.md](FRONTEND_AUTH0_QUICKSTART.md)** - For frontend developers
- 📕 **[AUTH0_M2M_GUIDE.md](AUTH0_M2M_GUIDE.md)** - Machine-to-Machine authentication

**Features Implemented:**
- ✅ User authentication (Auth0 Universal Login)
- ✅ M2M authentication (Node.js ↔ Python AI)
- ✅ Freemium model (Auth0 Actions)
- ✅ RBAC (Role-based permissions)
- ✅ Social login (Google, LinkedIn, GitHub)
- ✅ Enterprise-ready security

### Alternative: Clerk Integration

This backend also supports **Clerk** JWT tokens.

See [CLERK_INTEGRATION_GUIDE.md](CLERK_INTEGRATION_GUIDE.md) for Clerk setup.

---

## 🛣️ API Endpoints

All endpoints require: `Authorization: Bearer <jwt-token>`

### User Endpoints
- `POST /api/users` - Create new user
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile

### Contact Endpoints
- `GET /api/contacts` - List all contacts
- `GET /api/contacts/:id` - Get contact details
- `PUT /api/contacts/:id` - Update contact
- `DELETE /api/contacts/:id` - Delete contact
- `GET /api/contacts/search?query=...` - Search contacts

### Audio Processing Endpoints
- `POST /api/upload/process` - Upload & process audio
- `POST /api/upload/audio` - Upload audio only
- `POST /api/audio/process` - Process from URL

### Chat Endpoints
- `POST /api/chat/message` - Send message to AI
- `GET /api/chat/session/:id` - Get chat history

See [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md) for detailed API documentation with examples.

---

## ⚙️ Environment Variables

### Quick Start (Development Mode)

✅ **Backend works immediately** - Auth0 fields can be left blank!

```bash
npm run dev
# Uses mock authentication for development
```

### Auth0 Setup (Production)

See [AUTH0_COMPLETE_GUIDE.md](AUTH0_COMPLETE_GUIDE.md) for full setup or:

```bash
# 1. Copy example
cp .env.example .env

# 2. Fill in Auth0 credentials from Auth0 Dashboard
```

Required fields:
```env
# User Authentication
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_ISSUER_BASE_URL=https://your-domain.auth0.com
AUTH0_API_AUDIENCE=https://networkmemory-api

# M2M (Python AI Security)
AUTH0_M2M_CLIENT_ID=your-client-id
AUTH0_M2M_CLIENT_SECRET=your-secret
AUTH0_M2M_AUDIENCE=https://networkmemory-api
```

---

## 📊 Database Schema

### Tables
- **users** - User profiles and preferences
- **contacts** - Contact information from networking
- **conversations** - Conversation history and transcripts
- **chat_messages** - TalkBot chat history

### Migrations
```bash
# Generate migration
npm run db:generate

# Apply to database
npm run db:push

# Open database studio
npm run db:studio
```

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:3000/health
```

### With Authentication
```bash
# Get token from Clerk Dashboard → JWT Templates
export TOKEN="eyJhbGc..."

# Test user endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/users/me

# Test contacts
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/contacts
```

---

## 🏗️ Project Structure

```
networkmemory-backend/
├── src/
│   ├── index.ts              # Main server entry point
│   ├── db/
│   │   ├── index.ts          # Database connection
│   │   └── schema.ts         # Database schema (Drizzle)
│   ├── routes/
│   │   ├── users.ts          # User profile routes
│   │   ├── contacts.ts       # Contact CRUD routes
│   │   ├── audio.ts          # Audio processing routes
│   │   ├── upload.ts         # File upload routes
│   │   └── chat.ts           # TalkBot chat routes
│   ├── services/
│   │   ├── audioProcessor.ts # Audio processing service
│   │   ├── semanticSearch.ts # Vector search service
│   │   ├── talkbot.ts        # AI chat service
│   │   └── socket.ts         # WebSocket service
│   └── middleware/
│       ├── auth.ts           # Auth0/JWT middleware
│       └── clerk.ts          # Clerk-specific middleware
├── BACKEND_SETUP.md          # Backend setup guide
├── FRONTEND_INTEGRATION_GUIDE.md  # API reference for frontend
├── CLERK_INTEGRATION_GUIDE.md     # Clerk integration details
└── INTEGRATION_SUMMARY.md    # Quick integration overview
```

---

## 🔄 Integration Flow

### First-Time User
1. User signs up with Clerk (frontend)
2. Frontend calls `POST /api/users` (create in backend)
3. User completes profile
4. Frontend calls `PUT /api/users/me` (save profile)
5. User starts networking!

### Audio Processing
1. User records conversation (frontend)
2. Frontend uploads via `POST /api/upload/process`
3. Backend sends to Python AI service
4. Contact info extracted and saved
5. Frontend receives contact data

### AI Chat
1. User types message (frontend)
2. Frontend calls `POST /api/chat/message`
3. Backend uses AI to search contacts
4. AI suggests collaborators
5. Frontend displays results

---

## 🚨 Troubleshooting

### Database connection failed
- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Verify database exists

### 401 Unauthorized
- Check JWT token is valid and not expired
- Verify Clerk issuer URL in `.env`
- Check CORS settings

### Python AI service not available
- Start Python service: `cd ../networkmemory-ai-service && python main.py`
- Check `PYTHON_AI_URL` in `.env`
- Audio processing requires this service

---

## 📦 Scripts

```bash
npm run dev          # Start development server with hot reload
npm run build        # Build for production
npm start            # Start production server
npm run db:generate  # Generate database migration
npm run db:push      # Apply migration to database
npm run db:studio    # Open Drizzle Studio (database GUI)
```

---

## 🚀 Deployment

### Prerequisites
- PostgreSQL database (Neon, Supabase, etc.)
- Node.js hosting (Vercel, Railway, etc.)
- Python AI service running

### Environment Setup
Update `.env` for production:
```env
NODE_ENV=production
ALLOWED_ORIGINS=https://your-frontend.com
DATABASE_URL=postgresql://...  # Production DB
AUTH0_ISSUER_BASE_URL=https://your-app.clerk.accounts.dev
```

### Deploy
```bash
npm run build
npm start
```

---

## 🤝 Working with Frontend

**Give your frontend developer:**
1. Backend URL (e.g., `http://localhost:3000`)
2. Clerk Publishable Key (`pk_test_...`)
3. The file: [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)

They'll have everything they need!

---

## 📝 License

MIT

---

## 👥 Team

Built for NetworkMemory AI - Smart networking with AI-powered contact management

---

## 📞 Need Help?

1. Check the documentation files in this repo
2. Test endpoints with cURL or Postman
3. Check server logs for detailed errors
4. Verify environment variables are correct

**Happy coding! 🚀**
