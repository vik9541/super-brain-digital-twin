import Link from 'next/link';
import { Home, Users, TrendingUp, Network, GitBranch } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            Super Brain Contacts
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Network Intelligence Dashboard - Discover, Analyze, Connect
          </p>
          <Link
            href="/dashboard"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Open Dashboard →
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <Link href="/dashboard" className="group">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow border-t-4 border-blue-500">
              <div className="flex items-center justify-between mb-4">
                <Home className="w-8 h-8 text-blue-600" />
                <span className="text-sm text-gray-500 group-hover:text-blue-600">Overview</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Dashboard</h3>
              <p className="text-gray-600 text-sm">
                Real-time statistics and network insights
              </p>
            </div>
          </Link>

          <Link href="/dashboard/contacts" className="group">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow border-t-4 border-green-500">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-green-600" />
                <span className="text-sm text-gray-500 group-hover:text-green-600">Browse</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Contacts</h3>
              <p className="text-gray-600 text-sm">
                Search, filter, and manage contact database
              </p>
            </div>
          </Link>

          <Link href="/dashboard/influencers" className="group">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow border-t-4 border-yellow-500">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-yellow-600" />
                <span className="text-sm text-gray-500 group-hover:text-yellow-600">Analyze</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Influencers</h3>
              <p className="text-gray-600 text-sm">
                Discover top influencers and key connectors
              </p>
            </div>
          </Link>

          <Link href="/dashboard/graph" className="group">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow border-t-4 border-purple-500">
              <div className="flex items-center justify-between mb-4">
                <Network className="w-8 h-8 text-purple-600" />
                <span className="text-sm text-gray-500 group-hover:text-purple-600">Visualize</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Network Graph</h3>
              <p className="text-gray-600 text-sm">
                Interactive visualization of contact networks
              </p>
            </div>
          </Link>
        </div>

        {/* Stats Preview */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <GitBranch className="w-6 h-6" />
            Platform Features
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">∞</div>
              <div className="text-gray-600">Unlimited Contacts</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">AI</div>
              <div className="text-gray-600">Smart Deduplication</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">⚡</div>
              <div className="text-gray-600">Real-time Sync</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
