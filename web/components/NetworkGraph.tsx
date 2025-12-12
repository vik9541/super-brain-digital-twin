'use client';

import { useEffect, useRef, useState } from 'react';
import { NetworkGraph as NetworkGraphType } from '@/types';

// Define Cytoscape type to avoid import issues
interface CytoscapeInstance {
  fit: () => void;
  zoom: (level?: number) => number | void;
  center: () => void;
  destroy: () => void;
  on: (event: string, handler: (evt: any) => void) => void;
  elements: () => any;
  $(selector: string): any;
}

interface NetworkGraphProps {
  data: NetworkGraphType;
}

export default function NetworkGraph({ data }: NetworkGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<CytoscapeInstance | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient || !containerRef.current || !data) return;

    // Dynamic import of Cytoscape (client-side only)
    let cy: CytoscapeInstance;

    const initGraph = async () => {
      const Cytoscape = (await import('cytoscape')).default;
      
      // Convert data to Cytoscape format
      const elements = [
        ...data.nodes.map(node => ({
          data: {
            id: node.id,
            label: `${node.firstName || ''} ${node.lastName || ''}`.trim() || 'Unknown',
            influenceScore: node.influenceScore || 0,
            communityId: node.communityId || 0,
          }
        })),
        ...data.edges.map(edge => ({
          data: {
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            weight: edge.weight || 1,
          }
        }))
      ];

      // Community colors
      const communityColors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
      ];

      cy = Cytoscape({
        container: containerRef.current!,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': (ele: any) => {
                const communityId = ele.data('communityId') || 0;
                return communityColors[communityId % communityColors.length];
              },
              'width': (ele: any) => {
                const score = ele.data('influenceScore') || 0;
                return 20 + (score * 40); // Size: 20-60px
              },
              'height': (ele: any) => {
                const score = ele.data('influenceScore') || 0;
                return 20 + (score * 40);
              },
              'label': 'data(label)',
              'color': '#fff',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '10px',
              'font-weight': 'bold',
              'text-outline-color': '#000',
              'text-outline-width': 2,
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#cbd5e1',
              'target-arrow-color': '#cbd5e1',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'opacity': 0.6,
            }
          },
          {
            selector: 'node:selected',
            style: {
              'border-width': 3,
              'border-color': '#fbbf24',
            }
          },
          {
            selector: '.highlighted',
            style: {
              'background-color': '#fbbf24',
              'line-color': '#fbbf24',
              'target-arrow-color': '#fbbf24',
              'transition-property': 'background-color, line-color, target-arrow-color',
              'transition-duration': '0.5s',
              'z-index': 10,
            }
          }
        ],
        layout: {
          name: 'cose',
          idealEdgeLength: 100,
          nodeOverlap: 20,
          refresh: 20,
          fit: true,
          padding: 30,
          randomize: false,
          componentSpacing: 100,
          nodeRepulsion: 400000,
          edgeElasticity: 100,
          nestingFactor: 5,
          gravity: 80,
          numIter: 1000,
          initialTemp: 200,
          coolingFactor: 0.95,
          minTemp: 1.0
        },
        minZoom: 0.1,
        maxZoom: 3,
      });

      // Event handlers
      cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        const nodeId = node.id();
        
        // Highlight node and neighbors
        cy.elements().removeClass('highlighted');
        node.addClass('highlighted');
        node.neighborhood().addClass('highlighted');
        
        setSelectedNode(nodeId);
      });

      cy.on('tap', (evt) => {
        if (evt.target === cy) {
          cy.elements().removeClass('highlighted');
          setSelectedNode(null);
        }
      });

      cyRef.current = cy;
    };

    initGraph();

    return () => {
      cyRef.current?.destroy();
    };
  }, [isClient, data]);

  const handleFitToView = () => {
    cyRef.current?.fit();
  };

  const handleZoomIn = () => {
    const currentZoom = cyRef.current?.zoom() as number || 1;
    cyRef.current?.zoom(currentZoom * 1.2);
  };

  const handleZoomOut = () => {
    const currentZoom = cyRef.current?.zoom() as number || 1;
    cyRef.current?.zoom(currentZoom * 0.8);
  };

  if (!isClient) {
    return (
      <div className="w-full h-[600px] bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-gray-500">Loading graph...</div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div ref={containerRef} className="w-full h-[600px] bg-gray-50 rounded-lg border border-gray-300" />
      
      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={handleFitToView}
          className="px-3 py-2 bg-white border border-gray-300 rounded shadow hover:bg-gray-50 text-sm font-medium"
        >
          Fit to View
        </button>
        <button
          onClick={handleZoomIn}
          className="px-3 py-2 bg-white border border-gray-300 rounded shadow hover:bg-gray-50 text-sm font-medium"
        >
          Zoom In
        </button>
        <button
          onClick={handleZoomOut}
          className="px-3 py-2 bg-white border border-gray-300 rounded shadow hover:bg-gray-50 text-sm font-medium"
        >
          Zoom Out
        </button>
      </div>

      {/* Legend */}
      <div className="absolute top-4 left-4 bg-white border border-gray-300 rounded shadow p-3">
        <h4 className="font-semibold text-sm mb-2">Legend</h4>
        <div className="space-y-1 text-xs">
          <div>• Node size = Influence score</div>
          <div>• Node color = Community</div>
          <div>• Click node = Highlight network</div>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 bg-white border border-gray-300 rounded shadow p-3">
          <h4 className="font-semibold text-sm mb-1">Selected Node</h4>
          <div className="text-xs text-gray-600">ID: {selectedNode}</div>
        </div>
      )}
    </div>
  );
}
