package com.superbrain.contacts.api

import com.superbrain.contacts.models.Contact
import com.superbrain.contacts.models.PathNode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

/**
 * High-level API wrapper for Contacts GraphQL operations
 */
class ContactsApi(private val client: GraphQLClient) {
    
    constructor(baseURL: String) : this(GraphQLClient(baseURL))
    
    /**
     * Fetch contacts with optional search and limit
     * @param search Optional search string
     * @param limit Maximum number of results (default: 50)
     * @return List of Contact objects
     */
    suspend fun fetchContacts(
        search: String? = null,
        limit: Int = 50
    ): List<Contact> = withContext(Dispatchers.IO) {
        val query = """
            query GetContacts(${'$'}search: String, ${'$'}limit: Int!) {
              contacts(search: ${'$'}search, limit: ${'$'}limit) {
                id
                firstName
                lastName
                email
                organization
                influenceScore
                communityId
              }
            }
        """.trimIndent()
        
        val variables = mutableMapOf<String, Any>("limit" to limit)
        search?.let { variables["search"] = it }
        
        val response = client.execute(query, variables)
        val json = JSONObject(response)
        
        if (json.has("errors")) {
            throw GraphQLException(json.getJSONArray("errors"))
        }
        
        val contactsArray = json.getJSONObject("data").getJSONArray("contacts")
        parseContacts(contactsArray)
    }
    
    /**
     * Fetch top influencers by score
     * @param limit Maximum number of results (default: 20)
     * @param minScore Minimum influence score (default: 0.0)
     * @return List of Contact objects sorted by influence score
     */
    suspend fun fetchInfluencers(
        limit: Int = 20,
        minScore: Double = 0.0
    ): List<Contact> = withContext(Dispatchers.IO) {
        val query = """
            query GetInfluencers(${'$'}limit: Int!, ${'$'}minScore: Float!) {
              influencers(limit: ${'$'}limit, minScore: ${'$'}minScore) {
                id
                firstName
                lastName
                email
                organization
                influenceScore
                communityId
              }
            }
        """.trimIndent()
        
        val variables = mapOf(
            "limit" to limit,
            "minScore" to minScore
        )
        
        val response = client.execute(query, variables)
        val json = JSONObject(response)
        
        if (json.has("errors")) {
            throw GraphQLException(json.getJSONArray("errors"))
        }
        
        val influencersArray = json.getJSONObject("data").getJSONArray("influencers")
        parseContacts(influencersArray)
    }
    
    /**
     * Find shortest path between two contacts
     * @param id1 First contact UUID
     * @param id2 Second contact UUID
     * @return List of PathNode objects representing the shortest path
     */
    suspend fun fetchShortestPath(
        id1: UUID,
        id2: UUID
    ): List<PathNode> = withContext(Dispatchers.IO) {
        val query = """
            query GetShortestPath(${'$'}id1: UUID!, ${'$'}id2: UUID!) {
              shortestPath(id1: ${'$'}id1, id2: ${'$'}id2) {
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
        """.trimIndent()
        
        val variables = mapOf(
            "id1" to id1.toString(),
            "id2" to id2.toString()
        )
        
        val response = client.execute(query, variables)
        val json = JSONObject(response)
        
        if (json.has("errors")) {
            throw GraphQLException(json.getJSONArray("errors"))
        }
        
        val pathArray = json.getJSONObject("data").getJSONArray("shortestPath")
        parsePathNodes(pathArray)
    }
    
    // Helper methods
    
    private fun parseContacts(array: JSONArray): List<Contact> {
        val contacts = mutableListOf<Contact>()
        for (i in 0 until array.length()) {
            val obj = array.getJSONObject(i)
            contacts.add(parseContact(obj))
        }
        return contacts
    }
    
    private fun parseContact(obj: JSONObject): Contact {
        return Contact(
            id = UUID.fromString(obj.getString("id")),
            firstName = obj.optString("firstName").takeIf { it.isNotEmpty() },
            lastName = obj.optString("lastName").takeIf { it.isNotEmpty() },
            email = obj.optString("email").takeIf { it.isNotEmpty() },
            organization = obj.optString("organization").takeIf { it.isNotEmpty() },
            influenceScore = if (obj.has("influenceScore")) obj.getDouble("influenceScore") else null,
            communityId = if (obj.has("communityId")) obj.getInt("communityId") else null
        )
    }
    
    private fun parsePathNodes(array: JSONArray): List<PathNode> {
        val nodes = mutableListOf<PathNode>()
        for (i in 0 until array.length()) {
            val obj = array.getJSONObject(i)
            val contact = parseContact(obj.getJSONObject("contact"))
            nodes.add(
                PathNode(
                    contact = contact,
                    distance = obj.getInt("distance"),
                    connectionType = obj.optString("connectionType").takeIf { it.isNotEmpty() }
                )
            )
        }
        return nodes
    }
}

/**
 * GraphQL exception with error details
 */
class GraphQLException(errors: JSONArray) : Exception() {
    private val errorMessages: List<String> = (0 until errors.length()).map {
        errors.getJSONObject(it).getString("message")
    }
    
    override val message: String
        get() = "GraphQL errors: ${errorMessages.joinToString(", ")}"
}
