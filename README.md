# Idaeho

## What is this?

A mobile application that allows you to:

- play audio files

### Possible future feature

- turns your epub/pdf ebooks into audio

### Key Features

- **Cloud Sync** - Access your library from any device
- **File Upload** - Add audio files from your phone or computer
- **User Authentication** - Secure account system with JWT tokens
- **Offline Support** - Download for offline playback
- **Playback Controls** - Speed adjustment, repeat, shuffle modes
- **Library Management** - Organize by author, subject, and date

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Flutter Mobile App (iOS/Android)                           │
│  ├── UI Layer (Screens & Widgets)                           │
│  ├── State Management (Provider/Riverpod)                   │
│  ├── Local Storage (SQLite + File System)                   │
│  └── API Service Layer                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  FastAPI (Python)                                           │
│  ├── Authentication (JWT)                                   │
│  ├── Audio Management Endpoints                             │
│  └── File Upload/Download                                   │
└────────────┬───────────────────────┬────────────────────────┘
             │                       │
             ↓                       ↓
┌────────────────────────┐  ┌──────────────────────────┐
│   DATABASE LAYER       │  │   STORAGE LAYER          │
├────────────────────────┤  ├──────────────────────────┤
│  PostgreSQL            │  │  Cloud Storage           │
│  ├── users             │  │  (AWS S3)                │
│  ├── audio_files       │  │  ├── MP3 Files           │
│  ├── playlists         │  │  └── Cover Images        │
│  └── user_sessions     │  └──────────────────────────┘
└────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend (Mobile App)

- **Framework:** Flutter 3.x (Dart)
- **Local Database:** SQLite (sqflite)

### Backend (API Server)

- **Framework:** FastAPI (Python)

### Database

- **Primary Database:** PostgreSQL 15+

### Cloud Storage

- **File Storage:** AWS S3
- **CDN:** CloudFront (optional future feature for faster delivery)
