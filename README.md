# 🧘 Real-Time Sitting Posture Detection System

A real-time posture monitoring application that uses AI to analyze your sitting position through your webcam. Built with Django Channels for WebSocket streaming and MediaPipe for pose detection.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2+-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Connecting Your Own Frontend](#connecting-your-own-frontend)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Real-time Pose Detection**: Uses Google's MediaPipe for accurate body landmark detection
- **Live Video Streaming**: WebSocket-based video feed with ~30 FPS
- **Posture Analysis**: Calculates hip angle to determine sitting posture quality
- **Visual Feedback**: Draws skeleton overlay and posture metrics on video
- **Bi-directional Communication**: Frontend can control stream (start/stop)
- **Framework Agnostic**: Works with any frontend (React, Vue, Angular, Vanilla JS)

## 🏗️ Architecture

```
┌─────────────┐         WebSocket          ┌──────────────┐
│   Frontend  │ ←────────────────────────→ │    Django    │
│  (React/Any)│     ws://localhost:8000     │   Channels   │
└─────────────┘                             └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │  MediaPipe   │
                                            │   + OpenCV   │
                                            └──────┬───────┘
                                                   │
                                            ┌──────▼───────┐
                                            │   Webcam     │
                                            └──────────────┘
```

**Tech Stack:**
- **Backend**: Django 5.2+ with Django Channels
- **WebSocket Server**: Daphne (ASGI)
- **Message Broker**: Redis
- **Computer Vision**: OpenCV + MediaPipe
- **Protocol**: WebSocket (ws://)

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Redis Server** (Message broker for Django Channels)
- **Webcam** (Built-in or USB)
- **Git** (For cloning repositories)

### Installing Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
```

**macOS:**
```bash
brew install redis
```

**Windows:**
Download from [Redis Official Website](https://redis.io/download) or use WSL (Windows Subsystem for Linux)

**Verify Redis Installation:**
```bash
redis-cli ping
# Should return: PONG
```

## 📥 Installation

### 1. Clone the Repositories

**Backend:**
```bash
git clone <your-backend-repo-url>
cd posture-detection-backend
```

**Frontend** (if using the provided React app):
```bash
git clone <your-frontend-repo-url>
cd posture-detection-frontend
```

### 2. Set Up Python Virtual Environment

```bash
# Navigate to backend directory
cd posture-detection-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install django channels channels-redis daphne opencv-python mediapipe numpy django-cors-headers
```

**Or using requirements.txt:**
```bash
pip install -r requirements.txt
```

### 4. Configure Django Settings

Ensure your `posture_project/settings.py` includes:

```python
INSTALLED_APPS = [
    # ... other apps
    'channels',
    'corsheaders',
    'posture_stream',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ... other middleware
]

# ASGI Application
ASGI_APPLICATION = 'posture_project.asgi.application'

# Redis Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# CORS Settings (adjust for production)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React default
    "http://localhost:5173",      # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# For development only (not secure for production):
# CORS_ALLOW_ALL_ORIGINS = True
```

### 5. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Running the Application

### Step 1: Start Redis Server

**In Terminal 1:**
```bash
redis-server
```

Leave this running. You should see:
```
[PID] Ready to accept connections
```

### Step 2: Start Django Backend with Daphne

**In Terminal 2:**
```bash
# Navigate to backend directory
cd posture-detection-backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start ASGI server
daphne -b 127.0.0.1 -p 8000 posture_project.asgi:application
```

You should see:
```
2025-11-12 04:44:00,000 INFO     Starting server at tcp:port=8000:interface=127.0.0.1
2025-11-12 04:44:00,000 INFO     Listening on TCP address 127.0.0.1:8000
```

> ⚠️ **Important**: Do NOT use `python manage.py runserver` - it doesn't support WebSockets!

### Step 3: Start Frontend (Optional)

**In Terminal 3** (if using the provided React frontend):
```bash
cd posture-detection-frontend
npm install
npm run dev  # or npm start
```

Open your browser to `http://localhost:3000` (or the port shown)

### Verify Everything is Running

You should have:
- ✅ Redis running on port 6379
- ✅ Django/Daphne running on port 8000
- ✅ Frontend running on port 3000/5173
- ✅ Webcam accessible

## 🔌 Connecting Your Own Frontend

The beauty of WebSockets is they work with **any frontend framework**! Here's how to connect:

### WebSocket Connection Details

**Endpoint:** `ws://127.0.0.1:8000/ws/posture/`

**Protocol:** WebSocket (ws://)

**Data Format:** JSON

### Message Structure

#### **Server → Client** (Receiving Data)

```json
{
  "frame": "base64_encoded_jpeg_string",
  "posture": "Good Posture" | "Bad Posture" | "Unknown",
  "angle": 95
}
```

#### **Client → Server** (Sending Commands)

```json
{
  "command": "start" | "stop"
}
```

### Implementation Examples

#### 1. **Vanilla JavaScript**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Posture Detection</title>
</head>
<body>
    <h1>Posture Monitor</h1>
    <img id="videoFeed" style="width: 640px; height: 480px;" />
    <div id="postureStatus"></div>
    <button onclick="stopStream()">Stop</button>
    <button onclick="startStream()">Start</button>

    <script>
        const ws = new WebSocket('ws://127.0.0.1:8000/ws/posture/');

        ws.onopen = () => {
            console.log('Connected to posture detection');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Update video frame
            document.getElementById('videoFeed').src = 
                'data:image/jpeg;base64,' + data.frame;
            
            // Update posture status
            document.getElementById('postureStatus').innerHTML = 
                `<h2>${data.posture}</h2><p>Angle: ${data.angle}°</p>`;
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('Disconnected');
        };

        function stopStream() {
            ws.send(JSON.stringify({ command: 'stop' }));
        }

        function startStream() {
            ws.send(JSON.stringify({ command: 'start' }));
        }
    </script>
</body>
</html>
```

#### 2. **React**

```jsx
import React, { useEffect, useState, useRef } from 'react';

function PostureDetector() {
    const [frame, setFrame] = useState('');
    const [posture, setPosture] = useState('Connecting...');
    const [angle, setAngle] = useState(0);
    const wsRef = useRef(null);

    useEffect(() => {
        // Connect to WebSocket
        wsRef.current = new WebSocket('ws://127.0.0.1:8000/ws/posture/');

        wsRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setFrame(`data:image/jpeg;base64,${data.frame}`);
            setPosture(data.posture);
            setAngle(data.angle);
        };

        // Cleanup on unmount
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    const stopStream = () => {
        wsRef.current.send(JSON.stringify({ command: 'stop' }));
    };

    const startStream = () => {
        wsRef.current.send(JSON.stringify({ command: 'start' }));
    };

    return (
        <div>
            <h1>Posture Detection</h1>
            <img src={frame} alt="Video Feed" style={{ width: '640px' }} />
            <div>
                <h2>{posture}</h2>
                <p>Hip Angle: {angle}°</p>
            </div>
            <button onClick={startStream}>Start</button>
            <button onClick={stopStream}>Stop</button>
        </div>
    );
}

export default PostureDetector;
```

#### 3. **Vue.js**

```vue
<template>
  <div>
    <h1>Posture Detection</h1>
    <img :src="frame" style="width: 640px;" />
    <div>
      <h2>{{ posture }}</h2>
      <p>Hip Angle: {{ angle }}°</p>
    </div>
    <button @click="startStream">Start</button>
    <button @click="stopStream">Stop</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      ws: null,
      frame: '',
      posture: 'Connecting...',
      angle: 0
    };
  },
  mounted() {
    this.ws = new WebSocket('ws://127.0.0.1:8000/ws/posture/');
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.frame = 'data:image/jpeg;base64,' + data.frame;
      this.posture = data.posture;
      this.angle = data.angle;
    };
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  },
  methods: {
    startStream() {
      this.ws.send(JSON.stringify({ command: 'start' }));
    },
    stopStream() {
      this.ws.send(JSON.stringify({ command: 'stop' }));
    }
  }
};
</script>
```

#### 4. **Angular**

```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-posture-detector',
  template: `
    <h1>Posture Detection</h1>
    <img [src]="frame" style="width: 640px;" />
    <div>
      <h2>{{ posture }}</h2>
      <p>Hip Angle: {{ angle }}°</p>
    </div>
    <button (click)="startStream()">Start</button>
    <button (click)="stopStream()">Stop</button>
  `
})
export class PostureDetectorComponent implements OnInit, OnDestroy {
  private ws: WebSocket;
  frame: string = '';
  posture: string = 'Connecting...';
  angle: number = 0;

  ngOnInit() {
    this.ws = new WebSocket('ws://127.0.0.1:8000/ws/posture/');
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.frame = 'data:image/jpeg;base64,' + data.frame;
      this.posture = data.posture;
      this.angle = data.angle;
    };
  }

  ngOnDestroy() {
    if (this.ws) {
      this.ws.close();
    }
  }

  startStream() {
    this.ws.send(JSON.stringify({ command: 'start' }));
  }

  stopStream() {
    this.ws.send(JSON.stringify({ command: 'stop' }));
  }
}
```

#### 5. **Python (for testing/debugging)**

```python
import asyncio
import websockets
import json
import base64

async def connect():
    uri = "ws://127.0.0.1:8000/ws/posture/"
    async with websockets.connect(uri) as websocket:
        print("Connected!")
        
        async for message in websocket:
            data = json.loads(message)
            print(f"Posture: {data['posture']}, Angle: {data['angle']}°")
            
            # Optionally save frame
            # frame_data = base64.b64decode(data['frame'])
            # with open('frame.jpg', 'wb') as f:
            #     f.write(frame_data)

asyncio.run(connect())
```

## 📁 Project Structure

```
posture-detection-backend/
├── manage.py
├── requirements.txt
├── posture_project/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── asgi.py              # ASGI configuration (WebSocket routing)
│   ├── urls.py
│   └── wsgi.py
└── posture_stream/
    ├── __init__.py
    ├── consumers.py         # WebSocket consumer (main logic)
    ├── routing.py           # WebSocket URL routing
    ├── models.py
    ├── views.py
    └── apps.py
```

### Key Files Explained

**`asgi.py`**: Routes incoming WebSocket connections to the appropriate consumer

**`consumers.py`**: Contains the `PostureConsumer` class that handles:
- WebSocket connections
- Video capture from webcam
- MediaPipe pose detection
- Angle calculation
- Frame encoding and streaming

**`routing.py`**: Maps WebSocket URLs to consumers (like `urls.py` for HTTP)

## 🐛 Troubleshooting

### Issue: "Address already in use" (Redis)

**Solution**: Redis is already running (this is good!)
```bash
redis-cli ping  # Should return PONG
```

### Issue: "Not Found: /ws/posture/"

**Possible causes:**
1. Using `python manage.py runserver` instead of `daphne`
2. Missing `channels` in `INSTALLED_APPS`
3. `ASGI_APPLICATION` not set in settings.py

**Solution**: Use the correct command:
```bash
daphne -b 127.0.0.1 -p 8000 posture_project.asgi:application
```

### Issue: "Cannot import name 'consumers'"

**Solution**: Make sure `posture_stream/consumers.py` exists with the `PostureConsumer` class

### Issue: Camera not opening

**Solution**:
```bash
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
# Should print: True
```

If False:
- Check camera permissions
- Try different camera index (1, 2, etc.)
- Ensure no other app is using the camera

### Issue: CORS errors in browser

**Solution**: Add your frontend URL to `CORS_ALLOWED_ORIGINS` in `settings.py`
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

### Issue: High CPU usage

**Solution**: Reduce frame rate or resolution in `consumers.py`:
```python
# Lower resolution
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Lower frame rate
await asyncio.sleep(0.066)  # ~15 FPS instead of 30
```

### Issue: Slow/laggy video

**Possible causes:**
1. Network latency
2. CPU overload
3. Large frame size

**Solutions:**
- Reduce JPEG quality in `consumers.py`:
  ```python
  encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
  _, buffer = cv2.imencode('.jpg', image, encode_param)
  ```
- Lower resolution (see above)
- Use WebSocket compression

## 🔐 Production Deployment

For production deployment, consider:

1. **Use WSS (secure WebSocket)**:
   ```
   wss://yourdomain.com/ws/posture/
   ```

2. **Configure Nginx** as reverse proxy:
   ```nginx
   location /ws/ {
       proxy_pass http://localhost:8000;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
       proxy_cache_bypass $http_upgrade;
   }
   ```

3. **Use environment variables** for sensitive settings

4. **Run with Supervisor** for auto-restart:
   ```ini
   [program:daphne]
   command=/path/to/venv/bin/daphne -u /tmp/daphne.sock posture_project.asgi:application
   directory=/path/to/project
   autostart=true
   autorestart=true
   ```

5. **Scale with multiple workers** (Redis handles distribution)

6. **Add authentication** to secure WebSocket connections

7. **Implement rate limiting** to prevent abuse

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://google.github.io/mediapipe/) - Google's ML solutions
- [Django Channels](https://channels.readthedocs.io/) - WebSocket support for Django
- [OpenCV](https://opencv.org/) - Computer vision library

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Open an issue on GitHub
3. Refer to the official documentation:
   - [Django Channels Docs](https://channels.readthedocs.io/)
   - [MediaPipe Docs](https://google.github.io/mediapipe/)

---

**Built with ❤️ using Django Channels, MediaPipe, and OpenCV**