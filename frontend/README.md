# AI Tax Reform - Frontend

Modern Next.js frontend for the AI Tax Reform application with RAG-powered tax Q&A and calculator.

## Features

- 💬 **Chat Interface**: Ask questions about Nigerian tax law with AI-powered answers
- 🧮 **Tax Calculator**: Calculate personal income tax with detailed breakdowns
- ⚡ **Real-time Results**: Fast responses with caching and optimization
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- ✅ **Answer Verification**: Optional fact-checking for critical queries

## Tech Stack

- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **UI Components**: Lucide React icons
- **Markdown**: react-markdown with GFM support

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Running backend API (see main README)

### Installation

```bash
cd frontend
npm install
```

### Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:7860
```

For production, set to your Render backend URL:
```env
NEXT_PUBLIC_API_URL=https://ai-tax-reform.onrender.com
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Deployment on Vercel

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/AI-TAX-REFORM/tree/main/frontend)

### Manual Deploy

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   cd frontend
   vercel
   ```

3. Set environment variable in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` = Your Render backend URL

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app directory
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── ChatInterface.tsx
│   │   └── TaxCalculator.tsx
│   └── lib/                 # Utility functions
│       └── utils.ts
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## API Integration

The frontend connects to the following backend endpoints:

- `POST /qa` - Question answering with sources
- `POST /aqa` - Answered QA with verification
- `POST /calculate` - Tax calculation
- `POST /retrieve` - Raw document retrieval

## Features Detail

### Chat Interface

- Conversational UI for tax questions
- Displays AI-generated answers with sources
- Shows model used (Groq/Gemini)
- Optional answer verification toggle
- Source document excerpts with relevance scores

### Tax Calculator

- Input: Gross income, allowances, reliefs
- Output: Taxable income, tax due, effective rate
- Detailed breakdown by tax bracket
- Nigerian tax brackets (7%, 11%, 15%, 19%, 21%, 24%)

## Optimization Features

- Vectorstore caching on backend
- Component-level code splitting
- Responsive design for mobile/desktop
- Error handling with user-friendly messages
- Loading states and skeleton screens

## Contributing

See main project README for contribution guidelines.

## License

MIT License - see LICENSE file for details.
