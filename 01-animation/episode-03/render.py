"""Render the catalog and Cilly episode, reusing the common opening and ending."""

import argparse
import importlib.util
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
EPISODE_ONE = ROOT.parent / 'episode-01'
ARTWORK = ROOT / 'source' / 'task_01M7Z0S8XSRZAHG3JDP46DG5HR-0.png'
spec = importlib.util.spec_from_file_location('episode_one', EPISODE_ONE / 'render.py')
first = importlib.util.module_from_spec(spec)
spec.loader.exec_module(first)

NAMES = ('catalog', 'cilly', 'answer', 'reaction')
CAPTIONS = (
    first.CAPTIONS[0],
    '小帅先翻了猫咪图鉴。',
    '遇到不认识的猫，就拍下来问 Cilly。',
    '后来女神指着一只猫，小帅连它叫什么、平时爱吃什么都知道。',
    '女神一听，原来他也这么喜欢猫。',
    *first.CAPTIONS[4:],
)
AUDIO = (
    EPISODE_ONE / 'audio' / 'opening.mp3',
    *(ROOT / 'audio' / f'{name}.mp3' for name in NAMES),
    EPISODE_ONE / 'audio' / 'feeding-together.mp3',
    EPISODE_ONE / 'audio' / 'ending.mp3',
)
TITLE = '第三段-猫咪图鉴和Cilly-头像版'
PAPER, INK, BLUE, GOLD = first.PAPER, first.INK, first.BLUE, first.GOLD
LABEL = ImageFont.truetype(str(first.FONT_DIR / 'msyh.ttc'), 24)


def load_art():
    art = first.sprite_sheet()
    # Static rasterization of design/xiao-c/avatar-botstyle-v1.svg.
    art['cilly_avatar'] = Image.open(ROOT / 'source' / 'cilly-avatar.png').convert('RGBA')
    sheet = Image.open(ARTWORK).convert('RGB')
    w, h = sheet.width//2, sheet.height//2
    for key, x, y in (('photo', 0, 0), ('point', w, 0), ('explain', 0, h), ('smile', w, h)):
        tile = first.remove_paper(sheet.crop((x, y, x+w, y+h)))
        bounds = tile.getchannel('A').point(lambda a: 255 if a > 90 else 0).getbbox()
        art[key] = tile.crop(bounds)
    return art


def catalog_scene(frame, art, t):
    first.place(frame, first.standing_pose(art, 3*math.sin(t*8)), 320, 149, 412)
    draw = ImageDraw.Draw(frame)
    appeared = first.ease((t-.14)/.35)
    if appeared == 0:
        return
    x = round(746+22*(1-appeared))
    for offset in (22, 11, 0):
        draw.rounded_rectangle((x+offset, 203-offset, x+218+offset, 416-offset), 13,
                               fill='#faf1e2' if offset == 0 else '#fbf8f0', outline='#a18f78', width=2)
    draw.text((x+109, 236), '猫咪图鉴', font=LABEL, fill=INK, anchor='mm')
    slide = first.ease((t-.75)/.33)
    first.place(frame, art['cat'], x+65, 261, 121-5*slide)
    for y in (390, 400):
        first.line(draw, [(x+74, y), (x+143, y)], '#b7a187', 2)
    first.shine(draw, x+224, 218, max(0, 1-abs(t-.58)/.22))


def ask_cilly(frame, art, t):
    draw = ImageDraw.Draw(frame)
    snap = first.ease((t-.69)/.32)
    first.place(frame, art['photo'], 386, 302+6*(1-snap), 250, angle=-2*snap)
    first.place(frame, art['cat'], 710, 428, 132, angle=1.5*math.sin(t*4))
    first.shine(draw, 605, 391, max(0, 1-abs(t-1.12)/.22))
    appeared = first.ease((t-1.58)/.28)
    if appeared == 0:
        return
    x, y = 603, round(282+10*(1-appeared))
    fill = '#e9eef0'
    draw.rounded_rectangle((x, y, x+155, y+87), 22, fill=fill, outline=BLUE, width=2)
    draw.polygon(((x+14, y+65), (x-6, y+93), (x+37, y+84)), fill=fill)
    first.line(draw, [(x+14, y+65), (x-6, y+93), (x+37, y+84)], BLUE, 2)
    first.place(frame, art['cilly_avatar'], x+16, y+17, 53)
    draw.text((x+109, y+43), 'Cilly', font=LABEL, fill=INK, anchor='mm')


def answer_scene(frame, art, t, listening):
    draw = ImageDraw.Draw(frame)
    response = first.ease((t-1.04)/.35) if not listening else 1
    boy = art['explain'] if response > .25 else first.standing_pose(art, -8)
    first.place(frame, boy, 360, 164, 393, angle=.8*response*math.sin(t*5.5))
    girl = art['smile'] if listening else art['point']
    first.place(frame, girl, 739, 178, 371, angle=(1.2 if listening else .45)*math.sin(t*3.4))
    first.place(frame, art['cat_facing_right'], 583, 434+2*math.sin(t*5), 124)
    if not listening:
        shine = max(0, 1-abs(t-.50)/.42)
        first.shine(draw, 705, 403, shine, BLUE)
        if t > 2.42:
            amount = first.ease((t-2.42)/.35)
            x, y = 604, 307
            first.line(draw, [(x-27*amount, y), (x-18*amount,y+12*amount),
                              (x+17*amount,y+12*amount), (x+27*amount,y)], GOLD, 2)
            draw.ellipse((x-27*amount,y-6*amount,x+27*amount,y+4*amount),
                         fill='#e2c49b', outline=GOLD, width=2)
    else:
        first.shine(draw, 847, 209, max(0, 1-abs(t-.65)/.57))
        first.shine(draw, 690, 451, max(0, 1-abs(t-1.4)/.65))


def picture(t, starts, lengths, spoken, art, stages):
    opening, _, _, _, _, feeding, ending = lengths
    common = (opening, 0, 0, 0, feeding, ending)
    if t < opening:
        return first.render_frame(t, common, spoken, art, stages)
    if t >= starts[5]:
        return first.render_frame(t-starts[5]+opening, common, spoken, art, stages)
    shot = next(i for i in range(1, 5) if t < starts[i+1])
    local = t-starts[shot]
    frame = stages['campus' if shot == 1 else 'library'].copy()
    if shot == 1:
        catalog_scene(frame, art, local)
    elif shot == 2:
        ask_cilly(frame, art, local)
    else:
        answer_scene(frame, art, local, listening=shot == 4)
    ImageDraw.Draw(frame).text((640, 653), CAPTIONS[shot], font=first.SUBTITLE, fill=INK, anchor='mm')
    return frame


def soundtrack(path, starts, lengths):
    opening, catalog, cilly, answer, reaction, feeding, ending = lengths
    first.make_bed(path, (opening, catalog, cilly+answer+reaction, 0, feeding, ending))
    with wave.open(str(path), 'rb') as reader:
        params = reader.getparams()
        rate = reader.getframerate()
        signal = np.frombuffer(reader.readframes(reader.getnframes()), dtype='<i2').astype(float)
    for at, duration, freq, strength in ((starts[2]+1.12,.08,980,.034),
                                          (starts[2]+1.83,.26,740,.030),
                                          (starts[4]+.66,.38,660,.020)):
        t = np.arange(round(rate*duration))/rate
        loc = round(at*rate)
        signal[loc:loc+len(t)] += (32767*strength*np.sin(2*np.pi*freq*t)*
                                  np.minimum(1,t/.005)*np.exp(-t*6/duration))
    with wave.open(str(path), 'wb') as writer:
        writer.setparams(params)
        writer.writeframes(np.clip(signal,-32767,32767).astype('<i2').tobytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--stills', action='store_true')
    args = parser.parse_args()
    spoken = [first.media_duration(args.ffmpeg, path) for path in AUDIO]
    padding = (.22,.31,.31,.23,.32,.22,.65)
    lengths = [math.ceil((v+pad)*first.FPS)/first.FPS for v,pad in zip(spoken,padding)]
    starts = np.cumsum([0,*lengths]).tolist()
    art = load_art()
    stages = {key:first.background(key) for key in ('campus','library','walk')}
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    if args.stills:
        marks = [2.6, starts[1]+1.15, starts[2]+2.05, starts[3]+.57,
                 starts[3]+2.75, starts[4]+.92, starts[5]+1.0, starts[6]+1.5]
        board = Image.new('RGB',(960,1080),PAPER)
        for i,t in enumerate(marks):
            shot = picture(t, starts, lengths, spoken, art, stages)
            board.paste(shot.resize((480,270),Image.Resampling.LANCZOS),((i%2)*480,(i//2)*270))
        board.save(output/'storyboard.jpg', quality=93)
        return

    bed = output/'sound-bed.wav'
    soundtrack(bed, starts, lengths)
    cmd = [args.ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt',
           'rgb24','-s',f'{first.WIDTH}x{first.HEIGHT}','-r',str(first.FPS),'-i','-','-i',str(bed)]
    for path in AUDIO:
        cmd += ['-i',str(path)]
    filters = [f'[{i+2}:a]aresample=48000,aformat=channel_layouts=mono,'
               f'apad,atrim=0:{length:.6f}[v{i}]' for i,length in enumerate(lengths)]
    inputs = ''.join(f'[v{i}]' for i in range(len(AUDIO)))
    filters += [f'{inputs}concat=n={len(AUDIO)}:v=0:a=1,volume=1.15[n]',
                '[1:a][n]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.93[a]']
    video = output/f'{TITLE}.mp4'
    cmd += ['-filter_complex',';'.join(filters),'-map','0:v','-map','[a]',
            '-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','160k','-movflags','+faststart',str(video)]
    duration = starts[-1]+.35
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as encoder:
        for i in range(round(duration*first.FPS)):
            frame = picture(i/first.FPS, starts, lengths, spoken, art, stages)
            encoder.stdin.write(frame.tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Episode 3 render failed')
    cues = [f'{i+1}\n{first.timestamp(starts[i])} --> {first.timestamp(starts[i]+spoken[i])}\n{line}'
            for i,line in enumerate(CAPTIONS)]
    video.with_suffix('.srt').write_text('\n\n'.join(cues)+'\n',encoding='utf-8-sig')
    print(f'{video} — {duration:.2f}s')


if __name__ == '__main__':
    main()
