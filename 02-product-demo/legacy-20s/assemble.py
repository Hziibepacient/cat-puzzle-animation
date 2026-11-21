from pathlib import Path
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

JOB = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS = 1920, 1080, 30
LEFT, TOP, SCREEN_W, SCREEN_H = 735, 53, 450, 974
DURATION = 20
SCENES = ("01-welcome", "02-assistant", "03-square", "04-catalog", "05-messages")


def frame_art(path):
    y, x = np.ogrid[:HEIGHT, :WIDTH]
    shade = np.exp(-(((x - WIDTH/2) / 660) ** 2 + ((y - 430) / 780) ** 2))
    paper = np.array([246, 243, 236], dtype=np.float32)
    warm_light = np.array([7, 7, 8], dtype=np.float32)
    rgb = np.uint8(np.around(paper + shade[..., None] * warm_light))
    art = Image.fromarray(rgb).convert("RGBA")

    shadow = Image.new("RGBA", art.size)
    draw = ImageDraw.Draw(shadow)
    draw.rounded_rectangle((LEFT-15, TOP+1, LEFT+SCREEN_W+15, TOP+SCREEN_H+22),
                           radius=54, fill=(59, 49, 32, 63))
    art.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(23)))
    draw = ImageDraw.Draw(art)
    draw.rounded_rectangle((LEFT-13, TOP+161, LEFT-7, TOP+223), radius=3, fill="#302E2B")
    draw.rounded_rectangle((LEFT-13, TOP+240, LEFT-7, TOP+303), radius=3, fill="#302E2B")
    draw.rounded_rectangle((LEFT+SCREEN_W+7, TOP+204, LEFT+SCREEN_W+13, TOP+290),
                           radius=3, fill="#302E2B")
    draw.rounded_rectangle((LEFT-11, TOP-11, LEFT+SCREEN_W+10, TOP+SCREEN_H+10),
                           radius=49, fill="#4B4843")
    draw.rounded_rectangle((LEFT-9, TOP-9, LEFT+SCREEN_W+8, TOP+SCREEN_H+8),
                           radius=47, fill="#22211F")
    draw.rounded_rectangle((LEFT-1, TOP-1, LEFT+SCREEN_W, TOP+SCREEN_H),
                           radius=39, fill="#101010")

    supersample = 4
    matte = Image.new("L", (SCREEN_W * supersample, SCREEN_H * supersample))
    ImageDraw.Draw(matte).rounded_rectangle((0, 0, matte.width-1, matte.height-1),
                                           radius=38*supersample, fill=255)
    matte = matte.resize((SCREEN_W, SCREEN_H), Image.Resampling.LANCZOS)
    alpha = Image.new("L", art.size, 255)
    alpha.paste(matte.point(lambda value: 255-value), (LEFT, TOP))
    art.putalpha(alpha)
    art.save(path)


def music(path):
    rate = 48000
    signal = np.zeros((DURATION * rate, 2), dtype=np.float64)

    def pluck(at, note, gain, pan, seconds, bass=False):
        start = round(at * rate)
        length = min(round(seconds * rate), len(signal) - start)
        if length <= 0:
            return
        time = np.arange(length) / rate
        frequency = 440 * 2**((note-69) / 12)
        phase = 2*np.pi*frequency*time
        if bass:
            tone = np.sin(phase)*np.exp(-3.0*time) + 0.18*np.sin(2*phase)*np.exp(-6*time)
        else:
            tone = sum(weight*np.sin(partial*phase)*np.exp(-decay*time)
                       for partial, weight, decay in ((1,1,4.1),(2.001,.23,8.0),
                                                        (3.01,.072,13),(4.12,.018,23)))
        rise = np.minimum(time / .025, 1)
        fall = np.minimum((seconds-time) / .12, 1)
        note_wave = gain * tone * rise * fall
        stereo = np.array([math.cos((pan+1)*math.pi/4),math.sin((pan+1)*math.pi/4)])
        signal[start:start+length] += note_wave[:,None] * stereo

    chords = ((48,55,60,64,67), (45,52,55,60,64), (41,48,53,57,64), (43,50,55,59,62),
              (48,55,60,64,69), (40,47,55,59,64), (41,48,53,57,60), (43,50,55,59,67),
              (45,52,57,60,64), (48,55,60,64,67))
    phrase = (
        ((.50,72), (1.00,76), (1.50,74)),
        ((.25,72), (1.25,69), (1.75,72)),
        ((.50,76), (1.25,77), (1.75,76)),
        ((.25,74), (1.25,71), (1.75,67)),
        ((.50,72), (1.00,76), (1.50,79)),
        ((.25,76), (1.25,74), (1.75,71)),
        ((.50,72), (1.00,69), (1.50,67)),
        ((.25,71), (1.25,74), (1.75,76)),
        ((.50,72), (1.25,69), (1.75,67)),
        ((.50,72), (1.00,76), (1.50,72)),
    )
    for bar, (root, fifth, a, b, c) in enumerate(chords):
        at = .08 + 2*bar
        pluck(at, root, .22, -.10, 1.32, bass=True)
        pluck(at+1, fifth, .10, .12, .87, bass=True)
        for beat, note in ((.25,a), (.75,b), (1.25,c), (1.50,b)):
            pluck(at+beat, note, .068, -.33 if beat<1 else .30, 1.22)
        for beat, note in phrase[bar]:
            pluck(at+beat, note, .122, .16, 1.32)
    quiet_layer = signal.copy()
    for delta, gain in ((.098,.135), (.189,.075), (.294,.04)):
        shift = round(delta * rate)
        signal[shift:] += quiet_layer[:-shift, ::-1] * gain
    time = np.arange(len(signal)) / rate
    volume = np.minimum(1, time/.32) * np.minimum(1, (DURATION-time)/.84)
    signal *= volume[:, None]
    rms = np.sqrt(np.mean(signal**2))
    signal *= min(10**(-20.5/20)/rms, .65/np.max(np.abs(signal)))
    with wave.open(str(path), "wb") as out:
        out.setparams((2,2,rate,0,"NONE","not compressed"))
        out.writeframes(np.around(signal*32767).astype("<i2").tobytes())


def compose(target):
    frame = JOB / "phone-frame.png"
    soundtrack = JOB / "ui-music.wav"
    frame_art(frame)
    music(soundtrack)
    script = [
        f"[{i}:v]trim=duration=4,setpts=PTS-STARTPTS,fps={FPS},"
        f"crop=390:844:0:0,scale={SCREEN_W}:{SCREEN_H}:flags=lanczos,setsar=1,"
        "tpad=stop_mode=clone:stop_duration=0.5,trim=duration=4"
        f"[scene{i}]"
        for i in range(len(SCENES))
    ]
    script += [
        "".join(f"[scene{i}]" for i in range(len(SCENES)))
        + f"concat=n={len(SCENES)}:v=1:a=0,pad={WIDTH}:{HEIGHT}:{LEFT}:{TOP}[screen]",
        "[screen][5:v]overlay=eof_action=repeat:repeatlast=1,format=yuv420p[video]",
    ]
    ffmpeg = sys.argv[2] if len(sys.argv) > 2 else "ffmpeg"
    args = [str(ffmpeg), "-hide_banner", "-nostdin", "-loglevel", "error", "-y"]
    for scene in SCENES:
        args += ["-i", str(JOB / (scene + ".webm"))]
    args += ["-i", str(frame), "-i", str(soundtrack), "-filter_complex_threads", "2",
             "-filter_complex", ";".join(script), "-map", "[video]", "-map", "6:a:0",
             "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-c:a", "aac",
             "-b:a", "192k", "-t", str(DURATION), "-movflags", "+faststart", str(target)]
    subprocess.run(args, check=True)


if __name__ == "__main__":
    compose(Path(sys.argv[1]))
