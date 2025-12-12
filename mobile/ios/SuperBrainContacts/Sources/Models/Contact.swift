import Foundation

/// Contact model matching GraphQL schema
public struct Contact: Codable, Identifiable, Equatable {
    public let id: UUID
    public let firstName: String?
    public let lastName: String?
    public let email: String?
    public let organization: String?
    public let influenceScore: Double?
    public let communityId: Int?
    
    public init(
        id: UUID,
        firstName: String? = nil,
        lastName: String? = nil,
        email: String? = nil,
        organization: String? = nil,
        influenceScore: Double? = nil,
        communityId: Int? = nil
    ) {
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.organization = organization
        self.influenceScore = influenceScore
        self.communityId = communityId
    }
    
    /// Full name computed property
    public var fullName: String {
        let parts = [firstName, lastName].compactMap { $0 }
        return parts.isEmpty ? "Unknown" : parts.joined(separator: " ")
    }
    
    /// Display name with fallback to email
    public var displayName: String {
        if !fullName.isEmpty && fullName != "Unknown" {
            return fullName
        }
        return email ?? "Unknown Contact"
    }
}
