"""Render the friend-subscription story using the approved common scenes."""

import argparse
import importlib.util
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
EPISODE_ONE = ROOT.parent / 'episode-01'
ARTWORK = ROOT / 'source' / 'task_01M7Z0CYQD2APEGBJDAEWQDDMC-0.png'
spec = importlib.util.spec_from_file_location('episode_one', EPISODE_ONE / 'render.py')
first = importlib.util.module_from_spec(spec)
spec.loader.exec_module(first)

CAPTIONS = (
    first.CAPTIONS[0],
    '他在 App 上添加了女神好友，订阅了她的偶遇动态。',
    '她刚发了一条，他的手机就响了。',
    *first.CAPTIONS[3:],
)
AUDIO = (
    EPISODE_ONE / 'audio' / 'opening.mp3',
    ROOT / 'audio' / 'friends.mp3',
    ROOT / 'audio' / 'alert.mp3',
    *(EPISODE_ONE / 'audio' / f'{name}.mp3' for name in first.CLIPS[3:]),
)
TITLE = '第二段-好友偶遇提醒-更新跑步台词'
POST_CUT = 1.04
RING = 1.53
PAPER, INK, BLUE, GOLD = first.PAPER, first.INK, first.BLUE, first.GOLD


def load_story_art():
    art = first.sprite_sheet()
    sheet = Image.open(ARTWORK).convert('RGB')
    half_width, half_height = sheet.width//2, sheet.height//2
    for name, x, y in (('wave', 0, 0), ('photo', half_width, 0),
                       ('reading', 0, half_height), ('standing_up', half_width, half_height)):
        tile = first.remove_paper(sheet.crop((x, y, x+half_width, y+half_height)))
        if name == 'standing_up':
            # The generated phone is floating next to his hand. Animate it as its own prop.
            phone_box = tuple(round(value*sheet.size[axis%2]/(979, 650)[axis%2])
                              - (x, y)[axis%2]
                              for axis, value in enumerate((811, 527, 852, 550)))
            phone = tile.crop(phone_box)
            art['phone'] = phone.crop(phone.getbbox())
            tile.paste((0, 0, 0, 0), phone_box)
        bounds = tile.getchannel('A').point(lambda a: 255 if a > 90 else 0).getbbox()
        art[name] = tile.crop(bounds)
    return art


def paper_bell(draw, x, y, amount):
    if amount <= 0:
        return
    def point(dx, dy):
        return x+dx*amount, y+dy*amount
    outline = [point(dx, dy) for dx, dy in ((-20, 12), (-15, 6), (-14, -8),
               (-9, -18), (0, -22), (9, -18), (14, -8), (15, 6), (20, 12))]
    draw.polygon(outline, fill='#f2debd')
    first.line(draw, outline + [outline[0]], GOLD, 2)
    first.line(draw, [point(-5, 18), point(0, 21), point(5, 18)], GOLD, 2)
    for side in (-1, 1):
        first.line(draw, [point(side*23, -10), point(side*30, -16)], GOLD, 2)


def connect_friends(frame, art, t):
    draw = ImageDraw.Draw(frame)
    greet = first.ease((t-.26)/.62)
    first.place(frame, first.standing_pose(art, 2*math.sin(t*5)*greet), 320, 149, 412)
    first.place(frame, art['wave'], 759+28*(1-greet), 164, 377,
                angle=greet*.8*math.sin(t*4), opacity=greet)
    if t > .9:
        # A friendly greeting and a small bell are illustration cues, outside the phone.
        first.shine(draw, 752, 275, max(0, 1-abs(t-1.35)/.52), BLUE)
    picture_tick = first.ease((t-1.73)/.36)
    if picture_tick > 0:
        first.line(draw, [(556, 308), (556+107*picture_tick, 303), (556+174*picture_tick, 307)],
                   '#b8b4a5', 2)
        paper_bell(draw, 650, 291, first.ease((t-2.00)/.42))


def shutter(frame, art, t):
    draw = ImageDraw.Draw(frame)
    press = first.ease((t-.17)/.25)
    draw.ellipse((397, 552, 785, 565), fill='#efebe3')
    first.place(frame, art['photo'], 434, 296+3*(1-press), 260, angle=-1.2*press)
    first.place(frame, art['cat'], 697, 422, 134, angle=-1.7*math.sin(t*5))
    flash = max(0, 1-abs(t-.48)/.21)
    first.shine(draw, 619, 390, flash)
    if t > .59:
        sent = first.ease((t-.59)/.28)
        # Two pen strokes echo the posting gesture without displaying UI.
        first.line(draw, [(620, 386), (620+20*sent, 376-8*sent)], BLUE, 2)
        first.line(draw, [(622, 394), (622+15*sent, 390-3*sent)], BLUE, 2)


def bench(draw):
    rail = '#a7ab9e'
    for y in (385, 402):
        first.line(draw, [(269, y), (602, y+2)], rail, 2)
    first.line(draw, [(279, 388), (272, 464), (624, 464), (609, 447), (272, 447)], rail, 3)
    first.line(draw, [(600, 389), (610, 447)], rail, 2)
    first.line(draw, [(288, 466), (285, 548)], rail, 3)
    first.line(draw, [(606, 466), (611, 548)], rail, 3)


def receive_alert(frame, art, t):
    draw = ImageDraw.Draw(frame)
    bench(draw)
    after_ring = t-RING
    rise = first.ease((after_ring-.19)/.34)
    if rise < .42:
        first.place(frame, art['reading'], 350, 308-14*rise, 243, angle=1+rise*3)
    else:
        height = 335+10*rise
        first.place(frame, art['standing_up'], 377+36*rise, 550-height, height)
    # The phone sits on the bench and buzzes before he reaches for it.
    pulse = 2.4*math.sin(after_ring*36)*max(0, 1-after_ring/.64) if after_ring > 0 else 0
    reach = first.ease((rise-.52)/.48)
    x = 576+pulse+46*reach
    y = 442-7*reach
    first.place(frame, art['phone'], x, y, 15, angle=3*reach)
    if after_ring > 0:
        wordless_ring = 1-abs((after_ring-.22)/.36)
        first.shine(draw, x+17, y-14, max(0, wordless_ring), BLUE)
        paper_bell(draw, 698, 375, first.ease(after_ring/.19)*(1-first.ease((after_ring-.7)/.4)))


def picture(t, lengths, spoken, art, stages):
    # Episodes share the opening and the complete two-shot fairytale ending.
    opening, friends, alert, run, feeding, ending = lengths
    alert_start = opening+friends
    run_start = alert_start+alert
    feeding_start = run_start+run
    common = (opening, 0, 0, 0, feeding, ending)
    if t < opening:
        return first.render_frame(t, common, spoken, art, stages)
    if t >= feeding_start:
        return first.render_frame(t-feeding_start+opening, common, spoken, art, stages)
    if t < alert_start:
        frame = stages['campus'].copy()
        connect_friends(frame, art, t-opening)
        caption = CAPTIONS[1]
    elif t < run_start:
        local = t-alert_start
        if local < POST_CUT:
            frame = stages['library'].copy()
            shutter(frame, art, local)
        else:
            frame = stages['path'].copy()
            receive_alert(frame, art, local)
        caption = CAPTIONS[2] if local < spoken[2] else ''
    else:
        elapsed = t-run_start
        frame = stages['path'].copy()
        first.runner(frame, art, elapsed, run)
        caption = CAPTIONS[3] if elapsed < spoken[3] else ''
    if caption:
        ImageDraw.Draw(frame).text((640, 653), caption, font=first.SUBTITLE, fill=INK, anchor='mm')
    return frame


def sound_bed(path, lengths):
    first.make_bed(path, lengths)
    with wave.open(str(path), 'rb') as reader:
        params = reader.getparams()
        rate = reader.getframerate()
        channel = np.frombuffer(reader.readframes(reader.getnframes()), dtype='<i2').astype(float)
    alert_start = sum(lengths[:2])

    def add(start, seconds, volume, pattern):
        position = round(rate*start)
        t = np.arange(round(rate*seconds))/rate
        envelope = np.minimum(1, t/.004)*np.exp(-t/seconds*6)
        channel[position:position+len(t)] += volume*32767*envelope*pattern(t)

    add(alert_start+.48, .085, .032, lambda t: np.sin(2*np.pi*987*t)*np.cos(2*np.pi*373*t))
    add(alert_start+RING, .35, .058, lambda t: np.sin(2*np.pi*988*t))
    add(alert_start+RING+.10, .38, .036, lambda t: np.sin(2*np.pi*1319*t))
    with wave.open(str(path), 'wb') as writer:
        writer.setparams(params)
        writer.writeframes(np.clip(channel,-32767,32767).astype('<i2').tobytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--stills', action='store_true')
    args = parser.parse_args()
    voice = [first.media_duration(args.ffmpeg, path) for path in AUDIO]
    pads = (.22, .20, .43, .20, .22, .65)
    lengths = [math.ceil((v+pad)*first.FPS)/first.FPS for v, pad in zip(voice, pads)]
    lengths[3] = max(lengths[3], 48/first.FPS)
    starts = np.cumsum([0, *lengths]).tolist()
    art = load_story_art()
    stages = {key: first.background(key) for key in ('campus', 'path', 'library', 'walk')}
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    if args.stills:
        marks = [2.6, starts[1]+2.8, starts[2]+.48, starts[2]+RING+.46,
                 starts[3]+.55, starts[4]+1, starts[5]+1.57]
        board = Image.new('RGB', (960, 1080), PAPER)
        for idx, t in enumerate(marks):
            frame = picture(t, lengths, voice, art, stages)
            board.paste(frame.resize((480,270), Image.Resampling.LANCZOS), ((idx%2)*480,(idx//2)*270))
        board.save(out/'storyboard.jpg', quality=92)
        return

    bed = out / 'sound-bed.wav'
    sound_bed(bed, lengths)
    command = [args.ffmpeg, '-hide_banner','-loglevel','error','-y','-f','rawvideo',
               '-pix_fmt','rgb24','-s',f'{first.WIDTH}x{first.HEIGHT}','-r',str(first.FPS),
               '-i','-','-i',str(bed)]
    for path in AUDIO:
        command += ['-i', str(path)]
    filters = [f'[{i+2}:a]aresample=48000,aformat=channel_layouts=mono,'
               f'volume={1.5 if i == 3 else 1},apad,atrim=0:{length:.6f}[v{i}]'
               for i, length in enumerate(lengths)]
    voices = ''.join(f'[v{i}]' for i in range(len(AUDIO)))
    filters += [f'{voices}concat=n={len(AUDIO)}:v=0:a=1,volume=1.15[n]',
                '[1:a][n]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.93[a]']
    video = out/f'{TITLE}.mp4'
    command += ['-filter_complex',';'.join(filters),'-map','0:v','-map','[a]',
                '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
                '-c:a','aac','-b:a','160k','-movflags','+faststart',str(video)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for frame in range(round((starts[-1]+.35)*first.FPS)):
            encoder.stdin.write(picture(frame/first.FPS, lengths, voice, art, stages).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Episode 2 render failed')
    cues = [f'{i+1}\n{first.timestamp(starts[i])} --> {first.timestamp(starts[i]+voice[i])}\n{text}'
            for i, text in enumerate(CAPTIONS)]
    video.with_suffix('.srt').write_text('\n\n'.join(cues)+'\n', encoding='utf-8-sig')
    print(f'{video} — {starts[-1]+.35:.2f}s')


if __name__ == '__main__':
    main()
