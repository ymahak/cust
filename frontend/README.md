# Frontend - AI Customer Support

## Quick Start

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   The app will be available at `http://localhost:5173`

## Prerequisites

- Make sure the backend is running on `http://localhost:8000`
- Start the backend first:
  ```bash
  cd ../backend
  python -m uvicorn app.main:app --reload --port 8000
  ```

## Features

- 🎨 Modern, attractive UI with gradients and animations
- 💬 Real-time chat interface
- 🔐 Optional authentication
- 📱 Responsive design for mobile devices
- ⚡ Fast and smooth user experience

## Troubleshooting

If you see a blank page:
1. Check the browser console for errors (F12)
2. Make sure the dev server is running (`npm run dev`)
3. Verify the backend is running on port 8000
4. Check that all dependencies are installed (`npm install`)
