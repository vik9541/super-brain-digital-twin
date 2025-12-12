"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getChurnRisk } from "@/lib/queries";
import { graphQLClient } from "@/lib/graphql-client";

interface ChurnFeatures {
  daysSinceUpdateNorm: number;
  interactionFrequencyNorm: number;
  inverseInfluence: number;
  tagCountNorm: number;
  communitySizeNorm: number;
}

interface ChurnPrediction {
  contactId: string;
  churnProbability: number;
  riskLevel: string;
  features: ChurnFeatures;
  interventions: string[];
  predictedAt: string;
  expiresAt: string;
}

export default function ChurnRiskPage() {
  const [contactId, setContactId] = useState("");
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<ChurnPrediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const fetchChurnRisk = async () => {
    if (!contactId.trim()) {
      setError("Please enter a contact ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await graphQLClient.request(getChurnRisk, {
        contactId,
      });

      setPrediction(data.churnRisk);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch churn prediction");
      console.error("Error fetching churn risk:", err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskConfig = (level: string) => {
    switch (level) {
      case "HIGH":
        return {
          color: "red",
          bg: "bg-red-50",
          border: "border-red-500",
          text: "text-red-700",
          badge: "bg-red-500",
          icon: "⚠️",
          label: "HIGH RISK",
        };
      case "MEDIUM":
        return {
          color: "yellow",
          bg: "bg-yellow-50",
          border: "border-yellow-500",
          text: "text-yellow-700",
          badge: "bg-yellow-500",
          icon: "⚡",
          label: "MEDIUM RISK",
        };
      default:
        return {
          color: "green",
          bg: "bg-green-50",
          border: "border-green-500",
          text: "text-green-700",
          badge: "bg-green-500",
          icon: "✅",
          label: "LOW RISK",
        };
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 p-8">
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
            ⚠️ Contact Churn Prediction
          </h1>
          <p className="text-gray-600 mt-2 text-lg">
            ML-powered churn risk analysis with actionable interventions
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
              onKeyDown={(e) => e.key === "Enter" && fetchChurnRisk()}
              className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-lg"
            />
            <button
              onClick={fetchChurnRisk}
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg hover:from-red-700 hover:to-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all font-semibold shadow-md"
            >
              {loading ? "Analyzing..." : "Analyze Risk"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Prediction Results */}
        {prediction && (
          <div>
            {(() => {
              const config = getRiskConfig(prediction.riskLevel);

              return (
                <>
                  {/* Risk Level Card */}
                  <div className={`${config.bg} border-4 ${config.border} rounded-xl p-8 mb-6 shadow-xl`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-6">
                        <div className="text-7xl">{config.icon}</div>
                        <div>
                          <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-1">
                            Churn Risk Assessment
                          </p>
                          <h2 className={`text-4xl font-bold ${config.text}`}>
                            {config.label}
                          </h2>
                          <p className="text-lg font-semibold text-gray-700 mt-2">
                            {(prediction.churnProbability * 100).toFixed(1)}% probability of churning
                          </p>
                        </div>
                      </div>

                      {/* Probability Gauge */}
                      <div className="text-center">
                        <div className="relative w-32 h-32">
                          <svg className="transform -rotate-90 w-32 h-32">
                            <circle
                              cx="64"
                              cy="64"
                              r="56"
                              stroke="#e5e7eb"
                              strokeWidth="12"
                              fill="none"
                            />
                            <circle
                              cx="64"
                              cy="64"
                              r="56"
                              stroke={config.badge.replace("bg-", "#")}
                              strokeWidth="12"
                              fill="none"
                              strokeDasharray={`${2 * Math.PI * 56}`}
                              strokeDashoffset={`${2 * Math.PI * 56 * (1 - prediction.churnProbability)}`}
                              strokeLinecap="round"
                            />
                          </svg>
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-2xl font-bold text-gray-900">
                              {(prediction.churnProbability * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Features Breakdown */}
                  <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      📊 Feature Analysis
                    </h3>
                    <p className="text-sm text-gray-600 mb-6">
                      5 normalized features used by RandomForest ML model (0 = good, 1 = concerning)
                    </p>

                    <div className="space-y-4">
                      {/* Days Since Update */}
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            📅 Days Since Last Update
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {(prediction.features.daysSinceUpdateNorm * 365).toFixed(0)} days
                            ({(prediction.features.daysSinceUpdateNorm * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-red-500 h-3 rounded-full transition-all"
                            style={{ width: `${prediction.features.daysSinceUpdateNorm * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Interaction Frequency */}
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            💬 Interaction Frequency (last 90 days)
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {(prediction.features.interactionFrequencyNorm * 3).toFixed(1)} interactions
                            ({(prediction.features.interactionFrequencyNorm * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-blue-500 h-3 rounded-full transition-all"
                            style={{ width: `${prediction.features.interactionFrequencyNorm * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Inverse Influence */}
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            ⭐ Inverse Influence Score
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {((1 - prediction.features.inverseInfluence) * 100).toFixed(0)}% influence
                            ({(prediction.features.inverseInfluence * 100).toFixed(0)}% inverse)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-purple-500 h-3 rounded-full transition-all"
                            style={{ width: `${prediction.features.inverseInfluence * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Tag Count */}
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            🏷️ Tag Engagement
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {(prediction.features.tagCountNorm * 10).toFixed(0)} tags
                            ({(prediction.features.tagCountNorm * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-green-500 h-3 rounded-full transition-all"
                            style={{ width: `${prediction.features.tagCountNorm * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Community Size */}
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            👥 Community Size
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {(prediction.features.communitySizeNorm * 100).toFixed(0)} members
                            ({(prediction.features.communitySizeNorm * 100).toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className="bg-yellow-500 h-3 rounded-full transition-all"
                            style={{ width: `${prediction.features.communitySizeNorm * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Interventions */}
                  <div className="bg-white rounded-xl shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      💡 Recommended Interventions
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Actionable steps to reduce churn risk
                    </p>

                    <div className="space-y-3">
                      {prediction.interventions.map((intervention, index) => (
                        <div
                          key={index}
                          className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg hover:bg-blue-100 transition-colors"
                        >
                          <p className="text-sm font-medium text-gray-900">
                            {intervention}
                          </p>
                        </div>
                      ))}
                    </div>

                    <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                      <span>
                        Predicted: {new Date(prediction.predictedAt).toLocaleString()}
                      </span>
                      <span>
                        Expires: {new Date(prediction.expiresAt).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </>
              );
            })()}
          </div>
        )}

        {/* Empty State */}
        {!loading && !prediction && !error && (
          <div className="bg-white rounded-xl shadow-lg p-16 text-center">
            <div className="text-8xl mb-6">📊</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              Predict Churn Risk
            </h3>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Enter a contact ID to analyze churn probability using our RandomForest ML model
              <br />
              Get detailed feature breakdown and actionable intervention recommendations
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
