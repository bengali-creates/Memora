/**
 * Auth0 Configuration
 *
 * Get these credentials from:
 * Auth0 Dashboard → Applications → NetworkMemory Mobile App → Settings
 */

export const auth0Config = {
  // Your Auth0 domain (e.g., "your-app.auth0.com")
  domain: process.env.EXPO_PUBLIC_AUTH0_DOMAIN || "dev-example.auth0.com",

  // Your Auth0 Client ID
  clientId: process.env.EXPO_PUBLIC_AUTH0_CLIENT_ID || "your-client-id-here",

  // Your API audience
  audience: process.env.EXPO_PUBLIC_AUTH0_AUDIENCE || "https://networkmemory-api",
};

/**
 * Backend API Configuration
 */
export const apiConfig = {
  baseUrl: process.env.EXPO_PUBLIC_API_URL || "http://localhost:3000/api",
};
