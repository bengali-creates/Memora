/**
 * Auth Context with Auth0
 *
 * Integrates Auth0 authentication while keeping the same interface
 * so existing UI components work without changes.
 */

import * as SecureStore from "expo-secure-store";
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import Auth0 from "react-native-auth0";
import { AuthUser, AuthContextType } from "@/types";
import { auth0Config, apiConfig } from "@/config/auth0";

const AUTH_KEY = "memora_auth_user";
const TOKEN_KEY = "memora_auth_token";

// Initialize Auth0
const auth0 = new Auth0({
  domain: auth0Config.domain,
  clientId: auth0Config.clientId,
});

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  signIn: async () => ({ success: false }),
  signUp: async () => ({ success: false }),
  signOut: async () => {},
  getToken: async () => null,
});

export function AuthProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load stored auth on mount
  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const [storedUser, storedToken] = await Promise.all([
        SecureStore.getItemAsync(AUTH_KEY),
        SecureStore.getItemAsync(TOKEN_KEY),
      ]);

      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error("Failed to load stored auth:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const signUp = useCallback(async (name: string, email: string, password: string) => {
    if (!name.trim() || !email.trim() || !password.trim()) {
      return { success: false, error: "All fields are required" };
    }

    try {
      // Create Auth0 account
      await auth0.auth.createUser({
        email: email.trim().toLowerCase(),
        password,
        connection: "Username-Password-Authentication",
        username: name.trim(),
        metadata: { name: name.trim() },
      });

      // Auto sign-in after signup
      return await signIn(email, password);
    } catch (error: any) {
      console.error("Sign up error:", error);
      return {
        success: false,
        error: error.message || "Sign up failed. Please try again.",
      };
    }
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    if (!email.trim() || !password.trim()) {
      return { success: false, error: "All fields are required" };
    }

    try {
      // Authenticate with Auth0
      const credentials = await auth0.auth.passwordRealm({
        username: email.trim().toLowerCase(),
        password,
        realm: "Username-Password-Authentication",
        scope: "openid profile email offline_access",
        audience: auth0Config.audience,
      });

      const { accessToken, idToken } = credentials;

      // Get user info
      const userInfo = await auth0.auth.userInfo({ token: accessToken });

      const authUser: AuthUser = {
        name: userInfo.name || userInfo.email?.split("@")[0] || "User",
        email: userInfo.email || email.trim().toLowerCase(),
      };

      // Store credentials
      await Promise.all([
        SecureStore.setItemAsync(AUTH_KEY, JSON.stringify(authUser)),
        SecureStore.setItemAsync(TOKEN_KEY, accessToken),
      ]);

      setUser(authUser);

      // Create user in backend if first time
      try {
        await fetch(`${apiConfig.baseUrl}/users`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: authUser.email,
            name: authUser.name,
          }),
        });
      } catch (backendError) {
        // User might already exist, that's ok
        console.log("Backend user creation (may already exist):", backendError);
      }

      return { success: true };
    } catch (error: any) {
      console.error("Sign in error:", error);
      return {
        success: false,
        error: error.message || "Sign in failed. Please check your credentials.",
      };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      await auth0.webAuth.clearSession();
      await Promise.all([
        SecureStore.deleteItemAsync(AUTH_KEY),
        SecureStore.deleteItemAsync(TOKEN_KEY),
      ]);
      setUser(null);
    } catch (error) {
      console.error("Sign out error:", error);
    }
  }, []);

  const getToken = useCallback(async () => {
    try {
      return await SecureStore.getItemAsync(TOKEN_KEY);
    } catch (error) {
      console.error("Get token error:", error);
      return null;
    }
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, signIn, signUp, signOut, getToken }),
    [user, isLoading, signIn, signUp, signOut, getToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

/**
 * Helper hook to get the access token
 * Use this when making API calls to the backend
 */
export function useAccessToken() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    SecureStore.getItemAsync(TOKEN_KEY).then(setToken);
  }, []);

  return token;
}
