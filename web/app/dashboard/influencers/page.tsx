'use client';

import { useEffect, useState } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_INFLUENCERS } from '@/lib/queries';
import { Contact, getContactDisplayName, getInfluencePercentage, getScoreColor, getScoreBgColor } from '@/types';
import { Loader2, TrendingUp, Award, Users } from 'lucide-react';
import Link from 'next/link';
import clsx from 'clsx';

export default function InfluencersPage() {
  const [influencers, setInfluencers] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInfluencers() {
      try {
        setLoading(true);
        const data = await fetchQuery<{ influencers: Contact[] }>(
          GET_INFLUENCERS,
          { limit: 50, minScore: 0.0 }
        );
        setInfluencers(data.influencers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load influencers');
        console.error('Failed to fetch influencers:', err);
      } finally {
        setLoading(false);
      }
    }

    loadInfluencers();
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Influencers</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="ml-3 text-gray-600">Loading influencers...</span>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <TrendingUp className="w-8 h-8 text-green-600" />
          Top Influencers
        </h1>
        <p className="text-gray-600">
          Discover the most influential contacts in your network based on connection strength and network position
        </p>
      </div>

      {/* Influencers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {influencers.map((contact, index) => {
          const score = contact.influenceScore || 0;
          const scorePercent = getInfluencePercentage(score);
          const rank = index + 1;
          
          return (
            <Link
              key={contact.id}
              href={`/dashboard/contacts/${contact.id}`}
              className="group"
            >
              <div className={clsx(
                "bg-white rounded-lg shadow-md hover:shadow-xl transition-all p-6 border-t-4",
                score >= 0.7 ? "border-green-500" :
                score >= 0.3 ? "border-yellow-500" :
                "border-red-500"
              )}>
                {/* Rank Badge */}
                <div className="flex items-start justify-between mb-4">
                  <div className={clsx(
                    "flex items-center justify-center w-10 h-10 rounded-full font-bold text-white",
                    rank <= 3 ? "bg-gradient-to-r from-yellow-400 to-yellow-600" :
                    rank <= 10 ? "bg-gradient-to-r from-gray-400 to-gray-600" :
                    "bg-gray-300 text-gray-700"
                  )}>
                    {rank <= 3 ? (
                      <Award className="w-6 h-6" />
                    ) : (
                      `#${rank}`
                    )}
                  </div>
                  
                  {/* Score Circle */}
                  <div className={clsx(
                    "flex items-center justify-center w-16 h-16 rounded-full font-bold text-lg",
                    getScoreBgColor(score),
                    getScoreColor(score)
                  )}>
                    {scorePercent}%
                  </div>
                </div>

                {/* Contact Info */}
                <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">
                  {getContactDisplayName(contact)}
                </h3>
                
                {contact.organization && (
                  <p className="text-sm text-gray-600 mb-3">{contact.organization}</p>
                )}

                {contact.email && (
                  <p className="text-sm text-gray-500 mb-3 truncate">{contact.email}</p>
                )}

                {/* Stats */}
                <div className="flex items-center justify-between pt-3 border-t">
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-4 h-4 mr-1" />
                    <span>{contact.connectionsCount || 0} connections</span>
                  </div>
                  
                  {contact.communityId !== null && contact.communityId !== undefined && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                      Community #{contact.communityId}
                    </span>
                  )}
                </div>

                {/* Tags */}
                {contact.tags && contact.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {contact.tags.slice(0, 3).map((tag, i) => (
                      <span 
                        key={i}
                        className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                    {contact.tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                        +{contact.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </div>

      {/* Empty State */}
      {influencers.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Influencers Found</h3>
          <p className="text-gray-600">
            Add contacts to your network to see influencer rankings
          </p>
        </div>
      )}
    </div>
  );
}
