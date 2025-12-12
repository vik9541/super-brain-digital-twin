"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getContactClusters } from "@/lib/queries";
import { graphQLClient } from "@/lib/graphql-client";

interface Contact {
  id: string;
  firstName: string;
  lastName: string;
  organization?: string;
  influenceScore?: number;
}

interface Cluster {
  clusterId: number;
  clusterSize: number;
  clusterTopics: string[];
  sampleContacts?: Contact[];
}

export default function ClustersPage() {
  const [loading, setLoading] = useState(false);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchClusters();
  }, []);

  const fetchClusters = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await graphQLClient.request(getContactClusters);
      setClusters(data.contactClusters || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch clusters");
      console.error("Error fetching clusters:", err);
    } finally {
      setLoading(false);
    }
  };

  const getClusterColor = (index: number) => {
    const colors = [
      { bg: "bg-blue-100", border: "border-blue-500", text: "text-blue-700", badge: "bg-blue-500" },
      { bg: "bg-purple-100", border: "border-purple-500", text: "text-purple-700", badge: "bg-purple-500" },
      { bg: "bg-green-100", border: "border-green-500", text: "text-green-700", badge: "bg-green-500" },
      { bg: "bg-orange-100", border: "border-orange-500", text: "text-orange-700", badge: "bg-orange-500" },
      { bg: "bg-pink-100", border: "border-pink-500", text: "text-pink-700", badge: "bg-pink-500" },
    ];
    return colors[index % colors.length];
  };

  const totalContacts = clusters.reduce((sum, cluster) => sum + cluster.clusterSize, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-8">
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
            🗂️ Contact Clusters
          </h1>
          <p className="text-gray-600 mt-2 text-lg">
            K-means clustering on contact embeddings with automatic topic inference
          </p>
        </div>

        {/* Stats Bar */}
        {clusters.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{clusters.length}</p>
                <p className="text-sm text-gray-600 mt-1">Total Clusters</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">{totalContacts}</p>
                <p className="text-sm text-gray-600 mt-1">Total Contacts</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">
                  {Math.round(totalContacts / clusters.length)}
                </p>
                <p className="text-sm text-gray-600 mt-1">Avg Cluster Size</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-orange-600">
                  {Math.max(...clusters.map(c => c.clusterTopics?.length || 0))}
                </p>
                <p className="text-sm text-gray-600 mt-1">Max Topics/Cluster</p>
              </div>
            </div>

            <button
              onClick={fetchClusters}
              disabled={loading}
              className="mt-4 w-full px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:bg-gray-400 transition-all font-semibold"
            >
              {loading ? "Refreshing..." : "🔄 Refresh Clusters"}
            </button>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mb-6">
            <p className="text-red-700 font-semibold">Error Loading Clusters</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && clusters.length === 0 && (
          <div className="bg-white rounded-xl shadow-lg p-16 text-center">
            <div className="animate-spin text-6xl mb-4">⚙️</div>
            <p className="text-xl font-semibold text-gray-700">
              Loading contact clusters...
            </p>
          </div>
        )}

        {/* Clusters Grid */}
        {!loading && clusters.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {clusters.map((cluster, index) => {
              const colors = getClusterColor(index);

              return (
                <div
                  key={cluster.clusterId}
                  className={`bg-white rounded-xl shadow-lg hover:shadow-xl transition-all overflow-hidden border-2 ${colors.border}`}
                >
                  {/* Cluster Header */}
                  <div className={`${colors.bg} p-6 border-b-2 ${colors.border}`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-2xl font-bold text-gray-900">
                          Cluster #{cluster.clusterId}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {cluster.clusterSize} contacts
                        </p>
                      </div>
                      <div className={`w-16 h-16 ${colors.badge} rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg`}>
                        {cluster.clusterId}
                      </div>
                    </div>
                  </div>

                  {/* Topics */}
                  <div className="p-6 border-b border-gray-200 bg-gray-50">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">
                      🏷️ Top Topics & Interests
                    </h4>
                    {cluster.clusterTopics && cluster.clusterTopics.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {cluster.clusterTopics.slice(0, 10).map((topic) => (
                          <span
                            key={topic}
                            className={`px-3 py-1 ${colors.bg} ${colors.text} rounded-full text-sm font-medium border ${colors.border}`}
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">
                        No topics inferred
                      </p>
                    )}
                  </div>

                  {/* Sample Contacts */}
                  <div className="p-6">
                    <h4 className="text-sm font-semibold text-gray-700 mb-4">
                      👥 Sample Members ({cluster.sampleContacts?.length || 0} shown)
                    </h4>
                    {cluster.sampleContacts && cluster.sampleContacts.length > 0 ? (
                      <div className="space-y-3">
                        {cluster.sampleContacts.map((contact) => (
                          <div
                            key={contact.id}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                            onClick={() => router.push(`/dashboard/contacts/${contact.id}`)}
                          >
                            <div>
                              <p className="font-semibold text-gray-900">
                                {contact.firstName} {contact.lastName}
                              </p>
                              {contact.organization && (
                                <p className="text-sm text-gray-600">
                                  {contact.organization}
                                </p>
                              )}
                            </div>
                            {contact.influenceScore !== undefined && (
                              <div className="text-right">
                                <div className="text-sm font-bold text-gray-900">
                                  {(contact.influenceScore * 100).toFixed(0)}%
                                </div>
                                <div className="text-xs text-gray-500">
                                  Influence
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">
                        No sample contacts available
                      </p>
                    )}

                    {cluster.clusterSize > (cluster.sampleContacts?.length || 0) && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-600 text-center">
                          + {cluster.clusterSize - (cluster.sampleContacts?.length || 0)} more contacts in this cluster
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Cluster Stats Footer */}
                  <div className={`${colors.bg} px-6 py-3 border-t-2 ${colors.border}`}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">
                        {((cluster.clusterSize / totalContacts) * 100).toFixed(1)}% of total
                      </span>
                      <button
                        className={`${colors.text} hover:underline font-semibold`}
                        onClick={() => {
                          // Future: Navigate to detailed cluster view
                          console.log(`View all contacts in cluster ${cluster.clusterId}`);
                        }}
                      >
                        View All →
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Empty State */}
        {!loading && clusters.length === 0 && !error && (
          <div className="bg-white rounded-xl shadow-lg p-16 text-center">
            <div className="text-8xl mb-6">🗂️</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">
              No Clusters Found
            </h3>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto mb-6">
              Clusters are generated nightly at 05:00 UTC using K-means algorithm
              <br />
              on contact embeddings. Topics are inferred from common tags and organizations.
            </p>
            <button
              onClick={fetchClusters}
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-semibold shadow-md"
            >
              Refresh Clusters
            </button>
          </div>
        )}

        {/* Info Card */}
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg">
          <h4 className="text-lg font-semibold text-blue-900 mb-2">
            ℹ️ How Clustering Works
          </h4>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• <strong>Algorithm:</strong> K-means clustering on 1536-dimensional OpenAI embeddings</li>
            <li>• <strong>Update Frequency:</strong> Nightly at 05:00 UTC (after embeddings generation)</li>
            <li>• <strong>Topic Inference:</strong> Top 5 most common tags and organizations per cluster</li>
            <li>• <strong>Default Clusters:</strong> n_clusters=5 (can be adjusted)</li>
            <li>• <strong>Use Cases:</strong> Interest groups, targeted campaigns, community segmentation</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
