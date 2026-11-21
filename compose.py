"""Assemble the four edited episodes and the hand-drawn question at the end."""

import argparse
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SPEC = spec_from_file_location("episode_one", ROOT / "episode-01" / "render.py")
renderer = module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)
FPS = renderer.FPS
SAMPLES_PER_FRAME = 48000 // FPS
QUICK_SPEED = 1.3
QUESTION_DELAY = 0.2
QUESTION_FRAMES = 80
QUESTION = "那么，这个 APP 是什么呢？"
TITLES = (
    "第一段-偶遇广场-更新跑步台词",
    "第二段-好友偶遇提醒-更新跑步台词",
    "第三段-猫咪图鉴和Cilly-头像版",
    "第四段-给Cilly发语音",
)


@dataclass(frozen=True)
class Segment:
    input_index: int
    start: int
    stop: int
    speed: float = 1.0

    @property
    def frames(self):
        return round((self.stop - self.start) / self.speed)


def read_cues(path):
    stamp = r"(\d+):(\d{2}):(\d{2}),(\d{3})"

    def seconds(time):
        hours, minutes, seconds, ms = map(int, time)
        return hours * 3600 + minutes * 60 + seconds + ms / 1000

    cue_pattern = rf"^{stamp} --> {stamp}\n(.+)$"
    content = path.read_text(encoding="utf-8-sig")
    return [(seconds(cue[:4]), seconds(cue[4:8]), cue[8])
            for cue in re.findall(cue_pattern, content, re.MULTILINE)]


def frame_count(ffmpeg, path):
    progress = subprocess.check_output(
        [ffmpeg, "-v", "error", "-nostats", "-progress", "pipe:1", "-i", str(path),
         "-map", "0:v:0", "-c:v", "copy", "-f", "null", "-"],
        text=True,
    )
    return int(re.findall(r"^frame=(\d+)$", progress, re.MULTILINE)[-1])


def timeline(ffmpeg, inputs):
    scenes, combined_cues = [], []
    offset = 0
    for index, path in enumerate(inputs):
        frames = frame_count(ffmpeg, path)
        cues = read_cues(path.with_suffix(".srt"))
        if not cues:
            raise ValueError(f"No cues in {path.with_suffix('.srt')}")
        if index == 0:
            clips = [Segment(index, 0, frames)]
        else:
            opening_end = round(cues[1][0] * FPS)
            ending_start = round(cues[-1][0] * FPS)
            clips = [
                Segment(index, 0, opening_end, QUICK_SPEED),
                Segment(index, opening_end, ending_start),
                Segment(index, ending_start, frames, QUICK_SPEED),
            ]
        for clip in clips:
            for begin, end, line in cues:
                start_frame, stop_frame = begin * FPS, end * FPS
                if clip.start - 0.02 <= start_frame < clip.stop - 0.02:
                    start = (offset + (start_frame - clip.start) / clip.speed) / FPS
                    stop = (offset + (stop_frame - clip.start) / clip.speed) / FPS
                    combined_cues.append((start, stop, line))
            offset += clip.frames
        scenes.extend(clips)
    combined_cues.append((offset / FPS + QUESTION_DELAY, (offset + QUESTION_FRAMES) / FPS, QUESTION))
    return scenes, combined_cues


def draw_question(destination, ffmpeg):
    assets = ROOT / "assets"
    music = ROOT / "episode-01" / "output" / "sound-bed.wav"
    voice = assets / "transition-narration.mp3"
    size = (renderer.WIDTH, renderer.HEIGHT)
    art = renderer.sprite_sheet()
    campus = renderer.background("campus")
    small = ImageFont.truetype(str(renderer.FONT_DIR / "STKAITI.TTF"), 55)
    large = ImageFont.truetype(str(renderer.FONT_DIR / "STKAITI.TTF"), 70)
    frames = QUESTION_FRAMES
    duration = frames / FPS

    def frame(t):
        pic = campus.copy()
        lift = renderer.ease((t-.25)/.55)
        bend = -28*(1-lift)+1.3*math.sin(t*4)*lift
        renderer.place(pic, renderer.standing_pose(art, bend), 320, 149, 412)
        ImageDraw.Draw(pic).text((613, 246), '那么，这个', font=small, fill=renderer.INK)
        visible = renderer.ease((t-.72)/.24)
        if visible:
            overlay = Image.new('RGBA', size)
            draw = ImageDraw.Draw(overlay)
            alpha = round(255*visible)
            def ink(color):
                return (*bytes.fromhex(color[1:]), alpha)
            draw.text((609, 322), 'APP', font=large, fill=ink(renderer.BLUE))
            draw.text((756, 322), '是什么呢？', font=large, fill=ink(renderer.INK))
            line = renderer.ease((t-.88)/.46)
            if line:
                renderer.line(draw, [(617, 404), (617+103*line, 399),
                                  (617+123*line, 404)], '#d6aa75', 4)
            pic.paste(overlay, (0, 0), overlay)
        return pic

    mix = (
        f"[1:a]aresample=48000,aformat=channel_layouts=mono,"
        f"adelay={round(QUESTION_DELAY * 1000)}:all=1,volume=1.12[voice];"
        f"[2:a]atrim=end={duration:.6f},volume=0.7,afade=d=0.22,"
        f"afade=t=out:st={duration - 0.30:.6f}:d=0.30[bed];"
        "[bed][voice]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93:latency=1[a]"
    )
    cmd = [ffmpeg, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
           "-i", str(voice), "-i", str(music), "-filter_complex", mix,
           "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", str(destination)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as encoder:
        for i in range(frames):
            encoder.stdin.write(frame(i / FPS).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError("Question scene encoding failed")


def assemble(ffmpeg, inputs, segments, output):
    cmd = [ffmpeg, "-v", "error", "-n"]
    for path in inputs:
        cmd.extend(["-i", str(path)])
    filters = []
    for i, part in enumerate(segments):
        filters.extend([
            f"[{part.input_index}:v]trim=start_frame={part.start}:end_frame={part.stop},"
            f"setpts=(PTS-STARTPTS)/{part.speed},fps={FPS}:start_time=0,"
            f"tpad=stop_mode=clone:stop=2,trim=end_frame={part.frames},setpts=N/({FPS}*TB)[v{i}]",
            f"[{part.input_index}:a]atrim=start_sample={part.start * SAMPLES_PER_FRAME}:"
            f"end_sample={part.stop * SAMPLES_PER_FRAME},asetpts=PTS-STARTPTS,atempo={part.speed},"
            f"apad,atrim=end_sample={part.frames * SAMPLES_PER_FRAME},asetpts=N/SR/TB[a{i}]",
        ])
    labels = "".join(f"[v{i}][a{i}]" for i in range(len(segments)))
    filters.append(f"{labels}concat=n={len(segments)}:v=1:a=1[v][a]")
    cmd.extend(["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output)])
    subprocess.run(cmd, check=True)
    if frame_count(ffmpeg, output) != sum(part.frames for part in segments):
        raise RuntimeError("Unexpected timeline length in exported video")


def save_cues(path, cues):
    blocks = [f"{i}\n{renderer.timestamp(begin)} --> {renderer.timestamp(end)}\n{line}"
              for i, (begin, end, line) in enumerate(cues, start=1)]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--output", default=ROOT / "build" / "Cat PUZZLE-重剪.mp4", type=Path)
    parser.add_argument("--subtitles-only", action="store_true")
    args = parser.parse_args()
    sources = [ROOT / f"episode-{index:02}" / "output" / f"{title}.mp4"
               for index, title in enumerate(TITLES, start=1)]
    segments, cues = timeline(args.ffmpeg, sources)
    if not args.subtitles_only:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="cat-puzzle-") as scratch:
            bridge = Path(scratch) / "question.mp4"
            draw_question(bridge, args.ffmpeg)
            segments.append(Segment(len(sources), 0, QUESTION_FRAMES))
            assemble(args.ffmpeg, [*sources, bridge], segments, args.output)
    save_cues(args.output.with_suffix(".srt"), cues)


if __name__ == "__main__":
    main()
