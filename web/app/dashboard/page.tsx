'use client';

import { useEffect, useState } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_NETWORK_STATS } from '@/lib/queries';
import { NetworkStats } from '@/types';
import { Users, TrendingUp, GitMerge, Clock, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { getContactDisplayName, getInfluencePercentage } from '@/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const data = await fetchQuery<{ networkStats: NetworkStats }>(GET_NETWORK_STATS);
        setStats(data.networkStats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats');
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    }

    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h3>
        <p className="text-red-600">{error}</p>
        <p className="text-sm text-red-500 mt-2">
          Make sure the GraphQL API is running at {process.env.NEXT_PUBLIC_GRAPHQL_URL}
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Network Intelligence Dashboard</h1>
        <p className="text-gray-600">Overview of your contact network and analytics</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Contacts */}
        <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-blue-500">
          <div className="flex items-center justify-between mb-4">
            <Users className="w-8 h-8 text-blue-600" />
            <span className="text-sm text-gray-500">Total</span>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {stats?.totalContacts?.toLocaleString() || 0}
          </div>
          <div className="text-sm text-gray-600">Contacts</div>
          <Link
            href="/dashboard/contacts"
            className="text-blue-600 hover:text-blue-700 text-sm font-medium mt-2 inline-block"
          >
            View all →
          </Link>
        </div>

        {/* Top Influencer */}
        <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-green-500">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <span className="text-sm text-gray-500">Score</span>
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1 truncate">
            {stats?.topInfluencer ? getContactDisplayName(stats.topInfluencer) : 'N/A'}
          </div>
          <div className="text-sm text-gray-600">
            Top Influencer: {stats?.topInfluencer ? `${getInfluencePercentage(stats.topInfluencer.influenceScore)}%` : 'N/A'}
          </div>
          <Link
            href="/dashboard/influencers"
            className="text-green-600 hover:text-green-700 text-sm font-medium mt-2 inline-block"
          >
            View ranking →
          </Link>
        </div>

        {/* Communities */}
        <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-purple-500">
          <div className="flex items-center justify-between mb-4">
            <GitMerge className="w-8 h-8 text-purple-600" />
            <span className="text-sm text-gray-500">Detected</span>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {stats?.communitiesCount || 0}
          </div>
          <div className="text-sm text-gray-600">Communities</div>
          <Link
            href="/dashboard/communities"
            className="text-purple-600 hover:text-purple-700 text-sm font-medium mt-2 inline-block"
          >
            Explore →
          </Link>
        </div>

        {/* Last Sync */}
        <div className="bg-white rounded-lg shadow-md p-6 border-t-4 border-yellow-500">
          <div className="flex items-center justify-between mb-4">
            <Clock className="w-8 h-8 text-yellow-600" />
            <span className="text-sm text-gray-500">Status</span>
          </div>
          <div className="text-lg font-bold text-gray-900 mb-1">
            {stats?.lastSyncTime ? new Date(stats.lastSyncTime).toLocaleDateString() : 'Never'}
          </div>
          <div className="text-sm text-gray-600">Last Sync Time</div>
          <div className="text-sm text-green-600 font-medium mt-2">
            ✓ System online
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/dashboard/contacts"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <Users className="w-6 h-6 text-blue-600" />
            <div>
              <div className="font-medium text-gray-900">Browse Contacts</div>
              <div className="text-sm text-gray-500">Search and filter</div>
            </div>
          </Link>

          <Link
            href="/dashboard/graph"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors"
          >
            <GitMerge className="w-6 h-6 text-purple-600" />
            <div>
              <div className="font-medium text-gray-900">Network Graph</div>
              <div className="text-sm text-gray-500">Visualize connections</div>
            </div>
          </Link>

          <Link
            href="/dashboard/influencers"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors"
          >
            <TrendingUp className="w-6 h-6 text-green-600" />
            <div>
              <div className="font-medium text-gray-900">Top Influencers</div>
              <div className="text-sm text-gray-500">View ranking</div>
            </div>
          </Link>
        </div>
      </div>

      {/* Additional Stats */}
      {stats && (
        <div className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Network Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold mb-1">{stats.totalConnections?.toLocaleString() || 0}</div>
              <div className="text-blue-100">Total Connections</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">
                {stats.avgInfluenceScore ? (stats.avgInfluenceScore * 100).toFixed(1) + '%' : 'N/A'}
              </div>
              <div className="text-blue-100">Avg Influence Score</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">
                {stats.totalContacts && stats.communitiesCount 
                  ? Math.round(stats.totalContacts / stats.communitiesCount)
                  : 0}
              </div>
              <div className="text-blue-100">Avg Community Size</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
