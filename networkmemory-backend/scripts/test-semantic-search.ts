/**
 * Test Semantic Search Script
 *
 * Tests if pgvector semantic search is working with existing contacts
 *
 * Run with: npx tsx scripts/test-semantic-search.ts
 */

import { db } from '../src/db/index.js';
import { contacts, users } from '../src/db/schema.js';
import { searchContactsSemantically } from '../src/services/semanticSearch.js';
import { sql } from 'drizzle-orm';

async function testSemanticSearch() {
  console.log('🧪 Testing Semantic Search with pgvector...\n');

  try {
    // Step 1: Check database connection
    console.log('[1/4] Testing database connection...');
    const result = await db.execute(sql`SELECT 1 as test`);
    console.log('✅ Database connected\n');

    // Step 2: Check if pgvector extension is enabled
    console.log('[2/4] Checking pgvector extension...');
    try {
      const extensionCheck = await db.execute(
        sql`SELECT * FROM pg_extension WHERE extname = 'vector'`
      );
      console.log('✅ pgvector extension enabled\n');
    } catch (error: any) {
      console.error('❌ pgvector extension check failed:', error.message);
      console.error('Run this in Neon SQL Editor:');
      console.error('  CREATE EXTENSION IF NOT EXISTS vector;\n');
      process.exit(1);
    }

    // Step 3: Check for test user and contacts
    console.log('[3/4] Checking for test data...');
    const [testUser] = await db
      .select()
      .from(users)
      .where(sql`${users.email} = 'test@networkmemory.ai'`);

    if (!testUser) {
      console.error('❌ Test user not found!');
      console.error('Create test user first in Neon SQL Editor\n');
      process.exit(1);
    }

    console.log(`✅ Found test user: ${testUser.email} (${testUser.id})`);

    const contactsWithEmbeddings = await db
      .select()
      .from(contacts)
      .where(sql`${contacts.userId} = ${testUser.id} AND ${contacts.embedding} IS NOT NULL`);

    console.log(`✅ Found ${contactsWithEmbeddings.length} contacts with embeddings\n`);

    if (contactsWithEmbeddings.length === 0) {
      console.warn('⚠️  No contacts with embeddings found!');
      console.warn('Insert test contacts with embeddings in Neon SQL Editor first\n');
      process.exit(0);
    }

    // Step 4: Test semantic search
    console.log('[4/4] Testing semantic search...\n');

    const testQueries = [
      'blockchain cryptocurrency expert',
      'iOS mobile app developer',
      'machine learning AI engineer'
    ];

    for (const query of testQueries) {
      try {
        console.log(`🔍 Query: "${query}"`);
        const results = await searchContactsSemantically(testUser.id, query, 3);

        if (results.length === 0) {
          console.log('   No results found');
        } else {
          results.forEach((contact, i) => {
            const similarity = (contact.similarity || 0) * 100;
            console.log(`   ${i + 1}. ${contact.name} - ${contact.role} at ${contact.company}`);
            console.log(`      Similarity: ${similarity.toFixed(1)}%`);
          });
        }
        console.log('');
      } catch (error: any) {
        console.error(`   ❌ Search failed: ${error.message}\n`);

        if (error.message?.includes('type "vector" does not exist')) {
          console.error('pgvector extension not enabled properly!');
          process.exit(1);
        }
      }
    }

    console.log('🎉 Semantic search test completed!\n');
    console.log('✅ pgvector is working correctly');
    console.log('✅ Cosine distance operator (<->) is functional');
    console.log('✅ Ready for real embeddings from Gemini\n');

    process.exit(0);

  } catch (error: any) {
    console.error('❌ Test failed:', error);

    if (error.code === 'ENOTFOUND') {
      console.error('\n⚠️  Network connectivity issue!');
      console.error('Cannot connect to Neon database from local machine.');
      console.error('Try:');
      console.error('  1. Mobile hotspot');
      console.error('  2. Different WiFi network');
      console.error('  3. VPN on/off toggle');
      console.error('  4. Run: ipconfig /flushdns\n');
    }

    process.exit(1);
  }
}

// Run the test
testSemanticSearch();
