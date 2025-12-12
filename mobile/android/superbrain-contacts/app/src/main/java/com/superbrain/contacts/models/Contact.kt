package com.superbrain.contacts.models

import java.util.UUID

/**
 * Contact model matching GraphQL schema
 */
data class Contact(
    val id: UUID,
    val firstName: String? = null,
    val lastName: String? = null,
    val email: String? = null,
    val organization: String? = null,
    val influenceScore: Double? = null,
    val communityId: Int? = null
) {
    /**
     * Full name computed property
     */
    val fullName: String
        get() {
            val parts = listOfNotNull(firstName, lastName)
            return if (parts.isEmpty()) "Unknown" else parts.joinToString(" ")
        }
    
    /**
     * Display name with fallback to email
     */
    val displayName: String
        get() = when {
            fullName.isNotEmpty() && fullName != "Unknown" -> fullName
            email != null -> email
            else -> "Unknown Contact"
        }
}
