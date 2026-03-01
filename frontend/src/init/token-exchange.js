/**
 * Token exchange for Option B: Backend-controlled JWT generation
 * 
 * Flow:
 * 1. User logs in via Keycloak (handled by Flask server-side)
 * 2. Frontend calls /auth/exchange to get custom API JWT
 * 3. Frontend stores custom JWT locally for API calls
 * 4. All API calls include custom JWT in Authorization header
 */

/**
 * Exchange Keycloak session for custom API JWT token
 * Must be called after user has authenticated with Keycloak
 * 
 * @returns {Promise<string>} - Custom API JWT token
 * @throws {Error} - If exchange fails or user not authenticated
 */
export async function exchangeTokenForAPI() {
  try {
    const response = await fetch('/auth/exchange', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Token exchange failed: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    
    if (!data.token) {
      throw new Error('No token in exchange response')
    }

    // Store token locally
    localStorage.setItem('api_token', data.token)
    localStorage.setItem('api_token_type', data.token_type || 'Bearer')
    localStorage.setItem('api_token_expires_in', data.expires_in || 86400)
    
    // Calculate and store expiration time
    const expiresAt = new Date(Date.now() + data.expires_in * 1000).getTime()
    localStorage.setItem('api_token_expires_at', expiresAt)
    
    console.log('Token exchange successful. Token will expire at', new Date(expiresAt))
    return data.token
  } catch (error) {
    console.error('Failed to exchange token for API access:', error)
    throw error
  }
}

/**
 * Get the current API JWT token
 * 
 * @returns {string|null} - API token or null if not available
 */
export function getAPIToken() {
  const token = localStorage.getItem('api_token')
  const expiresAt = localStorage.getItem('api_token_expires_at')
  
  // Check if token has expired
  if (token && expiresAt) {
    if (Date.now() > parseInt(expiresAt)) {
      console.warn('API token has expired')
      clearAPIToken()
      return null
    }
  }
  
  return token
}

/**
 * Check if API token exists and is valid
 * 
 * @returns {boolean}
 */
export function hasValidAPIToken() {
  return getAPIToken() !== null
}

/**
 * Clear stored API token (logout)
 */
export function clearAPIToken() {
  localStorage.removeItem('api_token')
  localStorage.removeItem('api_token_type')
  localStorage.removeItem('api_token_expires_in')
  localStorage.removeItem('api_token_expires_at')
}

/**
 * Attempt to refresh token by exchanging again
 * This will fail if Keycloak session has expired
 * 
 * @returns {Promise<boolean>} - true if refresh successful
 */
export async function refreshAPIToken() {
  try {
    await exchangeTokenForAPI()
    return true
  } catch (error) {
    console.error('Failed to refresh API token:', error)
    return false
  }
}
