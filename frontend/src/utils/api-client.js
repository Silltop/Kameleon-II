/**
 * API client wrapper for Option B authentication
 * Injects custom JWT token into all API requests
 */

import { getAPIToken, refreshAPIToken, clearAPIToken } from '../init/token-exchange'

/**
 * Configuration for API requests
 */
const API_CONFIG = {
  defaultTimeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000
}

/**
 * Makes an authenticated API request with custom JWT
 * 
 * @param {string} endpoint - API endpoint (e.g., '/api/uptime')
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise<object>} - { data, status, headers }
 * @throws {Error} - If request fails after retries
 */
export async function apiCall(endpoint, options = {}) {
  const token = getAPIToken()

  if (!token) {
    console.warn('No API token available. User may need to re-authenticate.')
    // Try to refresh
    const refreshed = await refreshAPIToken()
    if (!refreshed) {
      clearAPIToken()
      throw new Error('Authentication required. Please log in.')
    }
    // Retry with new token
    return apiCall(endpoint, options)
  }

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  }

  let lastError
  
  // Retry logic with exponential backoff
  for (let attempt = 0; attempt < API_CONFIG.retryAttempts; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.defaultTimeout)

      try {
        const response = await fetch(endpoint, {
          ...config,
          signal: controller.signal
        })

        clearTimeout(timeoutId)

        // Handle 401 Unauthorized - token may be invalid
        if (response.status === 401) {
          console.warn('Received 401 Unauthorized. Attempting token refresh...')
          const refreshed = await refreshAPIToken()
          if (refreshed && attempt < API_CONFIG.retryAttempts - 1) {
            // Retry with new token
            return apiCall(endpoint, options)
          }
          clearAPIToken()
          throw new Error('Authentication token is invalid or expired')
        }

        // Handle 403 Forbidden
        if (response.status === 403) {
          throw new Error('Access denied to this resource')
        }

        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type')
        let data = null
        
        if (contentType && contentType.includes('application/json')) {
          data = await response.json()
        } else if (response.ok) {
          data = await response.text()
        }

        // Throw error for non-2xx status codes
        if (!response.ok) {
          const errorMessage = data?.error || `HTTP ${response.status}`
          throw new Error(`API Error: ${errorMessage}`)
        }

        return { data, status: response.status, headers: response.headers }
      } catch (error) {
        clearTimeout(timeoutId)
        throw error
      }
    } catch (error) {
      lastError = error

      // Don't retry on authentication errors
      if (error.message.includes('Authentication')) {
        throw error
      }

      // Log retry attempt
      if (attempt < API_CONFIG.retryAttempts - 1) {
        const delay = API_CONFIG.retryDelay * Math.pow(2, attempt)
        console.warn(`API request failed (attempt ${attempt + 1}/${API_CONFIG.retryAttempts}). Retrying in ${delay}ms...`, error.message)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  throw new Error(`API request failed after ${API_CONFIG.retryAttempts} attempts: ${lastError?.message}`)
}

/**
 * GET request
 * @param {string} endpoint - API endpoint
 * @param {object} options - Additional fetch options
 */
export async function apiGet(endpoint, options = {}) {
  return apiCall(endpoint, {
    ...options,
    method: 'GET'
  })
}

/**
 * POST request
 * @param {string} endpoint - API endpoint
 * @param {object} body - Request body
 * @param {object} options - Additional fetch options
 */
export async function apiPost(endpoint, body, options = {}) {
  return apiCall(endpoint, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body)
  })
}

/**
 * PUT request
 * @param {string} endpoint - API endpoint
 * @param {object} body - Request body
 * @param {object} options - Additional fetch options
 */
export async function apiPut(endpoint, body, options = {}) {
  return apiCall(endpoint, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body)
  })
}

/**
 * DELETE request
 * @param {string} endpoint - API endpoint
 * @param {object} options - Additional fetch options
 */
export async function apiDelete(endpoint, options = {}) {
  return apiCall(endpoint, {
    ...options,
    method: 'DELETE'
  })
}

/**
 * PATCH request
 * @param {string} endpoint - API endpoint
 * @param {object} body - Request body
 * @param {object} options - Additional fetch options
 */
export async function apiPatch(endpoint, body, options = {}) {
  return apiCall(endpoint, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(body)
  })
}
