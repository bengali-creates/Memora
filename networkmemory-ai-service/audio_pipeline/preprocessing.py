"""
Audio Preprocessing Module

Flow: URL -> Download -> Convert -> Noise Filter -> Chunk -> Ready for transcription

Why each step:
1. Download: Get audio from remote storage (Supabase)
2. Convert: Standardize format (WAV, mono, 16kHz)
3. Noise Reduce: Clean up background noise (important for accuracy)
4. Chunk: Split long audio into manageable pieces (90s each)
"""

import os
import io
import tempfile
import numpy as np
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
from pydub.utils import which
from typing import List, Tuple, Dict
import httpx

# ============================================
# FFmpeg Path Fix for Windows
# ============================================
# If ffmpeg is not in PATH, set it manually
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffprobe.exe"

if os.path.exists(FFMPEG_PATH):
    print(f"[INFO] Setting ffmpeg path: {FFMPEG_PATH}")
    # Set AudioSegment paths
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffmpeg = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH

    # CRITICAL: Also set pydub.utils paths (this is what's missing!)
    from pydub import utils
    utils.ffmpeg = FFMPEG_PATH
    utils.ffprobe = FFPROBE_PATH

    # Add to PATH so subprocess can find it
    ffmpeg_bin_dir = os.path.dirname(FFMPEG_PATH)
    if ffmpeg_bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
        print(f"[INFO] Added ffmpeg to PATH: {ffmpeg_bin_dir}")

    print("[OK] FFmpeg configured successfully")
elif not which("ffmpeg"):
    print("[WARNING] ffmpeg not found in PATH and not at default location!")
    print("          Audio conversion may fail. Please install ffmpeg.")
else:
    print("[OK] ffmpeg found in PATH")


class AudioPreprocessor:
    """
    Handles all audio preprocessing tasks

    Key design decisions:
    - Use temp directory for intermediate files
    - Clean up after processing (save disk space)
    - Return both paths and metadata
    """

    def __init__(self, chunk_length_seconds: int = 90):
        """
        Args:
            chunk_length_seconds: Length of each audio chunk (default 90s)
                Why 90s? Balance between:
                - Too short: Loses conversation context
                - Too long: API timeouts, rate limits
                - 90s: ~3-5 conversational turns, safe for APIs
        """
        self.chunk_length_seconds = chunk_length_seconds
        self.temp_dir = tempfile.gettempdir()

        print(f"[OK] AudioPreprocessor initialized")
        print(f"   Chunk length: {chunk_length_seconds}s")
        print(f"   Temp directory: {self.temp_dir}")

    async def download_audio(self, audio_url: str) -> str:
        """
        Download audio file from URL or handle local file

        Args:
            audio_url: HTTP(S) URL to audio file OR local file path

        Returns:
            Path to downloaded file

        Why async:
        - Downloads can take time (large files)
        - Don't block the server while downloading
        - FastAPI is async, so this fits naturally
        """
        # Check if it's a local file first
        if os.path.exists(audio_url):
            print(f"\n[LOCAL] Using local audio file...")
            print(f"   Path: {audio_url}")
            file_size_mb = os.path.getsize(audio_url) / (1024 * 1024)
            print(f"[OK] Local file: {file_size_mb:.2f} MB")
            return audio_url

        print(f"\n[REQUEST] Downloading audio...")
        print(f"   URL: {audio_url}")

        try:
            # Use httpx for async HTTP requests (follow redirects)
            async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                response = await client.get(audio_url)

                if response.status_code != 200:
                    raise Exception(f"Download failed with status {response.status_code}")

                # Extract file extension from URL to preserve it
                # This helps FFmpeg identify the format
                import urllib.parse
                url_path = urllib.parse.urlparse(audio_url).path
                file_ext = os.path.splitext(url_path)[1] or ".tmp"

                # Save to temp file WITH proper extension
                temp_path = os.path.join(self.temp_dir, f"downloaded_audio_raw{file_ext}")
                with open(temp_path, "wb") as f:
                    f.write(response.content)

                file_size_mb = len(response.content) / (1024 * 1024)
                print(f"[OK] Downloaded: {file_size_mb:.2f} MB")
                print(f"   Saved to: {temp_path}")
                print(f"   File exists: {os.path.exists(temp_path)}")

                return temp_path

        except Exception as e:
            print(f"[ERROR] Download failed: {str(e)}")
            raise

    def convert_to_wav(self, audio_path: str, skip_if_wav: bool = False) -> str:
        """
        Convert audio to WAV format with optimal settings

        Settings:
        - Format: WAV (uncompressed, easy to process)
        - Channels: 1 (mono - we don't need stereo for speech)
        - Sample rate: 16kHz (optimal for speech recognition)
            - Lower than 16kHz: Loses speech information
            - Higher than 16kHz: Wastes space, no benefit for speech

        Args:
            audio_path: Path to input audio (any format)
            skip_if_wav: If True, skip conversion for WAV files (OPTIMIZATION)

        Returns:
            Path to WAV file
        """
        # Check if already WAV format (OPTIMIZATION)
        if skip_if_wav and audio_path.lower().endswith('.wav'):
            print(f"\n[OPTIMIZATION] File is already WAV format - checking if conversion needed...")

            try:
                # Load WAV to check if it meets our requirements
                audio = AudioSegment.from_wav(audio_path)

                orig_channels = audio.channels
                orig_rate = audio.frame_rate

                # Check if already in optimal format (mono, 16kHz)
                if audio.channels == 1 and audio.frame_rate == 16000:
                    print(f"   Already optimal: 1ch, 16000Hz")
                    print(f"[OK] Skipping conversion - using original file!")
                    return audio_path

                print(f"   Current: {orig_channels}ch, {orig_rate}Hz - needs conversion")

            except:
                print(f"   Could not verify format - will convert to be safe")

        print(f"\n Converting to WAV format...")
        print(f"   Input file: {audio_path}")
        print(f"   File exists: {os.path.exists(audio_path)}")
        if os.path.exists(audio_path):
            print(f"   File size: {os.path.getsize(audio_path) / (1024*1024):.2f} MB")

        try:
            # Load audio (pydub supports many formats: mp3, m4a, ogg, etc.)
            audio = AudioSegment.from_file(audio_path)

            # Get original info
            orig_channels = audio.channels
            orig_rate = audio.frame_rate
            orig_duration = len(audio) / 1000  # milliseconds to seconds

            print(f"   Original: {orig_channels}ch, {orig_rate}Hz, {orig_duration:.1f}s")

            needs_conversion = False

            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
                print(f"   -> Converted to mono")
                needs_conversion = True

            # Convert to 16kHz
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
                print(f"   -> Resampled to 16kHz")
                needs_conversion = True

            # Only save if conversion was needed
            if needs_conversion or not audio_path.lower().endswith('.wav'):
                # Save as WAV
                output_path = os.path.join(self.temp_dir, "audio_converted.wav")
                audio.export(output_path, format="wav")
                print(f"[OK] Converted: 1ch, 16000Hz, {orig_duration:.1f}s")
                return output_path
            else:
                print(f"[OK] Already in correct format")
                return audio_path

        except Exception as e:
            print(f"[ERROR] Conversion failed: {str(e)}")
            raise

    def apply_noise_reduction(self, audio_path: str, prop_decrease: float = 0.8) -> str:
        """
        Apply noise reduction to clean up background noise

        Why noise reduction:
        - Conference venues are noisy (people talking, music, etc.)
        - Clean audio = better transcription accuracy
        - Especially important for diarization (speaker separation)

        Args:
            audio_path: Path to WAV file
            prop_decrease: How much to reduce noise (0.8 = 80% reduction)

        Returns:
            Path to cleaned audio file
        """
        print(f"\n[AUDIO] Applying noise reduction...")

        try:
            # Load audio
            data, rate = sf.read(audio_path)

            print(f"   Original audio: {len(data)} samples")

            # Apply noise reduction
            # This uses spectral gating to identify and reduce noise
            reduced_noise = nr.reduce_noise(
                y=data,
                sr=rate,
                prop_decrease=prop_decrease,
                stationary=False  # Non-stationary noise (better for variable environments)
            )

            print(f"   Noise reduced by {prop_decrease*100:.0f}%")

            # Save cleaned audio
            output_path = os.path.join(self.temp_dir, "audio_cleaned.wav")
            sf.write(output_path, reduced_noise, rate)

            print(f"[OK] Noise reduction complete")

            return output_path

        except Exception as e:
            print(f"[ERROR] Noise reduction failed: {str(e)}")
            # If noise reduction fails, return original (don't fail the whole pipeline)
            print(f"[WARNING]  Continuing with original audio...")
            return audio_path

    def chunk_audio(self, audio_path: str) -> List[str]:
        """
        Split audio into chunks for processing

        Why chunk:
        - Long conversations take time to process
        - API rate limits and timeouts
        - Parallel processing possible (future optimization)

        Args:
            audio_path: Path to WAV file

        Returns:
            List of paths to chunk files
        """
        print(f"\n[AUDIO] Chunking audio...")

        try:
            # Load audio
            audio = AudioSegment.from_wav(audio_path)
            duration_seconds = len(audio) / 1000

            print(f"   Total duration: {duration_seconds:.1f}s")
            print(f"   Chunk length: {self.chunk_length_seconds}s")

            # If audio shorter than chunk length, no chunking needed
            if duration_seconds <= self.chunk_length_seconds:
                print(f"[OK] Audio shorter than {self.chunk_length_seconds}s, no chunking needed")
                return [audio_path]

            # Split into chunks
            chunk_length_ms = self.chunk_length_seconds * 1000
            chunks = []

            for i, chunk_start_ms in enumerate(range(0, len(audio), chunk_length_ms)):
                chunk = audio[chunk_start_ms:chunk_start_ms + chunk_length_ms]
                chunk_duration = len(chunk) / 1000

                chunk_path = os.path.join(
                    self.temp_dir,
                    f"audio_chunk_{i:03d}.wav"
                )
                chunk.export(chunk_path, format="wav")
                chunks.append(chunk_path)

                print(f"   [PACKAGE] Chunk {i+1}: {chunk_duration:.1f}s -> {os.path.basename(chunk_path)}")

            print(f"[OK] Created {len(chunks)} chunks")

            return chunks

        except Exception as e:
            print(f"[ERROR] Chunking failed: {str(e)}")
            raise

    async def preprocess(self, audio_url: str) -> Tuple[List[str], Dict]:
        """
        Complete preprocessing pipeline (from URL)

        Flow: Download -> Convert -> Clean -> Chunk

        Args:
            audio_url: URL to audio file

        Returns:
            Tuple of (chunk_paths, metadata)
        """
        print("\n" + "="*70)
        print("[AUDIO] AUDIO PREPROCESSING PIPELINE")
        print("="*70)

        try:
            # Step 1: Download
            downloaded_path = await self.download_audio(audio_url)

            # Step 2: Convert to WAV
            wav_path = self.convert_to_wav(downloaded_path)

            # Step 3: Apply noise reduction
            cleaned_path = self.apply_noise_reduction(wav_path)

            # Step 4: Chunk audio
            chunk_paths = self.chunk_audio(cleaned_path)

            # Gather metadata
            audio = AudioSegment.from_wav(cleaned_path)
            metadata = {
                "duration_seconds": len(audio) / 1000,
                "num_chunks": len(chunk_paths),
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "chunk_length": self.chunk_length_seconds
            }

            print("\n" + "="*70)
            print("[OK] PREPROCESSING COMPLETE")
            print(f"   Duration: {metadata['duration_seconds']:.1f}s")
            print(f"   Chunks: {metadata['num_chunks']}")
            print(f"   Sample rate: {metadata['sample_rate']}Hz")
            print("="*70 + "\n")

            return chunk_paths, metadata

        except Exception as e:
            print("\n" + "="*70)
            print("[ERROR] PREPROCESSING FAILED")
            print(f"   Error: {str(e)}")
            print("="*70 + "\n")
            raise

    async def preprocess_file(self, audio_file_path: str, skip_conversion: bool = False) -> Tuple[List[str], Dict]:
        """
        Complete preprocessing pipeline (from file path)

        Flow: Convert -> Clean -> Chunk
        (No download needed - file already on disk!)

        Args:
            audio_file_path: Path to audio file on disk
            skip_conversion: If True, skip WAV conversion for WAV files (OPTIMIZATION)

        Returns:
            Tuple of (chunk_paths, metadata)
        """
        print("\n" + "="*70)
        print("[AUDIO] AUDIO FILE PREPROCESSING")
        print("="*70)
        print(f"File: {audio_file_path}")
        print(f"Skip conversion: {skip_conversion}")

        try:
            # Step 1: Convert to WAV (with optimization)
            wav_path = self.convert_to_wav(audio_file_path, skip_if_wav=skip_conversion)

            # Step 2: Apply noise reduction
            cleaned_path = self.apply_noise_reduction(wav_path)

            # Step 3: Chunk audio
            chunk_paths = self.chunk_audio(cleaned_path)

            # Gather metadata
            audio = AudioSegment.from_wav(cleaned_path)
            metadata = {
                "duration_seconds": len(audio) / 1000,
                "num_chunks": len(chunk_paths),
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "chunk_length": self.chunk_length_seconds,
                "conversion_skipped": skip_conversion and audio_file_path.lower().endswith('.wav')
            }

            print("\n" + "="*70)
            print("[OK] PREPROCESSING COMPLETE")
            print(f"   Duration: {metadata['duration_seconds']:.1f}s")
            print(f"   Chunks: {metadata['num_chunks']}")
            if metadata.get('conversion_skipped'):
                print(f"   [OPTIMIZATION] WAV conversion skipped!")
            print("="*70 + "\n")

            return chunk_paths, metadata

        except Exception as e:
            print("\n" + "="*70)
            print("[ERROR] PREPROCESSING FAILED")
            print(f"   Error: {str(e)}")
            print("="*70 + "\n")
            raise


# ============================================
# Test Function
# ============================================

async def test_preprocessing():
    """
    Test audio preprocessing with a sample file

    To run: python -m audio_pipeline.preprocessing
    """
    print("\n🧪 Testing Audio Preprocessing\n")

    preprocessor = AudioPreprocessor(chunk_length_seconds=90)

    # Test with AssemblyAI's sample audio
    test_audio_url = "https://storage.googleapis.com/aai-docs-samples/espn.m4a"

    try:
        chunks, metadata = await preprocessor.preprocess(test_audio_url)

        print("\n[OK] Test Successful!")
        print(f"\nChunks created: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"  {i+1}. {chunk}")

        print(f"\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_preprocessing())
