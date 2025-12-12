# SuperBrain Contacts iOS SDK

Swift SDK for accessing SuperBrain Contacts GraphQL API.

## Requirements

- iOS 15.0+
- Swift 5.5+
- Xcode 13.0+

## Installation

### Swift Package Manager

Add the following to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/vik9541/super-brain-digital-twin.git", from: "1.0.0")
]
```

### Manual

Copy the `SuperBrainContacts` folder into your project.

## Configuration

```swift
import SuperBrainContacts

// Initialize the API client
let api = ContactsAPI(baseURL: "https://your-api-url.com")
```

## Usage Examples

### Fetch Contacts

```swift
// Fetch all contacts
let contacts = try await api.fetchContacts(limit: 50)

// Search contacts
let searchResults = try await api.fetchContacts(search: "John", limit: 20)

// Display contacts
for contact in contacts {
    print("\(contact.displayName) - \(contact.email ?? "No email")")
}
```

### Fetch Top Influencers

```swift
// Get top 10 influencers with score >= 0.5
let influencers = try await api.fetchInfluencers(limit: 10, minScore: 0.5)

// Display influencers with scores
for contact in influencers {
    if let score = contact.influenceScore {
        print("\(contact.displayName): \(String(format: "%.2f", score))")
    }
}
```

### Find Shortest Path Between Contacts

```swift
let contactId1 = UUID(uuidString: "123e4567-e89b-12d3-a456-426614174000")!
let contactId2 = UUID(uuidString: "987fcdeb-51a2-43f8-9abc-def012345678")!

let path = try await api.fetchShortestPath(id1: contactId1, id2: contactId2)

// Display path
for node in path {
    print("→ \(node.contact.displayName) (\(node.connectionDescription))")
}
```

## Error Handling

```swift
do {
    let contacts = try await api.fetchContacts()
} catch let error as NetworkError {
    print("Network error: \(error.localizedDescription)")
} catch let error as APIError {
    print("API error: \(error.localizedDescription)")
} catch {
    print("Unexpected error: \(error)")
}
```

## Advanced Configuration

### Custom Timeout

```swift
let client = GraphQLClient(baseURL: "https://your-api-url.com", timeout: 60)
let api = ContactsAPI(client: client)
```

### Authentication (if needed)

Extend `GraphQLClient` to add authorization headers:

```swift
// Add to your GraphQLClient subclass
request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
```

## Models

### Contact

```swift
public struct Contact {
    public let id: UUID
    public let firstName: String?
    public let lastName: String?
    public let email: String?
    public let organization: String?
    public let influenceScore: Double?
    public let communityId: Int?
    
    public var fullName: String  // Computed property
    public var displayName: String  // Computed property with fallback
}
```

### PathNode

```swift
public struct PathNode {
    public let contact: Contact
    public let distance: Int
    public let connectionType: String?
    
    public var connectionDescription: String  // Human-readable
}
```

## License

MIT

## Support

For issues and questions: https://github.com/vik9541/super-brain-digital-twin/issues
