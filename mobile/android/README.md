# SuperBrain Contacts Android SDK

Kotlin SDK for accessing SuperBrain Contacts GraphQL API.

## Requirements

- Android API 21+ (Android 5.0 Lollipop)
- Kotlin 1.5+
- OkHttp 4.x

## Installation

### Gradle

Add to your `build.gradle`:

```gradle
dependencies {
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'
}
```

### Manual

Copy the `com.superbrain.contacts` package into your project.

## Configuration

```kotlin
import com.superbrain.contacts.api.ContactsApi

// Initialize the API client
val api = ContactsApi(baseURL = "https://your-api-url.com")
```

## Usage Examples

### Fetch Contacts

```kotlin
// Fetch all contacts
lifecycleScope.launch {
    try {
        val contacts = api.fetchContacts(limit = 50)
        
        // Display contacts
        contacts.forEach { contact ->
            Log.d("Contact", "${contact.displayName} - ${contact.email ?: "No email"}")
        }
    } catch (e: Exception) {
        Log.e("API", "Error fetching contacts", e)
    }
}

// Search contacts
lifecycleScope.launch {
    val searchResults = api.fetchContacts(search = "John", limit = 20)
    // Process results...
}
```

### Fetch Top Influencers

```kotlin
lifecycleScope.launch {
    try {
        // Get top 10 influencers with score >= 0.5
        val influencers = api.fetchInfluencers(limit = 10, minScore = 0.5)
        
        // Display influencers with scores
        influencers.forEach { contact ->
            contact.influenceScore?.let { score ->
                Log.d("Influencer", "${contact.displayName}: ${"%.2f".format(score)}")
            }
        }
    } catch (e: Exception) {
        Log.e("API", "Error fetching influencers", e)
    }
}
```

### Find Shortest Path Between Contacts

```kotlin
lifecycleScope.launch {
    try {
        val contactId1 = UUID.fromString("123e4567-e89b-12d3-a456-426614174000")
        val contactId2 = UUID.fromString("987fcdeb-51a2-43f8-9abc-def012345678")
        
        val path = api.fetchShortestPath(id1 = contactId1, id2 = contactId2)
        
        // Display path
        path.forEach { node ->
            Log.d("Path", "→ ${node.contact.displayName} (${node.connectionDescription})")
        }
    } catch (e: Exception) {
        Log.e("API", "Error finding path", e)
    }
}
```

## Error Handling

```kotlin
lifecycleScope.launch {
    try {
        val contacts = api.fetchContacts()
    } catch (e: NetworkException) {
        Log.e("API", "Network error: ${e.message}")
    } catch (e: GraphQLException) {
        Log.e("API", "GraphQL error: ${e.message}")
    } catch (e: IOException) {
        Log.e("API", "I/O error: ${e.message}")
    } catch (e: Exception) {
        Log.e("API", "Unexpected error: ${e.message}")
    }
}
```

## Advanced Configuration

### Custom Timeout

```kotlin
val client = GraphQLClient(baseURL = "https://your-api-url.com", timeout = 60)
val api = ContactsApi(client)
```

### Authentication (if needed)

Extend `GraphQLClient` to add authorization headers:

```kotlin
// In GraphQLClient, modify the request builder:
.addHeader("Authorization", "Bearer $apiKey")
```

## Models

### Contact

```kotlin
data class Contact(
    val id: UUID,
    val firstName: String? = null,
    val lastName: String? = null,
    val email: String? = null,
    val organization: String? = null,
    val influenceScore: Double? = null,
    val communityId: Int? = null
) {
    val fullName: String  // Computed property
    val displayName: String  // Computed property with fallback
}
```

### PathNode

```kotlin
data class PathNode(
    val contact: Contact,
    val distance: Int,
    val connectionType: String? = null
) {
    val id: UUID  // Same as contact.id
    val connectionDescription: String  // Human-readable
}
```

## ProGuard Rules

If using ProGuard, add:

```proguard
-keep class com.superbrain.contacts.models.** { *; }
-keep class com.superbrain.contacts.api.** { *; }
```

## License

MIT

## Support

For issues and questions: https://github.com/vik9541/super-brain-digital-twin/issues
