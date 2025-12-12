// ==================== CONTACT TYPES ====================

export interface Contact {
  id: string;
  firstName?: string | null;
  lastName?: string | null;
  email?: string | null;
  organization?: string | null;
  influenceScore?: number | null;
  communityId?: number | null;
  tags?: string[] | null;
  connectionsCount?: number;
  connections?: ContactConnection[];
  createdAt?: string;
  updatedAt?: string;
}

export interface ContactConnection {
  id: string;
  firstName?: string | null;
  lastName?: string | null;
  connectionType?: string | null;
}

export interface ContactInput {
  firstName?: string;
  lastName?: string;
  email?: string;
  organization?: string;
  tags?: string[];
}

// ==================== PATH TYPES ====================

export interface PathNode {
  contact: Contact;
  distance: number;
  connectionType?: string | null;
}

// ==================== COMMUNITY TYPES ====================

export interface Community {
  id: number;
  name?: string;
  size: number;
  avgInfluenceScore?: number;
  topMembers?: Contact[];
  members?: Contact[];
}

// ==================== NETWORK TYPES ====================

export interface NetworkStats {
  totalContacts: number;
  totalConnections: number;
  avgInfluenceScore: number;
  topInfluencer?: Contact | null;
  communitiesCount: number;
  lastSyncTime?: string | null;
}

export interface NetworkGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  firstName?: string | null;
  lastName?: string | null;
  influenceScore?: number | null;
  communityId?: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
  connectionType?: string | null;
}

// ==================== DUPLICATE TYPES ====================

export interface DuplicateCandidate {
  contact1: Contact;
  contact2: Contact;
  similarity: number;
  reasons: string[];
}

export interface MergeResult {
  success: boolean;
  mergedContact?: Contact;
  message?: string;
}

// ==================== UTILITY TYPES ====================

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface SearchParams {
  search?: string;
  organization?: string;
  minInfluenceScore?: number;
  communityId?: number;
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Get full name from contact
 */
export function getContactFullName(contact: Contact): string {
  const parts = [contact.firstName, contact.lastName].filter(Boolean);
  return parts.length > 0 ? parts.join(' ') : 'Unknown';
}

/**
 * Get display name with fallback to email
 */
export function getContactDisplayName(contact: Contact): string {
  const fullName = getContactFullName(contact);
  if (fullName !== 'Unknown') return fullName;
  return contact.email || 'Unknown Contact';
}

/**
 * Get influence score as percentage
 */
export function getInfluencePercentage(score?: number | null): number {
  if (!score) return 0;
  return Math.round(score * 100);
}

/**
 * Get color based on influence score
 */
export function getScoreColor(score?: number | null): string {
  if (!score) return 'text-gray-400';
  if (score >= 0.7) return 'text-green-600';
  if (score >= 0.3) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Get color class based on influence score
 */
export function getScoreBgColor(score?: number | null): string {
  if (!score) return 'bg-gray-100';
  if (score >= 0.7) return 'bg-green-100';
  if (score >= 0.3) return 'bg-yellow-100';
  return 'bg-red-100';
}
