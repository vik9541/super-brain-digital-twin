'use client';

import { useEffect, useState } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_COMMUNITIES } from '@/lib/queries';
import { Community, getContactDisplayName } from '@/types';
import { Loader2, GitMerge, Users, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function CommunitiesPage() {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCommunities() {
      try {
        setLoading(true);
        const data = await fetchQuery<{ communities: Community[] }>(
          GET_COMMUNITIES,
          { minSize: 1 }
        );
        setCommunities(data.communities);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load communities');
        console.error('Failed to fetch communities:', err);
      } finally {
        setLoading(false);
      }
    }

    loadCommunities();
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Communities</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
        <span className="ml-3 text-gray-600">Loading communities...</span>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <GitMerge className="w-8 h-8 text-purple-600" />
          Communities
        </h1>
        <p className="text-gray-600">
          Detected contact clusters and groups based on connection patterns
        </p>
      </div>

      {/* Communities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {communities.map((community) => (
          <div
            key={community.id}
            className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 border-t-4 border-purple-500"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {community.name || `Community #${community.id}`}
                </h3>
                <div className="flex items-center text-sm text-gray-500 mt-1">
                  <Users className="w-4 h-4 mr-1" />
                  <span>{community.size} members</span>
                </div>
              </div>
              
              <div className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                #{community.id}
              </div>
            </div>

            {/* Avg Influence Score */}
            {community.avgInfluenceScore !== undefined && community.avgInfluenceScore !== null && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600">Avg Influence</span>
                  <span className="font-semibold text-purple-700">
                    {(community.avgInfluenceScore * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full transition-all"
                    style={{ width: `${community.avgInfluenceScore * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Top Members */}
            {community.topMembers && community.topMembers.length > 0 && (
              <div className="border-t pt-4">
                <div className="flex items-center text-xs text-gray-500 mb-2">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  <span>Top Members</span>
                </div>
                <div className="space-y-2">
                  {community.topMembers.slice(0, 3).map((member) => (
                    <Link
                      key={member.id}
                      href={`/dashboard/contacts/${member.id}`}
                      className="flex items-center justify-between text-sm hover:bg-purple-50 p-2 rounded transition-colors"
                    >
                      <span className="text-gray-700 truncate">
                        {getContactDisplayName(member)}
                      </span>
                      <span className="text-purple-600 font-semibold ml-2">
                        {member.influenceScore 
                          ? `${Math.round(member.influenceScore * 100)}%`
                          : '-'}
                      </span>
                    </Link>
                  ))}
                </div>
                {community.size > 3 && (
                  <div className="text-xs text-gray-500 text-center mt-2">
                    +{community.size - 3} more members
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {communities.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <GitMerge className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Communities Detected</h3>
          <p className="text-gray-600">
            Communities will appear here once contact connections are analyzed
          </p>
        </div>
      )}

      {/* Stats Summary */}
      {communities.length > 0 && (
        <div className="mt-8 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Community Analytics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold mb-1">{communities.length}</div>
              <div className="text-purple-100">Total Communities</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">
                {Math.round(
                  communities.reduce((sum, c) => sum + c.size, 0) / communities.length
                )}
              </div>
              <div className="text-purple-100">Avg Community Size</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">
                {Math.max(...communities.map(c => c.size))}
              </div>
              <div className="text-purple-100">Largest Community</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
