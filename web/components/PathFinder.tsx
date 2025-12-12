'use client';

import { useState, useCallback } from 'react';
import { fetchQuery } from '@/lib/graphql-client';
import { GET_SHORTEST_PATH } from '@/lib/queries';
import { PathNode, getContactDisplayName } from '@/types';
import { Search, ArrowRight, Loader2 } from 'lucide-react';

export default function PathFinder() {
  const [contactId1, setContactId1] = useState('');
  const [contactId2, setContactId2] = useState('');
  const [path, setPath] = useState<PathNode[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const findPath = useCallback(async () => {
    if (!contactId1 || !contactId2) {
      setError('Please enter both contact IDs');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const data = await fetchQuery<{ shortestPath: PathNode[] }>(
        GET_SHORTEST_PATH,
        { id1: contactId1, id2: contactId2 }
      );
      
      setPath(data.shortestPath);
      
      if (!data.shortestPath || data.shortestPath.length === 0) {
        setError('No path found between these contacts');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to find path');
      console.error('Path finding error:', err);
    } finally {
      setLoading(false);
    }
  }, [contactId1, contactId2]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Search className="w-5 h-5 text-blue-600" />
        Find Shortest Path
      </h3>

      {/* Input Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contact ID 1
          </label>
          <input
            type="text"
            value={contactId1}
            onChange={(e) => setContactId1(e.target.value)}
            placeholder="Enter UUID..."
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contact ID 2
          </label>
          <input
            type="text"
            value={contactId2}
            onChange={(e) => setContactId2(e.target.value)}
            placeholder="Enter UUID..."
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Find Button */}
      <button
        onClick={findPath}
        disabled={loading || !contactId1 || !contactId2}
        className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Finding path...
          </>
        ) : (
          <>
            <Search className="w-4 h-4" />
            Find Path
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Path Result */}
      {path && path.length > 0 && (
        <div className="mt-6 border-t pt-6">
          <h4 className="font-semibold text-gray-900 mb-3">
            Path Found ({path.length} steps, distance: {path[path.length - 1]?.distance || 0})
          </h4>
          
          <div className="space-y-3">
            {path.map((node, index) => (
              <div key={node.contact.id} className="flex items-center">
                {/* Node */}
                <div className="flex-1 bg-blue-50 border border-blue-200 rounded p-3">
                  <div className="font-medium text-gray-900">
                    {getContactDisplayName(node.contact)}
                  </div>
                  {node.contact.organization && (
                    <div className="text-sm text-gray-600">{node.contact.organization}</div>
                  )}
                  <div className="text-xs text-blue-600 mt-1">
                    Distance: {node.distance}
                    {node.connectionType && ` • Type: ${node.connectionType}`}
                  </div>
                </div>

                {/* Arrow */}
                {index < path.length - 1 && (
                  <ArrowRight className="w-6 h-6 text-gray-400 mx-2 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
