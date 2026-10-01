import logging
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files import File
from mutagen import File as MutagenFile

logger = logging.getLogger(__name__)


def make_preview(track):
    """Определяет длительность трека и вырезает 30-секундный демофрагмент.

    Полный файл остаётся в protected_media, в публичный каталог media/
    попадает только фрагмент. Для нарезки нужен FFmpeg.
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
    except Exception:  # нет FFmpeg или файл повреждён
        logger.exception('Не удалось создать демофрагмент для трека %s', track.pk)
    track.save(update_fields=['duration', 'preview_file'])
