import Foundation

/// Path node representing a step in the shortest path between contacts
public struct PathNode: Codable, Identifiable, Equatable {
    public let contact: Contact
    public let distance: Int
    public let connectionType: String?
    
    public var id: UUID {
        contact.id
    }
    
    public init(
        contact: Contact,
        distance: Int,
        connectionType: String? = nil
    ) {
        self.contact = contact
        self.distance = distance
        self.connectionType = connectionType
    }
    
    /// Human-readable connection description
    public var connectionDescription: String {
        if let type = connectionType {
            return "\(type) (distance: \(distance))"
        }
        return "Distance: \(distance)"
    }
}
