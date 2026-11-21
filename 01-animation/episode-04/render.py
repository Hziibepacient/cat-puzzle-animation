"""Render Xiaoshuai's voice post with the series opening and ending."""

import argparse
import importlib.util
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parent
SHARED = ROOT.parent / 'episode-01' / 'audio'
SPEC = importlib.util.spec_from_file_location('episode_three', ROOT.parent / 'episode-03' / 'render.py')
third = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(third)
first = third.first

ATLAS = ROOT / 'source' / 'task_01M7Z13DZRT1ZFSQSJXZST8JDN-0.png'
TITLE = '第四段-给Cilly发语音'
AUDIO = (
    SHARED / 'opening.mp3',
    *(ROOT / 'audio' / f'{part}.mp3' for part in ('setup', 'message', 'publish', 'girl')),
    SHARED / 'feeding-together.mp3',
    SHARED / 'ending.mp3',
)
CAPTIONS = (
    (first.CAPTIONS[0],),
    ('小帅先遇到了一只猫。', '他拍了张照，拿起手机给 Cilly 发语音。'),
    ('今天下午三点，图书馆门口。', '它在台阶上晒太阳，', '路过的人都忍不住看它一眼。'),
    ('小帅确认发布。',),
    ('女神刷到这条偶遇，', '也赶了过来。'),
    *tuple((line,) for line in first.CAPTIONS[4:]),
)
# Match the pauses in the approved recordings, including the changes of subtitle.
CUE_STARTS = ((0,), (0, 1.90), (0, 2.60, 4.36), (0,), (0, 1.58), (0,), (0,))
PADDING = (.22, .15, .14, .32, .47, .22, .65)
PAPER, INK, BLUE, GOLD = first.PAPER, first.INK, first.BLUE, first.GOLD


def load_art():
    art = third.load_art()
    atlas = Image.open(ATLAS).convert('RGB')
    sx, sy = atlas.width / 800, atlas.height / 531
    boxes = {
        'record': (122, 14, 244, 219),
        'tap': (519, 17, 657, 223),
        'notice': (139, 245, 257, 513),
        'girl_run': (503, 256, 696, 508),
    }
    for name, box in boxes.items():
        x0, y0, x1, y1 = box
        tile = atlas.crop((round(x0*sx), round(y0*sy), round(x1*sx), round(y1*sy)))
        sprite = first.remove_paper(tile)
        mask = Image.new('L', sprite.size)
        draw = ImageDraw.Draw(mask)
        outline = {
            'girl_run': [(503, 256), (696, 256), (696, 401), (644, 404), (633, 416),
                         (609, 428), (583, 437), (550, 437), (521, 430), (503, 430)],
            'tap': [(519, 17), (657, 17), (657, 103), (636, 103),
                    (636, 115), (657, 116), (657, 223), (519, 223)],
        }.get(name)
        if outline:
            draw.polygon([(round((x-x0)*sx), round((y-y0)*sy)) for x, y in outline], fill=255)
            sprite.putalpha(ImageChops.multiply(sprite.getchannel('A'), mask))
        art[name] = sprite
    return art


def cilly_bubble(frame, avatar, t, energy):
    shown = first.ease((t-2.91)/.28)
    if not shown:
        return
    x, y = 570, round(286 + 9*(1-shown))
    draw = ImageDraw.Draw(frame)
    fill = '#e8eef0'
    draw.rounded_rectangle((x, y, x+173, y+74), 20, fill=fill, outline=BLUE, width=2)
    draw.polygon(((x+5, y+53), (x-14, y+72), (x+26, y+71)), fill=fill)
    first.line(draw, [(x+5, y+53), (x-14, y+72), (x+26, y+71)], BLUE, 2)
    first.place(frame, avatar, x+12, y+12, 50)
    draw.text((x+87, y+36), 'Cilly', font=third.LABEL, fill=INK, anchor='mm')
    for i in range(5):
        level = 3 + 13*energy*(.28+.72*abs(math.sin(t*15+i*1.6)))
        bar = x+119+i*8
        first.line(draw, [(bar, y+37-level), (bar, y+37+level)], BLUE, 3)


def library_scene(frame, art, shot, t, energy):
    draw = ImageDraw.Draw(frame)
    if shot == 1 and t < 1.78:
        above = 145 + 3*math.sin(t*2)
        first.place(frame, first.standing_pose(art, -43+13*first.ease((t-.32)/.8)),
                    385, above, 408)
        first.shine(draw, 565, 219, max(0, 1-abs(t-.56)/.30))
    elif shot == 1 and t < 2.89:
        first.place(frame, art['photo'], 359, 297, 258,
                    angle=-1.2*first.ease((t-2.0)/.3))
        first.shine(draw, 570, 388, max(0, 1-abs(t-2.43)/.14))
    elif shot == 3:
        tap = max(0, 1-abs(t-.54)/.21)
        first.place(frame, art['tap'], 388, 297+3*tap, 257, angle=-1.7*tap)
        if t > .54:
            appear = first.ease((t-.54)/.24)
            y = round(362-17*appear)
            r = 20*appear
            draw.ellipse((598-r, y-r, 598+r, y+r), fill='#edf0e3', outline='#72836a', width=2)
            first.line(draw, [(598-8*appear, y), (598-2*appear, y+5*appear),
                              (598+9*appear, y-7*appear)], '#546f52', 3)
            first.shine(draw, 620, y, max(0, 1-abs(t-.76)/.24), '#899775')
    else:
        raising = first.ease((t-2.89)/.22) if shot == 1 else 1
        lift = 2*energy*math.sin(t*16)
        first.place(frame, art['record'], 389, 297+7*(1-raising)+lift, 255,
                    angle=1.3*(1-raising)+.45*energy*math.sin(t*14))
        cilly_bubble(frame, art['cilly_avatar'], t if shot == 1 else t+5, energy)
    first.place(frame, art['cat'], 738, 428+1.4*math.sin(t*4), 132, angle=1.4*math.sin(t*3))


def cat_closeup(frame, cat, t):
    draw = ImageDraw.Draw(frame)
    draw.ellipse((505, 532, 823, 555), fill='#eeeadf')
    first.place(frame, cat, 512, 269+2*math.sin(t*4), 283, angle=1.3*math.sin(t*3))
    for x, y, length in ((815, 283, 31), (824, 306, 40), (829, 332, 35)):
        drift = .6 + .4*math.sin(t*4+x)
        first.line(draw, [(x, y), (x+length*drift, y-16*drift)], '#cfa476', 3)


def girl_notification(frame, art, t):
    first.place(frame, art['notice'], 730, 165, 387, angle=1.4*math.sin(t*5)*math.exp(-t))
    draw = ImageDraw.Draw(frame)
    first.shine(draw, 755, 264, max(0, 1-abs(t-.24)/.22), BLUE)
    appear = first.ease((t-.32)/.3)
    if appear:
        x = round(571+13*(1-appear))
        draw.rounded_rectangle((x, 204, x+122, 322), 10, fill='#faf3e7', outline='#aa9075', width=2)
        first.place(frame, art['cat'], x+21, 217, 91, opacity=appear)
        first.line(draw, [(x+122, 280), (x+154, 289)], '#aa9075', 2)


def girl_running(frame, sprite, t, duration):
    progress = min(1, t/duration)
    center = 950-650*progress
    phase = math.tau*2.4*t
    ground = 550
    hip = ground-95-8*abs(math.sin(phase))
    draw = ImageDraw.Draw(frame)
    draw.ellipse((center-90, ground+1, center+73, ground+8), fill='#eeebe3')
    for offset, outline in ((math.pi, '#68645d'), (0, INK)):
        beat = phase+offset
        sweep = math.sin(beat)
        foot = (center-70*sweep, ground-4-43*max(0, math.cos(beat)))
        knee = (center-38*sweep-11, (hip+foot[1])/2+4)
        points = [(center, hip), knee, foot]
        first.line(draw, points, outline, 13)
        first.line(draw, points, '#f6efe6', 9)
        x, y = foot
        shoe = [(x+7, y-5), (x+10, y+1), (x+6, y+5), (x-17, y+5),
                (x-21, y+1), (x-17, y-3), (x-7, y-3), (x-2, y-9)]
        draw.polygon(shoe, fill=PAPER)
        first.line(draw, [*shoe, shoe[0]], outline, 2)
    first.place(frame, sprite, center-100, hip-208, 293, angle=1.2*math.sin(phase))
    for i in range(3):
        trail = 24+13*math.sin(phase-i)
        first.line(draw, [(center+133, hip-102+i*23),
                          (center+133+trail, hip-103+i*23)], '#aaa8a0', 2)


def cue(shot, local):
    index = sum(local >= start for start in CUE_STARTS[shot])-1
    return CAPTIONS[shot][index]


def picture(t, starts, lengths, spoken, art, backgrounds, speech):
    opening, _, _, _, _, feeding, ending = lengths
    common = (opening, 0, 0, 0, feeding, ending)
    if t < opening:
        return first.render_frame(t, common, spoken, art, backgrounds)
    if t >= starts[5]:
        return first.render_frame(t-starts[5]+opening, common, spoken, art, backgrounds)
    shot = next(i for i in range(1, 5) if t < starts[i+1])
    local = t-starts[shot]
    if shot == 2 and 2.60 <= local < 4.36:
        frame = backgrounds['library_detail'].copy()
        cat_closeup(frame, art['cat'], local-2.60)
    elif shot < 4:
        frame = backgrounds['library'].copy()
        energy = speech[min(len(speech)-1, math.floor(local*first.FPS))] if shot == 2 else 0
        library_scene(frame, art, shot, local, energy)
    elif local < 1.58:
        frame = backgrounds['campus'].copy()
        girl_notification(frame, art, local)
    else:
        frame = backgrounds['path'].copy()
        girl_running(frame, art['girl_run'], local-1.58, lengths[shot]-1.58)
    ImageDraw.Draw(frame).text((640, 653), cue(shot, local), font=first.SUBTITLE, fill=INK, anchor='mm')
    return frame


def dialogue_levels(ffmpeg):
    rate = 24000
    pcm = subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(AUDIO[2]), '-f', 'f32le',
                                   '-ac', '1', '-ar', str(rate), '-'])
    samples = np.frombuffer(pcm, dtype='<f4')
    stride = rate//first.FPS
    rms = np.array([np.sqrt(np.mean(samples[i:i+stride]**2)) for i in range(0, len(samples), stride)])
    return np.clip(rms / max(.02, np.percentile(rms, 89)), 0, 1)


def soundtrack(path, starts, lengths):
    opening, setup, message, publish, girl, feeding, ending = lengths
    first.make_bed(path, (opening, setup, message+publish+girl, 0, feeding, ending))
    with wave.open(str(path), 'rb') as reader:
        params = reader.getparams()
        rate = reader.getframerate()
        signal = np.frombuffer(reader.readframes(reader.getnframes()), dtype='<i2').astype(float)

    def tick(at, duration, freq, strength):
        t = np.arange(round(rate*duration))/rate
        start = round(at*rate)
        signal[start:start+len(t)] += (
            32767*strength*np.sin(math.tau*freq*t)*np.minimum(1,t/.006)*np.exp(-t*6/duration)
        )

    tick(starts[1]+2.43, .07, 1150, .042)
    tick(starts[1]+3.20, .17, 695, .022)
    tick(starts[3]+.54, .19, 780, .027)
    tick(starts[3]+.61, .20, 1046, .021)
    tick(starts[4]+.24, .13, 830, .026)
    for step in np.arange(1.63, girl-.09, .208):
        tick(starts[4]+step, .082, 100, .024)
    with wave.open(str(path), 'wb') as writer:
        writer.setparams(params)
        writer.writeframes(np.clip(signal,-32767,32767).astype('<i2').tobytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--stills', action='store_true')
    args = parser.parse_args()
    spoken = [first.media_duration(args.ffmpeg, path) for path in AUDIO]
    lengths = [math.ceil((v+pad)*first.FPS)/first.FPS for v, pad in zip(spoken, PADDING)]
    starts = np.cumsum([0, *lengths]).tolist()
    art = load_art()
    stages = {key: first.background(key) for key in ('campus', 'library', 'path', 'walk')}
    stages['library_detail'] = stages['library'].copy()
    detail = stages['library'].crop((427, 225, 1120, 553))
    stages['library_detail'].paste(detail.resize((first.WIDTH, 606), Image.Resampling.BICUBIC), (0, 0))
    speech = dialogue_levels(args.ffmpeg)
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    if args.stills:
        marks = [starts[1]+.87, starts[1]+2.44, starts[2]+1.5, starts[2]+3.65,
                 starts[3]+.82, starts[4]+.58, starts[4]+2.12, starts[5]+1.35]
        board = Image.new('RGB', (960, 1080), PAPER)
        for i, t in enumerate(marks):
            shot = picture(t, starts, lengths, spoken, art, stages, speech)
            board.paste(shot.resize((480, 270), Image.Resampling.LANCZOS), (i%2*480, i//2*270))
        board.save(output / 'storyboard.jpg', quality=94)
        return

    bed = output / 'sound-bed.wav'
    soundtrack(bed, starts, lengths)
    cmd = [args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt',
           'rgb24', '-s', f'{first.WIDTH}x{first.HEIGHT}', '-r', str(first.FPS), '-i', '-', '-i', str(bed)]
    for path in AUDIO:
        cmd += ['-i', str(path)]
    filters = [f'[{i+2}:a]aresample=48000,aformat=channel_layouts=mono,'
               f'apad,atrim=0:{length:.6f}[v{i}]' for i, length in enumerate(lengths)]
    inputs = ''.join(f'[v{i}]' for i in range(len(AUDIO)))
    filters += [f'{inputs}concat=n={len(AUDIO)}:v=0:a=1,volume=1.15[n]',
                '[1:a][n]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.93:latency=1[a]']
    video = output / f'{TITLE}.mp4'
    cmd += ['-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(video)]
    duration = starts[-1]+.35
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as encoder:
        for i in range(round(duration*first.FPS)):
            frame = picture(i/first.FPS, starts, lengths, spoken, art, stages, speech)
            encoder.stdin.write(frame.tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Episode 4 render failed')

    cues = []
    for shot, lines in enumerate(CAPTIONS):
        offsets = CUE_STARTS[shot]
        for begin, end, line in zip(offsets, (*offsets[1:], spoken[shot]), lines):
            start = first.timestamp(starts[shot]+begin)
            stop = first.timestamp(starts[shot]+end)
            cues.append(f'{len(cues)+1}\n{start} --> {stop}\n{line}')
    video.with_suffix('.srt').write_text('\n\n'.join(cues)+'\n', encoding='utf-8-sig')
    print(f'{video} ({duration:.2f}s)')


if __name__ == '__main__':
    main()
