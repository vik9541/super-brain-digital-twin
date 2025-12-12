"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getContactSentiment } from "@/lib/queries";
import { graphQLClient } from "@/lib/graphql-client";

interface SentimentComponents {
  tagsSentiment: number;
  notesSentiment: number;
  interactionsSentiment: number;
}

interface Sentiment {
  contactId: string;
  overallSentiment: number;
  sentimentLabel: string;
  components: SentimentComponents;
  analyzedAt: string;
  expiresAt: string;
}

export default function SentimentPage() {
  const [contactId, setContactId] = useState("");
  const [loading, setLoading] = useState(false);
  const [sentiment, setSentiment] = useState<Sentiment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchSentiment = async () => {
    if (!contactId.trim()) {
      setError("Please enter a contact ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await graphQLClient.request(getContactSentiment, {
        contactId,
      });

      setSentiment(data.contactSentiment);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch sentiment");
      console.error("Error fetching sentiment:", err);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentConfig = (label: string) => {
    switch (label) {
      case "Very Positive":
        return {
          color: "emerald",
          bg: "bg-gradient-to-br from-emerald-50 to-green-100",
          icon: "😊",
          emoji: "🌟",
          description: "Extremely positive relationship",
        };
      case "Positive":
        return {
          color: "green",
          bg: "bg-gradient-to-br from-green-50 to-lime-100",
          icon: "🙂",
          emoji: "✨",
          description: "Generally positive relationship",
        };
      case "Neutral":
        return {
          color: "gray",
          bg: "bg-gradient-to-br from-gray-50 to-slate-100",
          icon: "😐",
          emoji: "➖",
          description: "Neutral relationship",
        };
      case "Negative":
        return {
          color: "orange",
          bg: "bg-gradient-to-br from-orange-50 to-yellow-100",
          icon: "🙁",
          emoji: "⚠️",
          description: "Somewhat negative relationship",
        };
      case "Very Negative":
        return {
          color: "red",
          bg: "bg-gradient-to-br from-red-50 to-rose-100",
          icon: "😠",
          emoji: "🚨",
          description: "Very negative relationship",
        };
      default:
        return {
          color: "gray",
          bg: "bg-gradient-to-br from-gray-50 to-slate-100",
          icon: "😐",
          emoji: "➖",
          description: "Unknown sentiment",
        };
    }
  };

  const getSentimentBarColor = (value: number) => {
    if (value > 0.5) return "bg-green-500";
    if (value > 0.2) return "bg-lime-500";
    if (value > -0.2) return "bg-gray-400";
    if (value > -0.5) return "bg-orange-500";
    return "bg-red-500";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2 font-medium"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900">
            😊 Contact Sentiment Analysis
          </h1>
          <p className="text-gray-600 mt-2 text-lg">
            Multi-component sentiment analysis using tags, notes, and interaction patterns
          </p>
        </div>

        {/* Search */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter Contact ID (UUID)"
              value={contactId}
              onChange={(e) => setContactId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchSentiment()}
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
            />
            <button
              onClick={fetchSentiment}
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all font-semibold shadow-md"
            >
              {loading ? "Analyzing..." : "Analyze Sentiment"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Sentiment Results */}
        {sentiment && (
          <div>
            {(() => {
              const config = getSentimentConfig(sentiment.sentimentLabel);

              return (
                <>
                  {/* Overall Sentiment Card */}
                  <div className={`${config.bg} rounded-xl p-8 mb-6 shadow-xl border-2 border-${config.color}-200`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-6">
                        <div className="text-8xl">{config.icon}</div>
                        <div>
                          <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-1">
                            Overall Sentiment
                          </p>
                          <h2 className="text-4xl font-bold text-gray-900 mb-2">
                            {sentiment.sentimentLabel}
                          </h2>
                          <p className="text-lg text-gray-700">
                            {config.emoji} {config.description}
                          </p>
                        </div>
                      </div>

                      {/* Sentiment Score */}
                      <div className="text-center">
                        <div className="text-5xl font-bold text-gray-900">
                          {sentiment.overallSentiment > 0 ? "+" : ""}
                          {sentiment.overallSentiment.toFixed(2)}
                        </div>
                        <p className="text-sm text-gray-600 mt-2">
                          Sentiment Score
                        </p>
                        <p className="text-xs text-gray-500">
                          (-1 to +1 scale)
                        </p>
                      </div>
                    </div>

                    {/* Sentiment Bar */}
                    <div className="mt-6">
                      <div className="relative w-full h-6 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="absolute top-0 left-1/2 w-px h-6 bg-gray-400 z-10"
                        />
                        <div
                          className={`h-6 ${getSentimentBarColor(sentiment.overallSentiment)} transition-all`}
                          style={{
                            width: `${Math.abs(sentiment.overallSentiment) * 50}%`,
                            marginLeft: sentiment.overallSentiment >= 0 ? "50%" : `${50 - Math.abs(sentiment.overallSentiment) * 50}%`,
                          }}
                        />
                      </div>
                      <div className="flex justify-between mt-2 text-xs text-gray-600">
                        <span>Very Negative (-1.0)</span>
                        <span>Neutral (0)</span>
                        <span>Very Positive (+1.0)</span>
                      </div>
                    </div>
                  </div>

                  {/* Component Breakdown */}
                  <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      📊 Component Breakdown
                    </h3>
                    <p className="text-sm text-gray-600 mb-6">
                      Weighted analysis: Tags (40%), Notes (30%), Interactions (30%)
                    </p>

                    <div className="space-y-6">
                      {/* Tags Sentiment */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              🏷️ Tags Sentiment
                            </h4>
                            <p className="text-sm text-gray-600">
                              Based on positive/negative keyword matching (40% weight)
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">
                              {sentiment.components.tagsSentiment > 0 ? "+" : ""}
                              {sentiment.components.tagsSentiment.toFixed(2)}
                            </div>
                          </div>
                        </div>
                        <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div className="absolute top-0 left-1/2 w-px h-4 bg-gray-400 z-10" />
                          <div
                            className={`h-4 ${getSentimentBarColor(sentiment.components.tagsSentiment)} transition-all`}
                            style={{
                              width: `${Math.abs(sentiment.components.tagsSentiment) * 50}%`,
                              marginLeft: sentiment.components.tagsSentiment >= 0 ? "50%" : `${50 - Math.abs(sentiment.components.tagsSentiment) * 50}%`,
                            }}
                          />
                        </div>
                      </div>

                      {/* Notes Sentiment */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              📝 Notes Sentiment
                            </h4>
                            <p className="text-sm text-gray-600">
                              TextBlob NLP polarity analysis (30% weight)
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">
                              {sentiment.components.notesSentiment > 0 ? "+" : ""}
                              {sentiment.components.notesSentiment.toFixed(2)}
                            </div>
                          </div>
                        </div>
                        <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div className="absolute top-0 left-1/2 w-px h-4 bg-gray-400 z-10" />
                          <div
                            className={`h-4 ${getSentimentBarColor(sentiment.components.notesSentiment)} transition-all`}
                            style={{
                              width: `${Math.abs(sentiment.components.notesSentiment) * 50}%`,
                              marginLeft: sentiment.components.notesSentiment >= 0 ? "50%" : `${50 - Math.abs(sentiment.components.notesSentiment) * 50}%`,
                            }}
                          />
                        </div>
                      </div>

                      {/* Interactions Sentiment */}
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              💬 Interactions Sentiment
                            </h4>
                            <p className="text-sm text-gray-600">
                              Frequency-based engagement analysis (30% weight)
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-gray-900">
                              {sentiment.components.interactionsSentiment > 0 ? "+" : ""}
                              {sentiment.components.interactionsSentiment.toFixed(2)}
                            </div>
                          </div>
                        </div>
                        <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div className="absolute top-0 left-1/2 w-px h-4 bg-gray-400 z-10" />
                          <div
                            className={`h-4 ${getSentimentBarColor(sentiment.components.interactionsSentiment)} transition-all`}
                            style={{
                              width: `${Math.abs(sentiment.components.interactionsSentiment) * 50}%`,
                              marginLeft: sentiment.components.interactionsSentiment >= 0 ? "50%" : `${50 - Math.abs(sentiment.components.interactionsSentiment) * 50}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div>
                        <p className="font-semibold text-gray-900 mb-1">Analysis Timestamp</p>
                        <p>{new Date(sentiment.analyzedAt).toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900 mb-1">Cache Expires</p>
                        <p>{new Date(sentiment.expiresAt).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-xs text-gray-500 text-center">
                        Sentiment refreshed every 14 days or when contact data changes
                      </p>
                    </div>
                  </div>
                </>
              );
            })()}
          </div>
        )}

        {/* Empty State */}
        {!loading && !sentiment && !error && (
          <div className="bg-white rounded-xl shadow-lg p-16 text-center">
            <div className="text-8xl mb-6">😊</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Analyze Contact Sentiment
            </h3>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Enter a contact ID to perform multi-component sentiment analysis
              <br />
              We analyze tags (40%), notes with NLP (30%), and interaction patterns (30%)
              <br />
              to generate an overall sentiment score from -1 (negative) to +1 (positive)
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
