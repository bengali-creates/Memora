/**
 * Seed Dummy Data Script
 *
 * Creates test user and contacts for testing semantic search
 *
 * Run with: npx tsx scripts/seed-dummy-data.ts
 */

import { db } from '../src/db/index.js';
import { users, contacts } from '../src/db/schema.js';
import { generateEmbedding } from '../src/services/semanticSearch.js';
import { sql } from 'drizzle-orm';

const dummyContacts = [
  {
    name: "Raj Kumar",
    role: "Blockchain Engineer",
    company: "Coinbase",
    location: "Bangalore, India",
    email: "raj.kumar@coinbase.com",
    phone: "+91-9876543210",
    topicsDiscussed: ["blockchain", "cryptocurrency", "DeFi", "smart contracts", "Ethereum"],
    conversationSummary: "Discussed implementing blockchain payment systems and DeFi protocols. Raj is very knowledgeable about Ethereum smart contracts and has experience with Layer 2 solutions.",
    metAt: "DevFest Kolkata 2026",
    metLocation: "Kolkata, India",
    confidenceScore: 0.95
  },
  {
    name: "Sarah Chen",
    role: "iOS Developer",
    company: "Apple",
    location: "Cupertino, USA",
    email: "sarah.chen@apple.com",
    topicsDiscussed: ["iOS development", "SwiftUI", "mobile architecture", "App Store optimization"],
    conversationSummary: "Expert in iOS development with 8 years at Apple. Specializes in SwiftUI and has published multiple apps with 10M+ downloads. Very passionate about mobile UX design.",
    metAt: "TechCrunch Disrupt 2025",
    metLocation: "San Francisco, USA",
    confidenceScore: 0.92
  },
  {
    name: "Mike Johnson",
    role: "ML Engineer",
    company: "Google DeepMind",
    location: "London, UK",
    email: "mike.j@deepmind.com",
    topicsDiscussed: ["machine learning", "neural networks", "computer vision", "TensorFlow", "AI research"],
    conversationSummary: "Works on computer vision models at DeepMind. Has published papers on efficient neural architectures. Very interested in edge AI and on-device ML.",
    metAt: "NeurIPS 2025",
    metLocation: "New Orleans, USA",
    confidenceScore: 0.89
  },
  {
    name: "Priya Sharma",
    role: "Product Manager",
    company: "Stripe",
    location: "Mumbai, India",
    email: "priya@stripe.com",
    topicsDiscussed: ["product management", "fintech", "payment systems", "API design", "developer experience"],
    conversationSummary: "Leading Stripe's India payment infrastructure. Expert in payment gateway design and regulatory compliance. Great network in Indian fintech ecosystem.",
    metAt: "Razorpay FTX 2026",
    metLocation: "Bangalore, India",
    confidenceScore: 0.88
  },
  {
    name: "Alex Martinez",
    role: "DevOps Engineer",
    company: "AWS",
    location: "Seattle, USA",
    email: "alex.m@amazon.com",
    topicsDiscussed: ["DevOps", "Kubernetes", "CI/CD", "cloud infrastructure", "Docker", "microservices"],
    conversationSummary: "Senior DevOps engineer at AWS. Expert in container orchestration and serverless architectures. Has helped 100+ companies migrate to cloud.",
    metAt: "AWS re:Invent 2025",
    metLocation: "Las Vegas, USA",
    confidenceScore: 0.91
  },
  {
    name: "Lisa Wang",
    role: "UX Designer",
    company: "Figma",
    location: "San Francisco, USA",
    email: "lisa@figma.com",
    topicsDiscussed: ["UX design", "design systems", "user research", "prototyping", "accessibility"],
    conversationSummary: "Lead designer at Figma. Specializes in design systems and has worked on products used by millions. Very passionate about accessibility and inclusive design.",
    metAt: "Config 2025",
    metLocation: "San Francisco, USA",
    confidenceScore: 0.87
  },
  {
    name: "Arjun Patel",
    role: "Data Scientist",
    company: "Meta",
    location: "Menlo Park, USA",
    email: "arjun.patel@meta.com",
    topicsDiscussed: ["data science", "recommendation systems", "A/B testing", "analytics", "Python", "SQL"],
    conversationSummary: "Works on recommendation algorithms at Meta. Expert in large-scale data processing and experimentation. Has experience with personalization systems serving billions of users.",
    metAt: "Data Science Summit 2025",
    metLocation: "Austin, USA",
    confidenceScore: 0.90
  },
  {
    name: "Emma Thompson",
    role: "Frontend Engineer",
    company: "Vercel",
    location: "Remote",
    email: "emma@vercel.com",
    topicsDiscussed: ["React", "Next.js", "web performance", "TypeScript", "frontend architecture"],
    conversationSummary: "Frontend engineer at Vercel working on Next.js. Expert in web performance optimization and has contributed to open source. Very active in React community.",
    metAt: "React Conf 2025",
    metLocation: "Amsterdam, Netherlands",
    confidenceScore: 0.93
  }
];

async function seedDummyData() {
  console.log('🌱 Seeding dummy data for NetworkMemory AI...\n');

  try {
    // Create test user
    console.log('[1/3] Creating test user...');
    const [testUser] = await db.insert(users).values({
      email: 'test@networkmemory.ai',
      name: 'Test User'
    }).returning().onConflictDoNothing();

    if (!testUser) {
      console.log('⚠️  Test user already exists, fetching...');
      const [existingUser] = await db.select().from(users).where(sql`${users.email} = 'test@networkmemory.ai'`);
      if (existingUser) {
        console.log(`✅ Using existing user: ${existingUser.email} (${existingUser.id})\n`);
      }
    } else {
      console.log(`✅ Created user: ${testUser.email} (${testUser.id})\n`);
    }

    const userId = testUser?.id || (await db.select().from(users).where(sql`${users.email} = 'test@networkmemory.ai'`))[0].id;

    // Insert contacts with embeddings
    console.log('[2/3] Creating contacts with embeddings...');
    console.log('⏳ This will take ~1 minute (generating embeddings with Gemini)\n');

    for (let i = 0; i < dummyContacts.length; i++) {
      const contact = dummyContacts[i];

      // Generate embedding text
      const embeddingText = [
        `Role: ${contact.role}`,
        `Company: ${contact.company}`,
        `Topics: ${contact.topicsDiscussed.join(', ')}`,
        `Summary: ${contact.conversationSummary}`
      ].join('. ');

      console.log(`  [${i + 1}/${dummyContacts.length}] Generating embedding for ${contact.name}...`);

      // Generate embedding
      const embedding = await generateEmbedding(embeddingText);

      // Insert contact
      await db.insert(contacts).values({
        userId: userId,
        name: contact.name,
        role: contact.role,
        company: contact.company,
        location: contact.location,
        email: contact.email,
        phone: contact.phone,
        topicsDiscussed: contact.topicsDiscussed,
        conversationSummary: contact.conversationSummary,
        metAt: contact.metAt,
        metLocation: contact.metLocation,
        confidenceScore: contact.confidenceScore,
        embedding: embedding  // Vector type handles this automatically
      });

      console.log(`    ✅ ${contact.name} (${contact.role} at ${contact.company})`);
    }

    console.log(`\n✅ Created ${dummyContacts.length} contacts\n`);

    // Test semantic search
    console.log('[3/3] Testing semantic search...\n');

    const { searchContactsSemantically } = await import('../src/services/semanticSearch.js');

    const testQueries = [
      "blockchain expert",
      "iOS mobile developer",
      "machine learning AI",
      "payment systems fintech"
    ];

    for (const query of testQueries) {
      console.log(`🔍 Searching for: "${query}"`);
      const results = await searchContactsSemantically(userId, query, 3);

      results.forEach((r, i) => {
        console.log(`  ${i + 1}. ${r.name} (${r.role} at ${r.company}) - Similarity: ${((r.similarity || 0) * 100).toFixed(1)}%`);
      });
      console.log('');
    }

    console.log('🎉 Dummy data seeded successfully!\n');
    console.log('📝 Test Information:');
    console.log(`   User ID: ${userId}`);
    console.log(`   Email: test@networkmemory.ai`);
    console.log(`   Contacts: ${dummyContacts.length}`);
    console.log('\n🧪 Try these tests:');
    console.log('   1. Chat: "I need blockchain expertise"');
    console.log('   2. Chat: "I want to build an iPhone app"');
    console.log('   3. Chat: "I need help with machine learning"');
    console.log('\n💡 Use this user ID in your requests (dev mode):');
    console.log(`   curl -H "X-User-Id: ${userId}" http://localhost:3000/api/contacts\n`);

    process.exit(0);

  } catch (error: any) {
    console.error('❌ Error seeding data:', error);

    // Check for pgvector error
    if (error.message?.includes('type "vector" does not exist')) {
      console.error('\n⚠️  PGVECTOR NOT ENABLED!');
      console.error('Run this in your Neon DB SQL Editor:');
      console.error('  CREATE EXTENSION IF NOT EXISTS vector;\n');
    }

    process.exit(1);
  }
}

// Run the seed function
seedDummyData();
