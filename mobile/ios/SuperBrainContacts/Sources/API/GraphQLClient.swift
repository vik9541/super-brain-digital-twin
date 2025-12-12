import Foundation

/// Minimal GraphQL client using URLSession for iOS 15+
@available(iOS 15.0, *)
public class GraphQLClient {
    private let baseURL: URL
    private let session: URLSession
    private let timeout: TimeInterval
    
    public init(baseURL: String, timeout: TimeInterval = 30) {
        guard let url = URL(string: baseURL) else {
            fatalError("Invalid base URL: \(baseURL)")
        }
        self.baseURL = url.appendingPathComponent("graphql")
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = timeout
        config.timeoutIntervalForResource = timeout
        self.session = URLSession(configuration: config)
        self.timeout = timeout
    }
    
    /// Execute GraphQL query with optional variables
    /// - Parameters:
    ///   - query: GraphQL query string
    ///   - variables: Optional variables dictionary
    /// - Returns: Raw JSON Data
    /// - Throws: NetworkError or DecodingError
    public func execute(query: String, variables: [String: Any]? = nil) async throws -> Data {
        var request = URLRequest(url: baseURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        var body: [String: Any] = ["query": query]
        if let variables = variables {
            body["variables"] = variables
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            return data
        case 400...499:
            throw NetworkError.clientError(statusCode: httpResponse.statusCode, data: data)
        case 500...599:
            throw NetworkError.serverError(statusCode: httpResponse.statusCode)
        default:
            throw NetworkError.unknown(statusCode: httpResponse.statusCode)
        }
    }
}

// MARK: - Error Types

public enum NetworkError: Error, LocalizedError {
    case invalidResponse
    case clientError(statusCode: Int, data: Data)
    case serverError(statusCode: Int)
    case unknown(statusCode: Int)
    
    public var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid server response"
        case .clientError(let code, _):
            return "Client error: HTTP \(code)"
        case .serverError(let code):
            return "Server error: HTTP \(code)"
        case .unknown(let code):
            return "Unknown error: HTTP \(code)"
        }
    }
}
