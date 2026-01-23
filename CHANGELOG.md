# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-23

### Added

#### Web UI

- **Complete Modern Web Interface**: Full-featured SPA built with React + TypeScript + Vite
- **Discord-Bot Style Design**: Dark grayscale theme matching Discord-Bot UI aesthetics
- **Dashboard Page**: Real-time bot statistics with uptime, latency, member counts via Telegram API
- **Media Library Page**: Browse Sonarr series and Radarr movies with proper poster display
- **Groups Management Page**: Detailed group statistics with member/admin counts
- **Settings Page**: Complete configuration interface for bot, Sonarr, Radarr, TMDb, and Night Mode
- **About Page**: Version information, bot stats, system resources, and GitHub integration
- **JWT Authentication**: Secure login system with token-based authentication
- **Responsive Layout**: Modern sidebar navigation with mobile support

#### Caching System

- **Client-Side Cache**: React Context-based caching with configurable TTL
- **Smart Data Loading**: Instant page loads on tab switching with cached data
- **Memory-Efficient**: useRef implementation prevents unnecessary re-renders
- **Configurable TTL**: Different cache durations for different data types (2-10 minutes)

#### API Enhancements

- **FastAPI Backend**: Modern async API with comprehensive endpoints
- **Real-time Metrics**: Live bot status, latency measurements, resource monitoring
- **Telegram Integration**: Direct API calls for group statistics and member counts
- **Version Checking**: GitHub releases API integration for update notifications
- **Static File Serving**: Optimized frontend delivery with proper routing

#### Settings Features

- **Password Visibility Toggles**: Show/hide API keys and tokens with eye icons
- **TMDb Language Support**: 10 language options with database synchronization
- **Improved Night Mode UI**: Better time pickers with monospace fonts
- **Database Integration**: Settings changes update both config.json and SQLite

#### Groups Features

- **Detailed Statistics**: Real-time member counts and admin lists via Telegram API
- **Night Mode Integration**: Posts Telegram messages when Night Mode is activated
- **Permission Management**: Automatically restricts group permissions during Night Mode
- **Enhanced Display**: Modern card layout with stat items and icons

#### Media Features

- **Correct Poster Display**: Sonarr now shows posters instead of banners
- **Proper Aspect Ratios**: Different ratios for TV series (680/1000) and movies (2/3)
- **Tab-Based Navigation**: Separate Sonarr and Radarr views
- **Search Functionality**: Filter media by title

#### Visual Improvements

- **White Icons**: Stat card icons with white color on colored backgrounds
- **Favicon Support**: Proper favicon display in browser tabs
- **Loading Spinners**: Consistent loading states across all pages
- **Card Spacing**: Improved layout with proper margins between elements

### Changed

- **Architecture**: Migrated from basic web interface to modern SPA architecture
- **Styling**: Complete CSS overhaul with Discord-Bot grayscale theme
- **Navigation**: Sidebar-based navigation replacing basic page structure
- **Data Fetching**: Implemented caching layer for improved performance
- **Image Loading**: Sonarr poster type filtering for correct image display

### Fixed

- **Bot Initialization**: Changed hasattr checks from username to token
- **Version Parsing**: Correctly extracts version number (e.g., "1.2.0") from version.txt
- **TypeScript Errors**: Resolved all TypeScript compilation warnings
- **Python Syntax**: Fixed duplicate loops and error handling in groups.py
- **CSS Imports**: Added proper type declarations for CSS modules
- **Cache Performance**: Replaced useState with useRef to prevent re-renders
- **Favicon Routing**: Added dedicated endpoint for favicon serving

### Security

- **JWT Tokens**: Secure authentication with configurable secret keys
- **Password Protection**: API keys hidden by default with toggle option
- **Auth Middleware**: Protected routes requiring valid authentication

### Technical Details

- **Frontend Stack**: React 18, TypeScript, Vite 5.4.21, TailwindCSS, React Router v6
- **Backend Stack**: FastAPI, Uvicorn, PyJWT, python-telegram-bot 20.0
- **Database**: SQLite for group data and settings
- **API Integration**: Telegram Bot API, TMDb API, Sonarr API, Radarr API
- **Build System**: Vite for fast builds and hot module replacement
- **Type Safety**: Full TypeScript with strict mode enabled

## [1.1.0] - Previous Release

### Features

- Basic Telegram bot functionality
- Sonarr and Radarr integration
- Night Mode implementation
- Group management
- Media search and requests

---

[1.2.0]: https://github.com/cyb3rgh05t/telegram-bot/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/cyb3rgh05t/telegram-bot/releases/tag/v1.1.0
