import io
import logging
import tempfile
import wave
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from mutagen import File as MutagenFile

logger = logging.getLogger(__name__)


def make_preview(track):
    """Определяет длительность трека и вырезает 30-секундный демофрагмент.

    Полный файл остаётся в protected_media, в публичный каталог media/
    попадает только фрагмент. Основной способ – pydub и FFmpeg (MP3 128 кбит/с
    с затуханием в конце); если FFmpeg не установлен, фрагмент вырезается
    средствами Python без перекодирования.
    """
    path = Path(track.audio_file.path)
    info = MutagenFile(path)
    if info is not None and info.info:
        track.duration = int(info.info.length)

    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(path)
        fragment = audio[:settings.PREVIEW_SECONDS * 1000].fade_out(2000)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'preview.mp3'
            fragment.export(out, format='mp3', bitrate='128k')
            with open(out, 'rb') as f:
                track.preview_file.save(f'{path.stem}_preview.mp3', File(f), save=False)
    except Exception:  # нет FFmpeg – режем без перекодирования
        logger.warning('FFmpeg недоступен, демофрагмент трека %s создаётся без перекодирования', track.pk)
        cut_without_ffmpeg(track, path, info)
    track.save(update_fields=['duration', 'preview_file'])


def cut_without_ffmpeg(track, path, info):
    seconds = settings.PREVIEW_SECONDS
    if path.suffix.lower() == '.wav':
        with wave.open(str(path), 'rb') as src:
            frames = src.readframes(src.getframerate() * seconds)
            params = src.getparams()
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as dst:
            dst.setparams(params)
            dst.writeframes(frames)
        data = buf.getvalue()
    else:
        # MP3 состоит из независимых кадров: первые N байт – это первые N секунд звука
        bitrate = getattr(getattr(info, 'info', None), 'bitrate', 0) or 320_000
        with open(path, 'rb') as src:
            data = src.read(bitrate // 8 * seconds)
    track.preview_file.save(f'{path.stem}_preview{path.suffix.lower()}', ContentFile(data), save=False)
