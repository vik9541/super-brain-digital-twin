# GitHub Copilot Instructions for Super Brain Digital Twin

## Project Overview
- **Project:** Digital Twin with AI (Super Brain v4.1)
- **Tech Stack:** FastAPI, Python 3.11, Kubernetes, DigitalOcean DOKS
- **Infrastructure:** Prometheus, Grafana, NGINX Ingress, Let's Encrypt
- **Deployment:** GitHub Actions → Docker → Kubernetes
- **Production:** 97v.ru (DOKS cluster)

## Code Quality Standards

### Python Code Quality
- **Style:** PEP 8 + Black formatter
- **Linting:** Flake8, pylint, mypy
- **Testing:** pytest with minimum 80% coverage
- **Type Hints:** All function signatures MUST have type annotations

```python
# ✅ GOOD - Type hints and docstring
async def analyze_code(repository_id: str, max_issues: int) -> List[Issue]:
    """Analyze code and return list of issues found."""
    pass

# ❌ BAD - No type hints
def analyze_code(repository_id, max_issues):
    pass
```

### FastAPI Endpoints
- Use async/await for all I/O operations
- Always validate input with Pydantic models
- Include comprehensive docstrings
- Return appropriate HTTP status codes
- Use dependency injection

### Security Requirements (HIGH PRIORITY)
- **NEVER hardcode secrets** - use environment variables
- Validate all external inputs
- Use HTTPS for API calls
- Apply rate limiting on sensitive endpoints
- Log authentication failures
- Use GitHub Secrets for CI/CD

### Testing Standards
- Minimum 80% code coverage
- 100% coverage for security code
- Test naming: `test_<function>_<scenario>`
- Use pytest fixtures for reusable data
- Mock external API calls
- Test both success and error paths

## When NOT to Use Copilot Suggestions
- Security-critical code (auth, encryption)
- Complex business logic
- When you don't understand the suggestion
- Infrastructure code (review Kubernetes manifests)

## Code Review Behavior
When reviewing PRs, Copilot MUST check for:
1. **Security Issues (CRITICAL)** - SQL injection, hardcoded secrets, XSS
2. **Code Quality (HIGH)** - Type hints, unused imports, complexity
3. **Performance (MEDIUM)** - N+1 queries, inefficient algorithms
4. **Testing (MEDIUM)** - Missing tests, insufficient coverage
5. **Documentation (LOW)** - Missing docstrings, outdated comments

## Team Preferences
- Prefer async/await over blocking I/O
- Use f-strings for formatting
- Use type hints everywhere
- Prefer explicit imports
- Use Pydantic for validation

## Communication
🇷🇺 Respond in Russian for all Copilot responses

**Version:** 1.0 | **Updated:** 2025-12-11