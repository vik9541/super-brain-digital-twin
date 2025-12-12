package com.superbrain.contacts.api

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Minimal GraphQL client using OkHttp with Kotlin coroutines
 */
class GraphQLClient(
    private val baseURL: String,
    timeout: Long = 30
) {
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(timeout, TimeUnit.SECONDS)
        .readTimeout(timeout, TimeUnit.SECONDS)
        .writeTimeout(timeout, TimeUnit.SECONDS)
        .build()
    
    private val graphqlURL = "$baseURL/graphql"
    private val mediaType = "application/json; charset=utf-8".toMediaType()
    
    /**
     * Execute GraphQL query with optional variables
     * @param query GraphQL query string
     * @param variables Optional variables map
     * @return Raw JSON response string
     * @throws NetworkException for network errors
     * @throws IOException for I/O errors
     */
    suspend fun execute(
        query: String,
        variables: Map<String, Any>? = null
    ): String = withContext(Dispatchers.IO) {
        val jsonBody = JSONObject().apply {
            put("query", query)
            variables?.let { put("variables", JSONObject(it)) }
        }
        
        val requestBody = jsonBody.toString().toRequestBody(mediaType)
        
        val request = Request.Builder()
            .url(graphqlURL)
            .post(requestBody)
            .addHeader("Content-Type", "application/json")
            .build()
        
        val response = client.newCall(request).execute()
        
        val responseBody = response.body?.string() 
            ?: throw NetworkException.InvalidResponse("Empty response body")
        
        when (response.code) {
            in 200..299 -> responseBody
            in 400..499 -> throw NetworkException.ClientError(response.code, responseBody)
            in 500..599 -> throw NetworkException.ServerError(response.code)
            else -> throw NetworkException.UnknownError(response.code)
        }
    }
}

/**
 * Network exception types
 */
sealed class NetworkException(message: String) : Exception(message) {
    data class InvalidResponse(val msg: String) : NetworkException("Invalid response: $msg")
    data class ClientError(val statusCode: Int, val data: String) : 
        NetworkException("Client error: HTTP $statusCode")
    data class ServerError(val statusCode: Int) : 
        NetworkException("Server error: HTTP $statusCode")
    data class UnknownError(val statusCode: Int) : 
        NetworkException("Unknown error: HTTP $statusCode")
}
