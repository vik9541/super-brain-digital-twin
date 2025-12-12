# Super Brain Digital Twin - Web UI Dashboard

Interactive Next.js 14 dashboard for visualizing and analyzing your contact network graph powered by GraphQL API.

## 🎯 Features

- **Dashboard Overview**: Real-time network statistics and insights
- **Contacts Management**: Search, filter, and browse all contacts with pagination
- **Influencers Ranking**: Top 50 influencers ranked by network analysis scores
- **Community Detection**: Visualize detected communities and clusters
- **Network Visualization**: Interactive Cytoscape.js graph with nodes and edges
- **Shortest Path Finder**: Find connection paths between any two contacts
- **Contact Details**: Comprehensive view of individual contact information

## 🚀 Tech Stack

- **Framework**: Next.js 14.2.0 (App Router)
- **Language**: TypeScript 5.3.3
- **Styling**: Tailwind CSS 3.4.1
- **GraphQL Client**: graphql-request 6.1.0
- **Graph Visualization**: Cytoscape.js 3.28.1
- **Icons**: Lucide React 0.344.0

## 📦 Installation

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your GraphQL API endpoint
# NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:8000/graphql
```

## 🔧 Configuration

Edit `web/.env.local`:

```env
# GraphQL API endpoint (required)
NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:8000/graphql

# Optional: Enable development logging
NEXT_PUBLIC_DEBUG=true
```

## 🏃 Development

```bash
# Start development server
npm run dev

# Open browser at http://localhost:3000
```

The dev server includes:
- Hot Module Replacement (HMR)
- Fast Refresh for instant updates
- TypeScript error reporting
- GraphQL query logging (if DEBUG=true)

## 🏗️ Build & Production

```bash
# Build for production
npm run build

# Start production server
npm start

# Build output in .next/ directory
```

## 📁 Project Structure

```
web/
├── app/                      # Next.js App Router
│   ├── layout.tsx            # Root layout with metadata
│   ├── page.tsx              # Landing page
│   ├── globals.css           # Global styles
│   └── dashboard/            # Dashboard routes
│       ├── layout.tsx        # Dashboard layout with nav
│       ├── page.tsx          # Main dashboard (stats)
│       ├── contacts/         # Contacts list & detail
│       │   ├── page.tsx      # Contacts table
│       │   └── [id]/page.tsx # Contact detail view
│       ├── influencers/      # Top influencers ranking
│       │   └── page.tsx
│       ├── communities/      # Community clusters
│       │   └── page.tsx
│       └── graph/            # Network visualization
│           └── page.tsx
├── components/               # React components
│   ├── Navigation.tsx        # Main navigation bar
│   ├── ContactTable.tsx      # Searchable contacts table
│   ├── NetworkGraph.tsx      # Cytoscape graph component
│   └── PathFinder.tsx        # Shortest path finder
├── lib/                      # Utilities
│   ├── graphql-client.ts     # GraphQL fetch helpers
│   └── queries.ts            # GraphQL queries
├── types/                    # TypeScript types
│   └── index.ts              # Contact, Community, etc.
├── public/                   # Static assets
├── package.json              # Dependencies
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── next.config.mjs           # Next.js configuration
```

## 🔌 GraphQL API Integration

The dashboard connects to the FastAPI GraphQL backend. Ensure the API is running:

```bash
# In root directory
uvicorn api.main:app --reload --port 8000

# GraphQL endpoint: http://localhost:8000/graphql
# GraphQL Playground: http://localhost:8000/graphql
```

### Available Queries

- `contacts(limit, offset)` - Fetch contacts with pagination
- `influencers(limit)` - Top influencers by score
- `communities` - Detected communities with members
- `networkGraph(limit)` - Graph nodes and edges
- `shortestPath(id1, id2)` - Path between two contacts
- `networkStats` - Overall network statistics

## 🎨 Customization

### Tailwind Theme

Edit `web/tailwind.config.ts` to customize colors:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#f0f9ff',
        // ... your brand colors
      }
    }
  }
}
```

### Graph Visualization

Modify `web/components/NetworkGraph.tsx` for custom layouts:

```typescript
layout: {
  name: 'cose',      // Options: cose, circle, grid, breadthfirst
  idealEdgeLength: 100,
  nodeRepulsion: 400000,
  // ... other physics parameters
}
```

## 📊 Component Usage

### ContactTable

```tsx
import ContactTable from '@/components/ContactTable';

<ContactTable
  contacts={contactsArray}
  initialPageSize={25}
/>
```

### NetworkGraph

```tsx
import NetworkGraph from '@/components/NetworkGraph';

<NetworkGraph
  data={{
    nodes: [...],
    edges: [...]
  }}
/>
```

### PathFinder

```tsx
import PathFinder from '@/components/PathFinder';

<PathFinder />
// Handles GraphQL queries internally
```

## 🚢 Deployment

### Vercel (Recommended)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy from web/ directory:
```bash
cd web
vercel
```

3. Set environment variables in Vercel Dashboard:
   - `NEXT_PUBLIC_GRAPHQL_ENDPOINT` = your production GraphQL URL

4. Automatic deployments on git push (connect GitHub repo)

### Docker

```dockerfile
# Use Node 18 Alpine
FROM node:18-alpine

WORKDIR /app
COPY web/package*.json ./
RUN npm ci --only=production

COPY web/ ./
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t super-brain-web .
docker run -p 3000:3000 -e NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://api:8000/graphql super-brain-web
```

## 🧪 Testing

```bash
# Run all tests (when implemented)
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_GRAPHQL_ENDPOINT` | Yes | - | GraphQL API URL |
| `NEXT_PUBLIC_DEBUG` | No | false | Enable debug logging |

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open Pull Request

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Cytoscape.js](https://js.cytoscape.org/)
- [GraphQL](https://graphql.org/learn/)

## 🐛 Troubleshooting

### GraphQL Connection Error

Check that:
1. Backend API is running (`uvicorn api.main:app --reload`)
2. CORS is configured correctly in FastAPI
3. `NEXT_PUBLIC_GRAPHQL_ENDPOINT` matches your API URL

### Graph Not Rendering

Ensure:
1. Cytoscape.js is loaded client-side only (`'use client'` directive)
2. Browser console shows no JavaScript errors
3. Network tab shows successful GraphQL responses

### Build Errors

```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Related Repositories

- **Backend API**: `../api/` - FastAPI + GraphQL server
- **Mobile SDK**: `../mobile/` - iOS/Android integrations
- **Infrastructure**: `../docker-compose.yml` - Full stack deployment

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using Next.js 14 and TypeScript**
