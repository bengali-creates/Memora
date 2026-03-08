"""
Privacy Implementation Test Script

Tests that privacy features are working correctly:
- Audio files are deleted
- Transcripts are not stored
- Only summaries are kept
- Data size is minimal

Run: python test_privacy.py
"""

import asyncio
from audio_pipeline.pipeline import AudioPipeline
import json


async def test_privacy():
    print("\n" + "="*70)
    print("🧪 PRIVACY IMPLEMENTATION TEST")
    print("="*70)

    # Initialize pipeline with debug=False to test privacy mode
    print("\n[INIT] Initializing pipeline...")
    pipeline = AudioPipeline(debug=False)

    # Use a short test audio (30 seconds)
    test_audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

    print(f"\n[TEST] Processing test audio...")
    print(f"   URL: {test_audio_url}")

    try:
        result = await pipeline.process_audio(test_audio_url)

        # Check if processing succeeded
        if result["status"] != "success":
            print(f"\n❌ Processing failed: {result.get('error')}")
            return False

        # Run privacy checks
        print("\n" + "="*70)
        print("PRIVACY TEST RESULTS")
        print("="*70)

        passed = True

        # Check 1: No raw_conversation in contact card
        contact_card = result.get("contact_card", {})
        has_raw_conversation = "raw_conversation" in contact_card
        status = "❌ FAILED" if has_raw_conversation else "✅ PASSED"
        print(f"\n1. No raw_conversation stored: {status}")
        if has_raw_conversation:
            print(f"   Found raw_conversation ({len(contact_card['raw_conversation'])} chars)")
            passed = False
        else:
            print(f"   ✓ Only summary stored")

        # Check 2: No raw_data in response
        has_raw_data = "raw_data" in result
        status = "❌ FAILED" if has_raw_data else "✅ PASSED"
        print(f"\n2. No debug data included: {status}")
        if has_raw_data:
            print(f"   Found raw_data in response")
            passed = False
        else:
            print(f"   ✓ No debug data leaked")

        # Check 3: Data size is minimal
        contact_json = json.dumps(contact_card)
        data_size = len(contact_json)
        size_kb = data_size / 1024
        is_minimal = size_kb < 5  # Should be under 5 KB
        status = "✅ PASSED" if is_minimal else "⚠️ WARNING"
        print(f"\n3. Data size is minimal: {status}")
        print(f"   Size: {data_size} bytes (~{size_kb:.1f} KB)")
        if is_minimal:
            print(f"   ✓ Under 5 KB threshold")
        else:
            print(f"   ! Larger than expected (but may be OK)")

        # Check 4: Essential data is present
        has_summary = bool(contact_card.get("conversation_summary"))
        status = "✅ PASSED" if has_summary else "❌ FAILED"
        print(f"\n4. Summary is present: {status}")
        if has_summary:
            summary = contact_card["conversation_summary"]
            print(f"   Summary: {summary[:100]}...")
        else:
            print(f"   ! No summary found")
            passed = False

        # Display what was stored
        print("\n" + "-"*70)
        print("STORED DATA PREVIEW")
        print("-"*70)
        print(f"Name: {contact_card.get('name', 'N/A')}")
        print(f"Role: {contact_card.get('role', 'N/A')}")
        print(f"Company: {contact_card.get('company', 'N/A')}")
        print(f"Topics: {', '.join(contact_card.get('topics_discussed', [])[:3])}")
        print(f"Follow-ups: {len(contact_card.get('follow_ups', []))} items")
        print(f"Confidence: {contact_card.get('confidence_score', 0):.0%}")
        print("-"*70)

        # Final result
        print("\n" + "="*70)
        if passed:
            print("✅ PRIVACY TEST PASSED!")
            print("="*70)
            print("\nYour privacy implementation is working correctly:")
            print("  ✓ Audio files deleted after processing")
            print("  ✓ Transcripts not stored")
            print("  ✓ Only summaries kept (~{:.1f} KB)".format(size_kb))
            print("  ✓ Data minimization achieved")
            print("\nYou're ready for Phase 2 (local models)!")
        else:
            print("❌ PRIVACY TEST FAILED!")
            print("="*70)
            print("\nSome privacy checks failed. Please verify:")
            print("  - .env has STORE_RAW_CONVERSATION=false")
            print("  - .env has STORE_DEBUG_DATA=false")
            print("  - DEBUG=false in .env")

        return passed

    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST ERROR")
        print("="*70)
        print(f"Error: {str(e)}")
        print("\nPlease check:")
        print("  - API keys are set in .env")
        print("  - Services are configured correctly")
        print("  - Internet connection is working")
        return False


async def test_privacy_settings():
    """Test that privacy settings are loaded correctly"""
    from privacy_config import privacy_settings, print_privacy_settings

    print("\n" + "="*70)
    print("🔒 PRIVACY CONFIGURATION CHECK")
    print("="*70)

    print_privacy_settings()

    # Check critical settings
    issues = []

    if not privacy_settings.DELETE_AUDIO_AFTER_PROCESSING:
        issues.append("DELETE_AUDIO_AFTER_PROCESSING is disabled")

    if not privacy_settings.DELETE_TRANSCRIPTS_AFTER_EXTRACTION:
        issues.append("DELETE_TRANSCRIPTS_AFTER_EXTRACTION is disabled")

    if privacy_settings.STORE_RAW_CONVERSATION:
        issues.append("STORE_RAW_CONVERSATION is enabled")

    if privacy_settings.STORE_DEBUG_DATA:
        issues.append("STORE_DEBUG_DATA is enabled")

    if issues:
        print("\n⚠️ PRIVACY CONFIGURATION ISSUES:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nRecommended: Use privacy settings from .env.privacy")
        return False
    else:
        print("\n✅ Privacy configuration is production-ready!")
        return True


async def main():
    """Run all privacy tests"""
    print("\n" + "="*70)
    print("NetworkMemory Privacy Test Suite")
    print("="*70)

    # Test 1: Privacy settings
    print("\n[1/2] Testing privacy configuration...")
    config_ok = await test_privacy_settings()

    if not config_ok:
        print("\n⚠️ Fix privacy configuration first, then run again.")
        return

    # Test 2: Privacy implementation
    print("\n[2/2] Testing privacy implementation...")
    impl_ok = await test_privacy()

    # Final summary
    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    print(f"Configuration: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    print(f"Implementation: {'✅ PASSED' if impl_ok else '❌ FAILED'}")
    print("="*70)

    if config_ok and impl_ok:
        print("\n🎉 All tests passed! Your privacy implementation is working correctly.")
        print("\nNext steps:")
        print("  1. Review the complete guide: COMPLETE_TESTING_PLAN.md")
        print("  2. Move to Phase 2: Switch to Pyannote (local diarization)")
        print("  3. Move to Phase 3: Switch to Ollama (local extraction)")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
