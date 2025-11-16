# Mutual Fund FAQ Chatbot Frontend

A modern, responsive frontend for the ICICI Prudential Mutual Fund FAQ chatbot, designed with Groww's UI theme.

## Features

- 🎨 **Groww-inspired Design**: Clean, modern interface matching Groww's green theme
- 💬 **Chatbot Interface**: Industry-standard chat UI with message bubbles
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast & Smooth**: Built with React and Vite for optimal performance
- 🔗 **Source Links**: Direct links to Groww source pages
- ⚠️ **Fact-Only Disclaimer**: Clear indication that this is factual information only

## Design Highlights

- **Color Scheme**: Groww green (#22c55e) as primary color
- **Typography**: Inter font family for clean, professional look
- **Components**: Card-based layouts with subtle shadows
- **Animations**: Smooth slide-in animations for messages
- **Accessibility**: Proper contrast ratios and keyboard navigation

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend server running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chatbot.jsx          # Main chatbot component
│   │   ├── Header.jsx            # App header
│   │   ├── FactOnlyBanner.jsx   # Disclaimer banner
│   │   ├── MessageList.jsx      # Message display
│   │   └── SuggestedQuestions.jsx # Quick question buttons
│   ├── services/
│   │   └── api.js                # API integration
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```

## Features

### Chat Interface
- Real-time message display
- Typing indicators
- Source URL links
- Scheme name display
- Suggested questions

### Design Elements
- Groww green color scheme
- Smooth animations
- Responsive layout
- Professional typography
- Clear fact-only branding

## API Integration

The frontend connects to the backend API at `/api/chat` endpoint:

```javascript
POST /api/chat
{
  "query": "What is the expense ratio?"
}

Response:
{
  "answer": "...",
  "source_url": "...",
  "scheme_name": "...",
  "fact_type": "..."
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is for educational/demonstration purposes.


