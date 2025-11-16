# Frontend Setup Guide

## Overview

A modern React-based frontend for the Mutual Fund FAQ chatbot, designed with **Groww's UI theme** and industry-standard chatbot design patterns.

## Features

✅ **Groww-Inspired Design**
- Green color scheme matching Groww's brand (#22c55e)
- Clean, professional interface
- Card-based layouts with subtle shadows
- Modern typography (Inter font)

✅ **Chatbot Interface**
- Industry-standard chat UI
- Message bubbles (user/assistant)
- Typing indicators
- Smooth animations
- Suggested questions

✅ **Fact-Only Branding**
- Prominent disclaimer banner
- "Fact Only" badges
- Clear messaging about no investment advice

✅ **Responsive Design**
- Works on desktop, tablet, and mobile
- Adaptive layouts
- Touch-friendly interactions

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

### 4. Make Sure Backend is Running

The frontend requires the backend API to be running on `http://localhost:8000`.

Start the backend:
```bash
# In project root
python run_server.py
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chatbot.jsx          # Main chat interface
│   │   ├── Header.jsx            # App header with branding
│   │   ├── FactOnlyBanner.jsx   # Disclaimer banner
│   │   ├── MessageList.jsx      # Message display component
│   │   └── SuggestedQuestions.jsx # Quick question buttons
│   ├── services/
│   │   └── api.js                # API client
│   ├── App.jsx                   # Root component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles + Tailwind
├── index.html
├── package.json
├── tailwind.config.js            # Tailwind with Groww colors
├── vite.config.js                # Vite configuration
└── README.md
```

## Design System

### Colors

- **Primary Green**: `#22c55e` (groww-green-500)
- **Dark Gray**: `#1f2937` (groww-dark-800)
- **Background**: `#f9fafb` (gray-50)
- **White**: `#ffffff`

### Typography

- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Components

- **Chat Messages**: Rounded bubbles with slide-in animations
- **Buttons**: Green primary buttons with hover effects
- **Cards**: White cards with subtle shadows
- **Input**: Rounded inputs with focus rings

## Key Components

### Chatbot Component
- Main chat interface
- Message handling
- Loading states
- Error handling
- Suggested questions

### Header Component
- App branding
- "Fact Only" badge
- Sticky header

### FactOnlyBanner Component
- Prominent disclaimer
- Blue informational banner
- Always visible

### MessageList Component
- Message rendering
- Source URL links
- Scheme name display
- User/assistant styling

## API Integration

The frontend connects to the backend at `/api/chat`:

```javascript
POST /api/chat
{
  "query": "What is the expense ratio?"
}

Response:
{
  "answer": "The expense ratio is...",
  "source_url": "https://groww.in/...",
  "scheme_name": "ICICI Prudential...",
  "fact_type": "expense_ratio"
}
```

## Build for Production

```bash
npm run build
```

Output will be in `frontend/dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Frontend won't start
- Check Node.js version (18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### API connection errors
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `.env` file
- Check browser console for CORS errors

### Styling issues
- Ensure Tailwind CSS is properly configured
- Check `tailwind.config.js` for correct paths
- Rebuild: `npm run build`

## Customization

### Change Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  'groww-green': {
    500: '#your-color',
    // ...
  }
}
```

### Modify Layout

Edit components in `src/components/` directory.

### Add Features

- New components in `src/components/`
- API calls in `src/services/api.js`
- Styles in `src/index.css`

## Next Steps

1. ✅ Frontend created
2. ✅ Design system implemented
3. ✅ API integration ready
4. ⏳ Test with backend
5. ⏳ Deploy (optional)

## Notes

- The frontend uses Vite for fast development
- Tailwind CSS for styling
- React 18 for UI
- Axios for API calls
- Lucide React for icons

---

**Ready to use!** Start the backend and frontend, then visit http://localhost:3000


