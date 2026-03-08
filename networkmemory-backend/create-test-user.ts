/**
 * Create a test user for testing the backend
 * Run with: npx tsx create-test-user.ts
 */

import { db } from './src/db/index.js';
import { users } from './src/db/schema.js';
import * as dotenv from 'dotenv';

dotenv.config();

async function createTestUser() {
  try {
    console.log('Creating test user...');

    const [user] = await db.insert(users).values({
      email: 'test@networkmemory.ai',
      name: 'Test User'
    }).returning();

    console.log('Test user created successfully!');
    console.log('User ID:', user.id);
    console.log('Email:', user.email);
    console.log('Name:', user.name);
    console.log('\nUse this ID for testing:', user.id);

    process.exit(0);
  } catch (error: any) {
    if (error.message.includes('unique constraint')) {
      console.log('Test user already exists');

      // Get existing user
      const sql = (await import('./src/db/index.js')).default;

      process.exit(0);
    } else {
      console.error('Error creating test user:', error);
      process.exit(1);
    }
  }
}

createTestUser();
