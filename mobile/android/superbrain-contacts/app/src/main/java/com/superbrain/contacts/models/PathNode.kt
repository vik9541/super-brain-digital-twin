package com.superbrain.contacts.models

import java.util.UUID

/**
 * Path node representing a step in the shortest path between contacts
 */
data class PathNode(
    val contact: Contact,
    val distance: Int,
    val connectionType: String? = null
) {
    val id: UUID
        get() = contact.id
    
    /**
     * Human-readable connection description
     */
    val connectionDescription: String
        get() = connectionType?.let { "$it (distance: $distance)" } ?: "Distance: $distance"
}
