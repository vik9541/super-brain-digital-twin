import Foundation

/// High-level API wrapper for Contacts GraphQL operations
@available(iOS 15.0, *)
public class ContactsAPI {
    private let client: GraphQLClient
    
    public init(client: GraphQLClient) {
        self.client = client
    }
    
    public convenience init(baseURL: String) {
        let client = GraphQLClient(baseURL: baseURL)
        self.init(client: client)
    }
    
    /// Fetch contacts with optional search and limit
    /// - Parameters:
    ///   - search: Optional search string
    ///   - limit: Maximum number of results (default: 50)
    /// - Returns: Array of Contact objects
    public func fetchContacts(search: String? = nil, limit: Int = 50) async throws -> [Contact] {
        let query = """
        query GetContacts($search: String, $limit: Int!) {
          contacts(search: $search, limit: $limit) {
            id
            firstName
            lastName
            email
            organization
            influenceScore
            communityId
          }
        }
        """
        
        var variables: [String: Any] = ["limit": limit]
        if let search = search {
            variables["search"] = search
        }
        
        let data = try await client.execute(query: query, variables: variables)
        let response = try JSONDecoder().decode(ContactsResponse.self, from: data)
        
        if let errors = response.errors {
            throw APIError.graphQLErrors(errors)
        }
        
        return response.data?.contacts ?? []
    }
    
    /// Fetch top influencers by score
    /// - Parameters:
    ///   - limit: Maximum number of results (default: 20)
    ///   - minScore: Minimum influence score (default: 0.0)
    /// - Returns: Array of Contact objects sorted by influence score
    public func fetchInfluencers(limit: Int = 20, minScore: Double = 0.0) async throws -> [Contact] {
        let query = """
        query GetInfluencers($limit: Int!, $minScore: Float!) {
          influencers(limit: $limit, minScore: $minScore) {
            id
            firstName
            lastName
            email
            organization
            influenceScore
            communityId
          }
        }
        """
        
        let variables: [String: Any] = [
            "limit": limit,
            "minScore": minScore
        ]
        
        let data = try await client.execute(query: query, variables: variables)
        let response = try JSONDecoder().decode(InfluencersResponse.self, from: data)
        
        if let errors = response.errors {
            throw APIError.graphQLErrors(errors)
        }
        
        return response.data?.influencers ?? []
    }
    
    /// Find shortest path between two contacts
    /// - Parameters:
    ///   - id1: First contact UUID
    ///   - id2: Second contact UUID
    /// - Returns: Array of PathNode objects representing the shortest path
    public func fetchShortestPath(id1: UUID, id2: UUID) async throws -> [PathNode] {
        let query = """
        query GetShortestPath($id1: UUID!, $id2: UUID!) {
          shortestPath(id1: $id1, id2: $id2) {
            contact {
              id
              firstName
              lastName
              email
              organization
              influenceScore
              communityId
            }
            distance
            connectionType
          }
        }
        """
        
        let variables: [String: Any] = [
            "id1": id1.uuidString,
            "id2": id2.uuidString
        ]
        
        let data = try await client.execute(query: query, variables: variables)
        let response = try JSONDecoder().decode(PathResponse.self, from: data)
        
        if let errors = response.errors {
            throw APIError.graphQLErrors(errors)
        }
        
        return response.data?.shortestPath ?? []
    }
}

// MARK: - Response Types

private struct ContactsResponse: Decodable {
    let data: ContactsData?
    let errors: [GraphQLError]?
}

private struct ContactsData: Decodable {
    let contacts: [Contact]
}

private struct InfluencersResponse: Decodable {
    let data: InfluencersData?
    let errors: [GraphQLError]?
}

private struct InfluencersData: Decodable {
    let influencers: [Contact]
}

private struct PathResponse: Decodable {
    let data: PathData?
    let errors: [GraphQLError]?
}

private struct PathData: Decodable {
    let shortestPath: [PathNode]
}

private struct GraphQLError: Decodable {
    let message: String
    let extensions: [String: String]?
}

// MARK: - Error Types

public enum APIError: Error, LocalizedError {
    case graphQLErrors([GraphQLError])
    
    public var errorDescription: String? {
        switch self {
        case .graphQLErrors(let errors):
            return "GraphQL errors: \(errors.map { $0.message }.joined(separator: ", "))"
        }
    }
}
