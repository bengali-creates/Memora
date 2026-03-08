/**
 * Contacts API Service
 * Connects frontend to Node.js backend for contact management
 */

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:3000/api';

export interface Contact {
  id: string;
  name: string;
  role?: string;
  company?: string;
  location?: string;
  phone?: string;
  email?: string;
  linkedinUrl?: string;
  topicsDiscussed?: string[];
  followUps?: string[];
  conversationSummary?: string;
  confidenceScore?: number;
  metAt?: string;
  metDate?: string;
  metLocation?: string;
  relationshipScore?: number;
  lastInteraction?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface UserStats {
  peopleMet: number;
  events: number;
  followUps: number;
}

export const contactsApi = {
  /**
   * Get all contacts for the current user
   */
  async getContacts(token: string): Promise<Contact[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/contacts`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch contacts: ${response.statusText}`);
      }

      const data = await response.json();
      return data.contacts || data || [];
    } catch (error) {
      console.error('[CONTACTS API] Failed to fetch contacts:', error);
      throw error;
    }
  },

  /**
   * Get a single contact by ID
   */
  async getContact(id: string, token: string): Promise<Contact> {
    try {
      const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch contact: ${response.statusText}`);
      }

      const data = await response.json();
      return data.contact || data;
    } catch (error) {
      console.error('[CONTACTS API] Failed to fetch contact:', error);
      throw error;
    }
  },

  /**
   * Update a contact
   */
  async updateContact(id: string, updates: Partial<Contact>, token: string): Promise<Contact> {
    try {
      const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update contact: ${response.statusText}`);
      }

      const data = await response.json();
      return data.contact || data;
    } catch (error) {
      console.error('[CONTACTS API] Failed to update contact:', error);
      throw error;
    }
  },

  /**
   * Delete a contact
   */
  async deleteContact(id: string, token: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/contacts/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete contact: ${response.statusText}`);
      }
    } catch (error) {
      console.error('[CONTACTS API] Failed to delete contact:', error);
      throw error;
    }
  },

  /**
   * Search contacts by query (semantic search)
   */
  async searchContacts(query: string, token: string): Promise<Contact[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/contacts/search?query=${encodeURIComponent(query)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to search contacts: ${response.statusText}`);
      }

      const data = await response.json();
      return data.contacts || data || [];
    } catch (error) {
      console.error('[CONTACTS API] Failed to search contacts:', error);
      throw error;
    }
  },

  /**
   * Get user stats (people met, events, follow-ups)
   */
  async getStats(token: string): Promise<UserStats> {
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        // If stats endpoint doesn't exist, calculate from contacts
        const contacts = await this.getContacts(token);
        return {
          peopleMet: contacts.length,
          events: new Set(contacts.map(c => c.metAt).filter(Boolean)).size,
          followUps: contacts.filter(c => c.followUps && c.followUps.length > 0).length,
        };
      }

      const data = await response.json();

      // Return stats if available, otherwise calculate
      if (data.stats) {
        return data.stats;
      }

      // Fallback: fetch contacts and calculate
      const contacts = await this.getContacts(token);
      return {
        peopleMet: contacts.length,
        events: new Set(contacts.map(c => c.metAt).filter(Boolean)).size,
        followUps: contacts.filter(c => c.followUps && c.followUps.length > 0).length,
      };
    } catch (error) {
      console.error('[CONTACTS API] Failed to fetch stats:', error);
      // Return default stats on error
      return {
        peopleMet: 0,
        events: 0,
        followUps: 0,
      };
    }
  },
};
