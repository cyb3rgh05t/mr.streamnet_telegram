# Telegram Bot for Media Management

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/cyb3rgh05t/telegram-bot/releases)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

A modern Telegram bot with a beautiful web interface for managing your media library through Sonarr and Radarr. Built with Python, FastAPI, and React.

## ✨ Features

### 🤖 Telegram Bot

- **Media Search**: Search for TV shows and movies via TMDb API
- **Sonarr Integration**: Add TV series with quality profiles and root folders
- **Radarr Integration**: Add movies with quality profiles and root folders
- **Night Mode**: Automatic or manual restriction of non-admin messages
- **Group Management**: Multi-group support with individual settings
- **Welcome Messages**: Customizable welcome messages for new members
- **Language Support**: Multi-language support for TMDb searches

### 🎨 Modern Web UI

- **Discord-Bot Style Design**: Clean, dark grayscale interface
- **Real-time Dashboard**: Bot uptime, latency, member counts, system resources
- **Media Library Browser**: View and search Sonarr series and Radarr movies
- **Groups Management**: Detailed statistics and Night Mode control
- **Settings Panel**: Configure all bot settings through web interface
- **About Page**: Version information, system stats, and update checking
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### ⚡ Performance

- **Client-Side Caching**: Smart data caching for instant page loads
- **Async API**: FastAPI backend for high performance
- **JWT Authentication**: Secure token-based authentication
- **Optimized Builds**: Vite for fast development and production builds

## 📋 Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Web Interface](#web-interface)
- [Bot Commands](#bot-commands)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Requirements

### Backend

- Python 3.8 or higher
- Telegram Bot Token from [BotFather](https://core.telegram.org/bots#botfather)
- Sonarr v3 instance (optional)
- Radarr v3 instance (optional)
- TMDb API key from [The Movie Database](https://www.themoviedb.org/)

### Frontend

- Node.js 18+ and npm (for building the web interface)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cyb3rgh05t/telegram-bot.git
cd telegram-bot
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the Web Interface

```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. Configure the Bot

Copy the example configuration:

```bash
cp config/config.json.example config/config.json
```

Edit `config/config.json` with your settings (see [Configuration](#configuration) section).

### 5. Run the Bot

```bash
python bot.py
```

The bot will start and the web interface will be available at `http://localhost:5000`

## ⚙️ Configuration

### config.json Structure

```json
{
  "bot": {
    "TOKEN": "your-telegram-bot-token"
  },
  "commands": {
    "MOVIE_COMMAND": "movie",
    "SERIES_COMMAND": "series"
  },
  "welcome": {
    "ENABLED": true,
    "MESSAGE": "Welcome to the group!"
  },
  "nightmode": {
    "NIGHTMODE_START": "00:00",
    "NIGHTMODE_END": "08:00"
  },
  "tmdb": {
    "API_KEY": "your-tmdb-api-key",
    "DEFAULT_LANGUAGE": "en"
  },
  "sonarr": {
    "URL": "http://localhost:8989",
    "API_KEY": "your-sonarr-api-key",
    "QUALITY_PROFILE_NAME": "HD-1080p",
    "ROOT_FOLDER_PATH": "/tv"
  },
  "radarr": {
    "URL": "http://localhost:7878",
    "API_KEY": "your-radarr-api-key",
    "QUALITY_PROFILE_NAME": "HD-1080p",
    "ROOT_FOLDER_PATH": "/movies"
  },
  "web": {
    "ENABLED": true,
    "HOST": "0.0.0.0",
    "PORT": 5000,
    "AUTH_ENABLED": true,
    "USERNAME": "admin",
    "PASSWORD": "changeme",
    "SECRET_KEY": "your-secret-key-change-in-production",
    "VERBOSE_LOGGING": false
  }
}
```

### Environment Variables

You can also use environment variables (they override config.json):

```bash
export BOT_TOKEN="your-telegram-bot-token"
export TMDB_API_KEY="your-tmdb-api-key"
export WEB_USERNAME="admin"
export WEB_PASSWORD="changeme"
```

## 🚀 Usage

### Starting the Bot

```bash
python bot.py
```

The bot will:

1. Connect to Telegram
2. Start the FastAPI web server
3. Serve the React frontend
4. Begin listening for commands

### Accessing the Web Interface

1. Open your browser to `http://localhost:5000`
2. Login with your configured username and password
3. Navigate through the dashboard, media library, groups, and settings

### First-Time Setup

1. Add the bot to your Telegram group
2. Make the bot an administrator
3. Use `/set_group_id` command in the group
4. Configure settings through the web interface

## 🌐 Web Interface

### Dashboard

- Bot status (online/offline)
- Uptime and latency
- Total groups and members
- Sonarr series and Radarr movies count
- System resources (CPU, memory, disk)
- Service status

### Media Library

- Browse Sonarr TV series
- Browse Radarr movies
- Search functionality
- Proper poster display with correct aspect ratios

### Groups

- List all configured groups
- View member and admin counts
- Toggle Night Mode for each group
- See language settings

### Settings

- Bot configuration
- Sonarr settings with API key management
- Radarr settings with API key management
- TMDb configuration with language selection
- Night Mode time configuration
- Save all changes instantly

### About

- Current version information
- Check for updates from GitHub
- Bot statistics and uptime
- System information
- Support links

## 🤖 Bot Commands

### User Commands

- `/start` - Start the bot and get welcome message
- `/movie <title>` - Search for a movie
- `/series <title>` - Search for a TV series
- `/help` - Show available commands

### Admin Commands

- `/set_group_id` - Register the current group
- `/language <code>` - Set language (de, en, es, fr, it, pt, ru, ja, ko, zh)
- `/nightmode_on` - Enable Night Mode manually
- `/nightmode_off` - Disable Night Mode manually
- `/info` - Show bot and group information

## 💻 Development

### Project Structure

```
telegram-bot/
├── api/                    # FastAPI backend
│   ├── routers/           # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── dashboard.py  # Dashboard data
│   │   ├── media.py      # Sonarr/Radarr integration
│   │   ├── groups.py     # Group management
│   │   ├── settings.py   # Configuration
│   │   └── about.py      # Version and system info
│   ├── static/           # Built frontend (generated)
│   └── main.py           # FastAPI application
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts (auth, cache)
│   │   ├── lib/          # Utilities and API client
│   │   └── pages/        # Page components
│   ├── public/           # Static assets
│   └── package.json
├── config/
│   ├── config.json       # Main configuration
│   └── config.json.example
├── database/             # SQLite database
├── logs/                 # Application logs
├── bot.py               # Main bot file
├── requirements.txt     # Python dependencies
└── version.txt          # Version information
```

### Building the Frontend

```bash
cd frontend
npm install
npm run build
```

The built files will be in `frontend/dist/` and automatically copied to `api/static/`.

### Development Mode

Frontend (with hot reload):

```bash
cd frontend
npm run dev
```

Backend:

```bash
python bot.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**cyb3rgh05t**

- GitHub: [@cyb3rgh05t](https://github.com/cyb3rgh05t)

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [React](https://reactjs.org/) - Frontend framework
- [Vite](https://vitejs.dev/) - Build tool
- [Sonarr](https://sonarr.tv/) - TV series management
- [Radarr](https://radarr.video/) - Movie management
- [TMDb](https://www.themoviedb.org/) - Movie and TV database

## 📊 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

Made with ❤️ by cyb3rgh05t
