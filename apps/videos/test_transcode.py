import io
import subprocess
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import mock, skipUnless

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from apps.videos import transcode
from apps.videos.transcode import ffmpeg_command, needs_transcode, transcode_video


def fake_video(name="videos/files/IMG_1.MOV", pk=1):
    storage = mock.Mock()
    storage.open.return_value = io.BytesIO(b"source-bytes")
    storage.save.return_value = "videos/files/IMG_1.mp4"
    return SimpleNamespace(
        pk=pk,
        title="Відео",
        video_file=SimpleNamespace(name=name, storage=storage),
    )


class NeedsTranscodeTests(SimpleTestCase):
    def test_mov_any_case(self):
        self.assertTrue(needs_transcode(fake_video("a/IMG.MOV")))
        self.assertTrue(needs_transcode(fake_video("a/clip.mov")))

    def test_mp4_and_empty(self):
        self.assertFalse(needs_transcode(fake_video("a/clip.mp4")))
        self.assertFalse(needs_transcode(SimpleNamespace(video_file=None)))

    def test_command_uses_h264_aac_faststart(self):
        command = ffmpeg_command("in", "out.mp4")
        self.assertIn("libx264", command)
        self.assertIn("aac", command)
        self.assertIn("+faststart", command)
        self.assertIn("yuv420p", command)
        self.assertEqual(command[-1], "out.mp4")


def fake_ffmpeg(command, **kwargs):
    Path(command[-1]).write_bytes(b"mp4-bytes")
    return SimpleNamespace(returncode=0, stderr="")


class TranscodeVideoTests(SimpleTestCase):
    def setUp(self):
        field = mock.Mock()
        field.generate_filename.side_effect = lambda instance, name: (
            f"videos/files/{name}"
        )
        meta = mock.patch.object(
            transcode.Video, "_meta", SimpleNamespace(get_field=lambda name: field)
        )
        meta.start()
        self.addCleanup(meta.stop)
        objects = mock.patch.object(transcode.Video, "objects")
        self.objects = objects.start()
        self.addCleanup(objects.stop)

    @mock.patch.object(transcode.subprocess, "run", side_effect=fake_ffmpeg)
    def test_replaces_file_and_keeps_source(self, _run):
        video = fake_video()
        self.objects.filter.return_value.update.return_value = 1

        self.assertTrue(transcode_video(video))

        storage = video.video_file.storage
        self.assertEqual(storage.save.call_args[0][0], "videos/files/IMG_1.mp4")
        self.objects.filter.assert_called_once_with(
            pk=1, video_file="videos/files/IMG_1.MOV"
        )
        self.assertEqual(video.video_file.name, "videos/files/IMG_1.mp4")
        storage.delete.assert_not_called()

    @mock.patch.object(transcode.subprocess, "run", side_effect=fake_ffmpeg)
    def test_delete_source(self, _run):
        video = fake_video()
        self.objects.filter.return_value.update.return_value = 1

        self.assertTrue(transcode_video(video, delete_source=True))
        video.video_file.storage.delete.assert_called_once_with(
            "videos/files/IMG_1.MOV"
        )

    @mock.patch.object(transcode.subprocess, "run", side_effect=fake_ffmpeg)
    def test_concurrent_change_discards_result(self, _run):
        video = fake_video()
        self.objects.filter.return_value.update.return_value = 0

        self.assertFalse(transcode_video(video))
        video.video_file.storage.delete.assert_called_once_with(
            "videos/files/IMG_1.mp4"
        )
        self.assertEqual(video.video_file.name, "videos/files/IMG_1.MOV")

    @mock.patch.object(
        transcode.subprocess,
        "run",
        return_value=SimpleNamespace(returncode=1, stderr="bad input"),
    )
    def test_ffmpeg_error(self, _run):
        with self.assertRaisesMessage(ValueError, "bad input"):
            transcode_video(fake_video())

    def test_skips_mp4(self):
        self.assertFalse(transcode_video(fake_video("a/clip.mp4")))

    @mock.patch.object(transcode, "VIDEO_MAX_SIZE", 3)
    def test_rejects_oversized_source(self):
        with self.assertRaisesMessage(ValueError, "300 MB"):
            transcode_video(fake_video())


class TranscodeCommandTests(SimpleTestCase):
    def videos(self):
        return [fake_video("a/one.MOV", pk=1), fake_video("a/two.mp4", pk=2)]

    def patch_queryset(self):
        queryset = mock.Mock()
        queryset.order_by.return_value = queryset
        queryset.filter.return_value = queryset
        queryset.iterator.return_value = iter(self.videos())
        return mock.patch(
            "apps.videos.management.commands.transcode_videos.Video.objects.exclude",
            return_value=queryset,
        )

    def test_dry_run_lists_only_mov(self):
        out = io.StringIO()
        with self.patch_queryset():
            call_command("transcode_videos", "--dry-run", "--video-id=1", stdout=out)
        self.assertIn("1: Відео (a/one.MOV)", out.getvalue())
        self.assertIn("Відео для перекодування: 1", out.getvalue())

    @mock.patch(
        "apps.videos.management.commands.transcode_videos.which", return_value=None
    )
    def test_requires_ffmpeg(self, _which):
        with self.patch_queryset(), self.assertRaisesMessage(CommandError, "FFmpeg"):
            call_command("transcode_videos", stdout=io.StringIO())

    @mock.patch(
        "apps.videos.management.commands.transcode_videos.which", return_value="ffmpeg"
    )
    @mock.patch(
        "apps.videos.management.commands.transcode_videos.transcode_video",
        side_effect=[True],
    )
    def test_converts(self, transcode_mock, _which):
        out = io.StringIO()
        with self.patch_queryset():
            call_command("transcode_videos", "--delete-source", stdout=out)
        transcode_mock.assert_called_once()
        self.assertTrue(transcode_mock.call_args.kwargs["delete_source"])
        self.assertIn("Перекодовано: 1; пропущено: 0; помилок: 0.", out.getvalue())

    @mock.patch(
        "apps.videos.management.commands.transcode_videos.which", return_value="ffmpeg"
    )
    @mock.patch(
        "apps.videos.management.commands.transcode_videos.transcode_video",
        side_effect=[False],
    )
    def test_skipped(self, _transcode, _which):
        out = io.StringIO()
        with self.patch_queryset():
            call_command("transcode_videos", stdout=out)
        self.assertIn("пропущено: 1", out.getvalue())

    @mock.patch(
        "apps.videos.management.commands.transcode_videos.which", return_value="ffmpeg"
    )
    @mock.patch(
        "apps.videos.management.commands.transcode_videos.transcode_video",
        side_effect=ValueError("boom"),
    )
    def test_failure_raises(self, _transcode, _which):
        err = io.StringIO()
        with self.patch_queryset(), self.assertRaises(CommandError):
            call_command("transcode_videos", stdout=io.StringIO(), stderr=err)
        self.assertIn("boom", err.getvalue())


@skipUnless(which("ffmpeg") and which("ffprobe"), "FFmpeg не встановлено")
class RealFfmpegTests(SimpleTestCase):
    def test_mov_becomes_h264_aac_mp4(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "in.mov"
            target = Path(directory) / "out.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc=size=320x240:rate=10:duration=1",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=duration=1",
                    "-c:v",
                    "mpeg4",
                    "-c:a",
                    "pcm_s16le",
                    str(source),
                ],
                check=True,
                timeout=60,
            )
            subprocess.run(ffmpeg_command(source, target), check=True, timeout=120)
            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "stream=codec_name",
                    "-of",
                    "csv=p=0",
                    str(target),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(probe.stdout.split(), ["h264", "aac"])
