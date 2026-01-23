# Telegram Bot Web UI - Frontend

Modern React + TypeScript frontend for the Telegram Bot management interface.

## 🚀 Quick Start

### Install Dependencies

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Runs at http://localhost:5173 with hot module replacement.

### Production Build

```bash
npm run build
```

Outputs optimized static files to `dist/` directory.

## 📦 Tech Stack

- **React 18** - UI library with concurrent features
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool with HMR
- **React Router v6** - Client-side routing
- **TailwindCSS** - Utility-first CSS framework
- **FontAwesome** - Icon library
- **Axios** - HTTP client with interceptors

## 🎨 Features

- ✅ JWT-based authentication
- ✅ Protected routes
- ✅ Responsive sidebar navigation
- ✅ Real-time dashboard updates
- ✅ Dark theme optimized
- ✅ Mobile-friendly layout
- ✅ Type-safe with TypeScript

## 📁 Project Structure

```
src/
├── main.tsx              # Entry point
├── App.tsx               # Router configuration
├── index.css             # Global styles + Custom CSS
├── components/           # Reusable components
│   ├── Layout.tsx        # Main layout with sidebar
│   ├── ProtectedRoute.tsx
│   └── LoadingSpinner.tsx
├── contexts/             # React contexts
│   └── AuthContext.tsx   # Authentication state
├── lib/                  # Utilities
│   ├── api.ts            # Axios instance with JWT
│   └── utils.ts          # Helper functions
└── pages/                # Route components
    ├── Login.tsx
    ├── Dashboard.tsx
    ├── Settings.tsx
    ├── Media.tsx
    └── Groups.tsx
```

## 🔧 Configuration

The frontend automatically proxies API requests to the backend running on port 5000 (see `vite.config.ts`).

## 📝 Development Tips

- **Hot Reload:** Changes reflect instantly
- **TypeScript:** Errors show in terminal and browser
- **DevTools:** React DevTools extension recommended
- **Proxy:** API requests auto-proxy to backend

## 🏗️ Building for Production

1. Build the frontend:

   ```bash
   npm run build
   ```

2. Files are in `dist/` - ready to deploy!

3. Options:
   - Serve with Nginx/Caddy
   - Serve from FastAPI (mount static files)
   - Deploy to Vercel/Netlify/Cloudflare Pages

## 🎯 API Integration

The app connects to the FastAPI backend running on port 5000.

API client is configured in `src/lib/api.ts` with:

- Automatic JWT token injection
- 401 error handling (auto-logout)
- Request/response interceptors

## 📱 Mobile Support

Fully responsive design with:

- Mobile-friendly navigation
- Touch-optimized controls
- Adaptive layouts
- Optimized performance
