import { gql } from 'graphql-request';

// ==================== CONTACTS QUERIES ====================

export const GET_CONTACTS = gql`
  query GetContacts($search: String, $limit: Int, $offset: Int) {
    contacts(search: $search, limit: $limit, offset: $offset) {
      id
      firstName
      lastName
      email
      organization
      influenceScore
      communityId
      tags
      createdAt
      updatedAt
    }
  }
`;

export const GET_CONTACT_BY_ID = gql`
  query GetContactById($id: UUID!) {
    contact(id: $id) {
      id
      firstName
      lastName
      email
      organization
      influenceScore
      communityId
      tags
      connections {
        id
        firstName
        lastName
        connectionType
      }
      createdAt
      updatedAt
    }
  }
`;

// ==================== INFLUENCERS QUERIES ====================

export const GET_INFLUENCERS = gql`
  query GetInfluencers($limit: Int, $minScore: Float) {
    influencers(limit: $limit, minScore: $minScore) {
      id
      firstName
      lastName
      email
      organization
      influenceScore
      communityId
      connectionsCount
      tags
    }
  }
`;

// ==================== COMMUNITIES QUERIES ====================

export const GET_COMMUNITIES = gql`
  query GetCommunities($minSize: Int) {
    communities(minSize: $minSize) {
      id
      name
      size
      avgInfluenceScore
      topMembers {
        id
        firstName
        lastName
        influenceScore
      }
    }
  }
`;

export const GET_COMMUNITY_BY_ID = gql`
  query GetCommunityById($id: Int!) {
    community(id: $id) {
      id
      name
      size
      avgInfluenceScore
      members {
        id
        firstName
        lastName
        email
        organization
        influenceScore
      }
    }
  }
`;

// ==================== NETWORK ANALYSIS QUERIES ====================

export const GET_SHORTEST_PATH = gql`
  query GetShortestPath($id1: UUID!, $id2: UUID!) {
    shortestPath(id1: $id1, id2: $id2) {
      contact {
        id
        firstName
        lastName
        email
        influenceScore
      }
      distance
      connectionType
    }
  }
`;

export const GET_NETWORK_STATS = gql`
  query GetNetworkStats {
    networkStats {
      totalContacts
      totalConnections
      avgInfluenceScore
      topInfluencer {
        id
        firstName
        lastName
        influenceScore
      }
      communitiesCount
      lastSyncTime
    }
  }
`;

export const GET_NETWORK_GRAPH = gql`
  query GetNetworkGraph($limit: Int) {
    networkGraph(limit: $limit) {
      nodes {
        id
        firstName
        lastName
        influenceScore
        communityId
      }
      edges {
        source
        target
        weight
        connectionType
      }
    }
  }
`;

// ==================== DUPLICATES QUERIES ====================

export const GET_DUPLICATE_CANDIDATES = gql`
  query GetDuplicateCandidates($limit: Int, $minSimilarity: Float) {
    duplicateCandidates(limit: $limit, minSimilarity: $minSimilarity) {
      contact1 {
        id
        firstName
        lastName
        email
        organization
      }
      contact2 {
        id
        firstName
        lastName
        email
        organization
      }
      similarity
      reasons
    }
  }
`;

// ==================== MUTATIONS ====================

export const MERGE_CONTACTS = gql`
  mutation MergeContacts($primaryId: UUID!, $duplicateId: UUID!) {
    mergeContacts(primaryId: $primaryId, duplicateId: $duplicateId) {
      success
      mergedContact {
        id
        firstName
        lastName
        email
      }
      message
    }
  }
`;

export const UPDATE_CONTACT = gql`
  mutation UpdateContact($id: UUID!, $data: ContactInput!) {
    updateContact(id: $id, data: $data) {
      id
      firstName
      lastName
      email
      organization
      tags
    }
  }
`;

// ==================== PHASE 6: ML-POWERED QUERIES ====================

export const GET_SIMILAR_CONTACTS = gql`
  query GetSimilarContacts($contactId: UUID!, $limit: Int) {
    similarContacts(contactId: $contactId, limit: $limit) {
      contactId
      firstName
      lastName
      organization
      similarityScore
      commonTags
    }
  }
`;

export const GET_RECOMMENDED_CONTACTS = gql`
  query GetRecommendedContacts($userId: UUID!, $limit: Int, $minScore: Float) {
    recommendedContacts(userId: $userId, limit: $limit, minScore: $minScore) {
      contactId
      firstName
      lastName
      organization
      influenceScore
      totalScore
      components {
        mutualFriends
        semanticSimilarity
        influenceScore
        sameOrganization
      }
      reason
    }
  }
`;

export const GET_CHURN_RISK = gql`
  query GetChurnRisk($contactId: UUID!) {
    churnRisk(contactId: $contactId) {
      contactId
      churnProbability
      riskLevel
      features {
        daysSinceUpdateNorm
        interactionFrequencyNorm
        inverseInfluence
        tagCountNorm
        communitySizeNorm
      }
      interventions
      predictedAt
      expiresAt
    }
  }
`;

export const GET_CONTACT_SENTIMENT = gql`
  query GetContactSentiment($contactId: UUID!) {
    contactSentiment(contactId: $contactId) {
      contactId
      overallSentiment
      sentimentLabel
      components {
        tagsSentiment
        notesSentiment
        interactionsSentiment
      }
      analyzedAt
      expiresAt
    }
  }
`;

export const GET_CONTACT_CLUSTERS = gql`
  query GetContactClusters {
    contactClusters {
      clusterId
      clusterSize
      clusterTopics
      sampleContacts {
        id
        firstName
        lastName
        organization
        influenceScore
      }
    }
  }
`;
