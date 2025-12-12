'use client';

import { useEffect, useState } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_NETWORK_GRAPH } from '@/lib/queries';
import { NetworkGraph as NetworkGraphType } from '@/types';
import NetworkGraph from '@/components/NetworkGraph';
import PathFinder from '@/components/PathFinder';
import { Loader2, Network } from 'lucide-react';

export default function GraphPage() {
  const [graphData, setGraphData] = useState<NetworkGraphType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadGraph() {
      try {
        setLoading(true);
        const data = await fetchQuery<{ networkGraph: NetworkGraphType }>(
          GET_NETWORK_GRAPH,
          { limit: 200 } // Limit nodes for performance
        );
        setGraphData(data.networkGraph);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load network graph');
        console.error('Failed to fetch graph:', err);
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Network Graph</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Network className="w-8 h-8 text-purple-600" />
          Network Visualization
        </h1>
        <p className="text-gray-600">
          Interactive graph showing contact relationships and community structures
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center min-h-[600px] bg-white rounded-lg shadow-md">
          <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
          <span className="ml-3 text-gray-600">Loading network graph...</span>
        </div>
      )}

      {/* Network Graph */}
      {!loading && graphData && (
        <div className="space-y-6">
          <NetworkGraph data={graphData} />
          
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="text-2xl font-bold text-gray-900">
                {graphData.nodes.length}
              </div>
              <div className="text-sm text-gray-600">Nodes (Contacts)</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="text-2xl font-bold text-gray-900">
                {graphData.edges.length}
              </div>
              <div className="text-sm text-gray-600">Edges (Connections)</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="text-2xl font-bold text-gray-900">
                {graphData.edges.length > 0 
                  ? (graphData.edges.length / graphData.nodes.length).toFixed(1)
                  : 0}
              </div>
              <div className="text-sm text-gray-600">Avg Connections/Node</div>
            </div>
          </div>

          {/* Path Finder */}
          <PathFinder />
        </div>
      )}
    </div>
  );
}
