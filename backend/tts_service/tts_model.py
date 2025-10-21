from gtts import gTTS
import re, unicodedata, shutil, subprocess, tempfile


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    replacements = {
        "'": "'", "'": "'", """: '"', """: '"',
        "—": "-", "–": "-", "…": "...", "\u00a0": " ",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    
    # Remove Markdown formatting that causes asterisks in TTS
    # Remove bold/italic asterisks: **text** or *text* -> text
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)  # **bold** -> bold
    s = re.sub(r'\*([^*]+)\*', r'\1', s)      # *italic* -> italic
    
    # Remove other Markdown formatting
    s = re.sub(r'__([^_]+)__', r'\1', s)      # __underline__ -> underline
    s = re.sub(r'_([^_]+)_', r'\1', s)        # _underline_ -> underline
    s = re.sub(r'`([^`]+)`', r'\1', s)        # `code` -> code
    s = re.sub(r'```[^`]*```', '', s)         # Remove code blocks
    s = re.sub(r'#{1,6}\s*', '', s)           # Remove headers # ## ###
    s = re.sub(r'^\s*[-*+]\s+', '', s, flags=re.MULTILINE)  # Remove bullet points
    s = re.sub(r'^\s*\d+\.\s+', '', s, flags=re.MULTILINE)  # Remove numbered lists
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)  # [link text](url) -> link text
    
    # Clean up any remaining asterisks that might be standalone
    s = re.sub(r'\*+', '', s)
    
    s = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in s)
    return re.sub(r"\s+", " ", s).strip()


def generate_tts(text: str, output_path: str):
    """Generate speech from text using gTTS and save as MP3"""
    tts = gTTS(text=text, lang="en")
    tts.save(output_path)


def speed_up_wav(input_path: str, speed: float = 1.0) -> str:
    """Adjust playback speed using FFmpeg (if available)"""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path or abs(speed - 1.0) < 1e-6:
        return input_path

    out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    subprocess.run(
        [ffmpeg_path, "-y", "-i", input_path, "-filter:a", f"atempo={speed}", "-vn", out_path],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return out_path
