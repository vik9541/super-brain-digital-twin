"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getSimilarContacts } from "@/lib/queries";
import { graphQLClient } from "@/lib/graphql-client";

interface SimilarContact {
  contactId: string;
  firstName: string;
  lastName: string;
  organization?: string;
  similarityScore: number;
  commonTags?: string[];
}

export default function SimilarContactsPage() {
  const [contactId, setContactId] = useState("");
  const [loading, setLoading] = useState(false);
  const [similarContacts, setSimilarContacts] = useState<SimilarContact[]>([]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSearch = async () => {
    if (!contactId.trim()) {
      setError("Please enter a contact ID");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await graphQLClient.request(getSimilarContacts, {
        contactId,
        limit: 10,
      });

      setSimilarContacts(data.similarContacts || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch similar contacts");
      console.error("Error fetching similar contacts:", err);
    } finally {
      setLoading(false);
    }
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return "text-green-600 bg-green-50";
    if (score >= 0.8) return "text-blue-600 bg-blue-50";
    if (score >= 0.7) return "text-yellow-600 bg-yellow-50";
    return "text-gray-600 bg-gray-50";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            🔍 Similar Contacts
          </h1>
          <p className="text-gray-600 mt-2">
            Find semantically similar contacts using AI-powered embeddings
          </p>
        </div>

        {/* Search Input */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Enter Contact ID (UUID)"
              value={contactId}
              onChange={(e) => setContactId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {similarContacts.length > 0 && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h2 className="text-xl font-semibold text-gray-900">
                Found {similarContacts.length} Similar Contacts
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Ranked by cosine similarity (OpenAI embeddings)
              </p>
            </div>

            <div className="divide-y divide-gray-200">
              {similarContacts.map((contact, index) => (
                <div
                  key={contact.contactId}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl font-bold text-gray-400">
                          #{index + 1}
                        </span>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {contact.firstName} {contact.lastName}
                          </h3>
                          {contact.organization && (
                            <p className="text-sm text-gray-600">
                              {contact.organization}
                            </p>
                          )}
                        </div>
                      </div>

                      {contact.commonTags && contact.commonTags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {contact.commonTags.map((tag) => (
                            <span
                              key={tag}
                              className="px-3 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="ml-6">
                      <div
                        className={`px-4 py-2 rounded-lg font-semibold ${getSimilarityColor(
                          contact.similarityScore
                        )}`}
                      >
                        {(contact.similarityScore * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-center">
                        Similarity
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <button
                      onClick={() => router.push(`/dashboard/contacts/${contact.contactId}`)}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      View Full Profile →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && similarContacts.length === 0 && !error && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Find Similar Contacts
            </h3>
            <p className="text-gray-600">
              Enter a contact ID above to discover semantically similar people
              <br />
              using AI-powered OpenAI embeddings
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
