"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getRecommendedContacts } from "@/lib/queries";
import { graphQLClient } from "@/lib/graphql-client";

interface ScoreComponents {
  mutualFriends: number;
  semanticSimilarity: number;
  influenceScore: number;
  sameOrganization: number;
}

interface Recommendation {
  contactId: string;
  firstName: string;
  lastName: string;
  organization?: string;
  influenceScore: number;
  totalScore: number;
  components: ScoreComponents;
  reason: string;
}

export default function RecommendationsPage() {
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchRecommendations = async (uid: string) => {
    setLoading(true);
    setError(null);

    try {
      const data = await graphQLClient.request(getRecommendedContacts, {
        userId: uid,
        limit: 20,
        minScore: 0.6,
      });

      setRecommendations(data.recommendedContacts || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch recommendations");
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.85) return "bg-green-500";
    if (score >= 0.75) return "bg-blue-500";
    if (score >= 0.65) return "bg-yellow-500";
    return "bg-gray-400";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 0.85) return { label: "Excellent Match", color: "bg-green-100 text-green-800" };
    if (score >= 0.75) return { label: "Good Match", color: "bg-blue-100 text-blue-800" };
    if (score >= 0.65) return { label: "Decent Match", color: "bg-yellow-100 text-yellow-800" };
    return { label: "Possible Match", color: "bg-gray-100 text-gray-800" };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2 font-medium"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900">
            🎯 People You Should Know
          </h1>
          <p className="text-gray-600 mt-2 text-lg">
            AI-powered recommendations based on mutual connections, interests, and influence
          </p>
        </div>

        {/* User ID Input */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter Your Contact ID (UUID)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && userId && fetchRecommendations(userId)}
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            />
            <button
              onClick={() => userId && fetchRecommendations(userId)}
              disabled={loading || !userId}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all font-semibold shadow-md"
            >
              {loading ? "Loading..." : "Get Recommendations"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded text-red-700">
              <p className="font-semibold">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}
        </div>

        {/* Recommendations Grid */}
        {recommendations.length > 0 && (
          <div>
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                {recommendations.length} Recommendations
              </h2>
              <p className="text-gray-600">
                Based on 4-component scoring algorithm
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recommendations.map((rec, index) => {
                const badge = getScoreBadge(rec.totalScore);
                
                return (
                  <div
                    key={rec.contactId}
                    className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all overflow-hidden"
                  >
                    {/* Header with Score */}
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border-b border-gray-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-3xl font-bold text-gray-400">
                              #{index + 1}
                            </span>
                            <div>
                              <h3 className="text-xl font-bold text-gray-900">
                                {rec.firstName} {rec.lastName}
                              </h3>
                              {rec.organization && (
                                <p className="text-sm text-gray-600 mt-1">
                                  {rec.organization}
                                </p>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center gap-3 mt-3">
                            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badge.color}`}>
                              {badge.label}
                            </span>
                            <span className="text-sm text-gray-600">
                              Influence: {(rec.influenceScore * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-3xl font-bold text-blue-600">
                            {(rec.totalScore * 100).toFixed(0)}
                          </div>
                          <p className="text-xs text-gray-500 mt-1">Match Score</p>
                        </div>
                      </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="p-6">
                      <div className="mb-4">
                        <p className="text-sm text-gray-700 font-medium mb-3">
                          📊 Score Breakdown
                        </p>
                        <div className="space-y-2">
                          {/* Mutual Friends */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Mutual Friends (30%)</span>
                              <span className="font-semibold">{(rec.components.mutualFriends * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-purple-500 h-2 rounded-full transition-all"
                                style={{ width: `${rec.components.mutualFriends * 100}%` }}
                              />
                            </div>
                          </div>

                          {/* Semantic Similarity */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Similar Interests (30%)</span>
                              <span className="font-semibold">{(rec.components.semanticSimilarity * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full transition-all"
                                style={{ width: `${rec.components.semanticSimilarity * 100}%` }}
                              />
                            </div>
                          </div>

                          {/* Influence */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Influence (25%)</span>
                              <span className="font-semibold">{(rec.components.influenceScore * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-green-500 h-2 rounded-full transition-all"
                                style={{ width: `${rec.components.influenceScore * 100}%` }}
                              />
                            </div>
                          </div>

                          {/* Same Organization */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Same Organization (15%)</span>
                              <span className="font-semibold">{rec.components.sameOrganization > 0 ? "Yes" : "No"}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-yellow-500 h-2 rounded-full transition-all"
                                style={{ width: `${rec.components.sameOrganization * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Reason */}
                      <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 mb-4">
                        <p className="text-sm text-gray-700">
                          💡 <span className="font-semibold">Why?</span> {rec.reason}
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-3">
                        <button
                          onClick={() => router.push(`/dashboard/contacts/${rec.contactId}`)}
                          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                        >
                          View Profile
                        </button>
                        <button
                          className="flex-1 px-4 py-2 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium text-sm"
                        >
                          Connect
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && recommendations.length === 0 && !error && (
          <div className="bg-white rounded-xl shadow-lg p-16 text-center">
            <div className="text-8xl mb-6">🎯</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Discover Your Network
            </h3>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Enter your contact ID to get personalized recommendations
              <br />
              We'll analyze mutual connections, shared interests, influence scores,
              <br />
              and organizational relationships to find the best matches
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
