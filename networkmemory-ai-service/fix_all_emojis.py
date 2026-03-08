"""
Remove all emojis from Python files for Windows compatibility

Run: python fix_all_emojis.py
"""

import os
import re

# Files to fix
FILES_TO_FIX = [
    'audio_pipeline/preprocessing.py',
    'audio_pipeline/transcription.py',
    'audio_pipeline/diarization.py',
    'audio_pipeline/extraction.py',
    'audio_pipeline/pipeline.py',
    'main.py',
    'config.py',
]

# Emoji replacements
EMOJI_REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '🚀': '[*]',
    '🎉': '[OK]',
    '📦': '[PACKAGE]',
    '🔧': '[SERVICES]',
    '⚙️': '[CONFIG]',
    '📥': '[REQUEST]',
    '🎵': '[AUDIO]',
    '👥': '[SPEAKER]',
    '⚠️': '[WARNING]',
    '🧠': '[AI]',
    '💡': '[INFO]',
    '🔑': '[KEY]',
    '📍': '',
    '📚': '',
    '💚': '',
    '👤': '',
    '🏢': '',
    '💼': '',
    '📊': '',
    '🗣️': '',
    '📝': '',
    '⏱️': '[TIME]',
}

def fix_file(filepath):
    """Remove emojis from a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace all emojis
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed: {filepath}")
            return True
        else:
            print(f"[SKIP] No emojis found: {filepath}")
            return False
    except FileNotFoundError:
        print(f"[SKIP] File not found: {filepath}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to fix {filepath}: {e}")
        return False

def main():
    print("="*70)
    print("REMOVING ALL EMOJIS FOR WINDOWS COMPATIBILITY")
    print("="*70)

    fixed_count = 0

    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            fixed_count += 1

    print("\n" + "="*70)
    print(f"[OK] Fixed {fixed_count} files")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart your Python server")
    print("2. Test the API endpoint again")

if __name__ == "__main__":
    main()
