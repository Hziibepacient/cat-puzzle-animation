"""Render the first Cat Puzzle story with the four original APIMart drawings."""

import argparse
import math
import os
from pathlib import Path
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source' / 'task_01M7YZ37TJ0896X40V9VAYR3D8-0.png'
WALK_SOURCE = ROOT / 'source' / 'walk' / 'task_01M7Z04ADTHZT8KMS04XZJ38J0-0.png'
WIDTH, HEIGHT, FPS = 1280, 720, 30
PAPER = '#fdfcf9'
INK = '#252526'
BLUE = '#526f88'
GOLD = '#d48844'
MUTED = '#a0a79b'
CAPTIONS = (
    '有一个大学生叫小帅，他最近下载了一个 APP。',
    '小帅在偶遇广场刷到了女神发的猫咪照片。',
    '他一看，地点就在图书馆门口。',
    '小帅立马跑了过去。',
    '小帅和女神一起喂猫。',
    '从此他和女神幸福快乐的生活在了一起。',
)
CLIPS = ('opening', 'feed', 'library', 'run', 'feeding-together', 'ending')
FONT_DIR = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
SUBTITLE = ImageFont.truetype(str(FONT_DIR / 'msyh.ttc'), 34)
HAND = ImageFont.truetype(str(FONT_DIR / 'STKAITI.TTF'), 43)
NAME = ImageFont.truetype(str(FONT_DIR / 'STKAITI.TTF'), 88)
SIGN = ImageFont.truetype(str(FONT_DIR / 'STKAITI.TTF'), 30)


def ease(value):
    t = min(1, max(0, value))
    return t * t * (3 - 2 * t)


def line(draw, points, color=INK, width=3):
    draw.line(points, fill=color, width=width, joint='curve')
    radius = width / 2
    for x, y in (points[0], points[-1]):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def curve(points, samples=24):
    a, b, c, d = points
    return [tuple((1-t)**3*a[i] + 3*t*(1-t)**2*b[i] +
                  3*t*t*(1-t)*c[i] + t**3*d[i] for i in range(2))
            for t in np.linspace(0, 1, samples)]


def sprout(draw, x, y, size=1):
    for points in (((0, 0), (-3, -17), (-11, -20), (-18, -21)),
                   ((0, 0), (1, -22), (7, -28), (14, -32)),
                   ((0, 0), (5, -10), (15, -10), (20, -11))):
        line(draw, curve([(x+a*size, y+b*size) for a, b in points]), MUTED, 2)


def campus_tree(draw, x, y, scale):
    tone = '#a7ab9e'
    contours = (
        ((0, 0), (-6, -72), (19, -161), (11, -205)),
        ((9, -116), (31, -151), (47, -138), (64, -178)),
        ((11, -158), (1, -185), (-36, -174), (-49, -207)),
        ((-49, -207), (-88, -211), (-79, -263), (-22, -264)),
        ((-22, -264), (13, -305), (69, -290), (73, -255)),
        ((73, -255), (132, -260), (109, -187), (64, -178)),
    )
    for contour in contours:
        line(draw, curve([(x+dx*scale, y+dy*scale) for dx, dy in contour]), tone, 2)


def background(location):
    image = Image.new('RGB', (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    for x in range(32, WIDTH, 64):
        draw.line((x, 0, x, 608), fill='#f4f2ee')
    for y in range(30, 608, 64):
        draw.line((0, y, WIDTH, y), fill='#f4f2ee')

    if location in ('campus', 'path'):
        line(draw, curve(((86, 551), (360, 545), (888, 558), (1190, 550))), '#b2b2a6', 2)
        for x, scale in ((114, 1), (287, .6), (992, .65), (1152, .85)):
            sprout(draw, x, 550, scale)
        if location == 'campus':
            line(draw, [(710, 493), (1038, 495), (1056, 509), (696, 508), (710, 493)], '#aba99b', 2)
            line(draw, [(727, 490), (742, 434), (1019, 435), (1037, 490)], '#a7ab9e', 2)
            line(draw, [(735, 454), (1025, 456)], '#a7ab9e', 2)
            line(draw, [(715, 509), (719, 548)], '#a7ab9e', 3)
            line(draw, [(1033, 509), (1027, 548)], '#a7ab9e', 3)
            line(draw, curve(((1082, 552), (1080, 451), (1107, 380), (1095, 300))), '#a7ab9e', 2)
            for branch in (((1097, 419), (1117, 387), (1143, 387), (1157, 351)),
                           ((1099, 385), (1087, 367), (1063, 357), (1048, 327))):
                line(draw, curve(branch), '#a7ab9e', 2)
            line(draw, curve(((1048, 327), (1008, 315), (1024, 267), (1077, 270))), '#a7ab9e', 2)
            line(draw, curve(((1077, 270), (1100, 216), (1157, 242), (1158, 276))), '#a7ab9e', 2)
            line(draw, curve(((1158, 276), (1212, 276), (1209, 344), (1157, 351))), '#a7ab9e', 2)
    elif location == 'walk':
        line(draw, curve(((87, 380), (228, 373), (353, 380), (469, 370))), '#d1d0c4', 2)
        line(draw, curve(((802, 373), (958, 376), (1073, 374), (1190, 381))), '#d1d0c4', 2)
        left = curve(((500, 370), (474, 420), (371, 496), (217, 591)))
        right = curve(((760, 370), (772, 426), (902, 519), (1097, 591)))
        draw.polygon(left + right[::-1], fill='#faf5ec')
        line(draw, left, '#c7bdad', 2)
        line(draw, right, '#c7bdad', 2)
        campus_tree(draw, 184, 492, 1.04)
        campus_tree(draw, 401, 398, .53)
        campus_tree(draw, 1086, 490, .94)
        campus_tree(draw, 877, 398, .48)
        for x, y, scale in ((122, 526, .55), (269, 495, .8), (350, 445, .45),
                            (460, 388, .3), (836, 402, .4), (979, 484, .52), (1153, 546, .75)):
            sprout(draw, x, y, scale)
        for x, y in ((127, 548), (253, 538), (342, 478), (930, 476), (1099, 524), (1157, 567)):
            line(draw, [(x, y), (x+21, y-1)], '#ddd7cb', 2)
    else:
        wall = '#b0b1a5'
        draw.polygon([(341, 223), (638, 147), (941, 223)], fill='#f3ebdc')
        line(draw, [(335, 224), (638, 147), (943, 223), (335, 224)], wall, 3)
        draw.rectangle((374, 227, 900, 445), fill='#fcf8ef', outline=wall, width=2)
        line(draw, [(389, 405), (887, 406)], '#dedbd0', 2)
        for x in (419, 482, 795, 858):
            line(draw, [(x, 246), (x - 2, 437)], wall, 2)
            line(draw, [(x + 10, 246), (x + 9, 437)], '#dedbd0', 2)
        draw.rectangle((570, 308, 707, 438), fill='#f1eee5', outline=wall, width=2)
        line(draw, [(638, 310), (638, 437)], wall, 2)
        for x in (623, 648):
            line(draw, [(x, 371), (x, 383)], wall, 2)
        draw.text((638, 269), '图 书 馆', font=SIGN, fill='#696f63', anchor='mm')
        for x1, x2, y in ((366, 909, 445), (335, 938, 472), (306, 969, 499), (273, 1002, 527)):
            line(draw, [(x1, y), (x2, y + 1)], wall, 2)
        line(draw, [(185, 565), (1080, 565)], '#c3c0b4', 2)
        for x, y, size in ((201, 561, .75), (260, 549, .55), (1050, 546, .8), (1110, 562, .55)):
            sprout(draw, x, y, size)
    return image


def remove_paper(image):
    pixels = np.asarray(image, dtype=np.float32)
    opacity = np.clip((253 - np.min(pixels, axis=2)) / 245, 0, 1)
    opacity = np.where(opacity < .032, 0, np.sqrt(opacity))
    rgb = np.clip((pixels - 255 * (1-opacity[..., None])) /
                  np.maximum(opacity[..., None], .001), 0, 255)
    return Image.fromarray(np.dstack((rgb, 255*opacity)).astype('uint8'))


def sprite_sheet():
    source = Image.open(SOURCE).convert('RGB')
    # Coordinates are measured on a proportional 979 by 650 review copy.
    coords = {
        'standing': (170, 18, 314, 309),
        'running': (608, 28, 816, 294),
        'cat': (168, 411, 341, 589),
        'feeding': (541, 365, 890, 604),
        'girl_feeding': (729, 376, 890, 604),
    }
    sprites = {}
    for key, box in coords.items():
        scaled_box = tuple(round(v * source.size[i % 2] / (979, 650)[i % 2])
                           for i, v in enumerate(box))
        # Remove the near-white paper while preserving antialiased ink edges.
        sprites[key] = remove_paper(source.crop(scaled_box))
    girl = sprites['girl_feeding']
    sx, sy = girl.width / 161, girl.height / 228
    # Keep her fingers while removing the shared bowl from the two-person pose.
    girl_mask = Image.new('L', girl.size, 255)
    ImageDraw.Draw(girl_mask).polygon([(round(x*sx), round(y*sy)) for x, y in
                                      [(0, 122), (13, 122), (17, 135), (12, 141),
                                       (6, 147), (8, 151), (0, 152)]], fill=0)
    girl.putalpha(ImageChops.multiply(girl.getchannel('A'), girl_mask))
    sprites['cat_facing_right'] = ImageOps.mirror(sprites['cat'])
    standing = sprites['standing']
    sx, sy = standing.width / 144, standing.height / 291
    arm_mask = Image.new('L', standing.size)
    ImageDraw.Draw(arm_mask).polygon([(round(x*sx), round(y*sy)) for x, y in
                                     [(86, 130), (94, 121), (94, 95), (127, 92),
                                      (128, 122), (96, 140), (88, 139)]], fill=255)
    alpha = standing.getchannel('A')
    arm = standing.copy()
    arm.putalpha(ImageChops.multiply(alpha, arm_mask))
    body = standing.copy()
    body_alpha = ImageChops.subtract(alpha, arm.getchannel('A'))
    ImageDraw.Draw(body_alpha).rectangle((round(125*sx), round(60*sy), standing.width,
                                          round(87*sy)), fill=0)
    body.putalpha(body_alpha)
    sprites['standing_body'] = body
    sprites['standing_arm'] = arm
    # The original run drawing supplies torso, face, scarf and arms. Legs are
    # drawn separately so ground contact alternates during the tracking shot.
    run = sprites['running']
    sprites['runner_top'] = run.crop((0, 0, run.width, round(run.height * 176/266)))
    walk_source = Image.open(WALK_SOURCE).convert('RGB')
    walk = walk_source.crop((0, 0, walk_source.width//2, walk_source.height))
    alternate = walk.copy()
    # Reverse just the lower-leg strides so the handclasp and heads stay fixed.
    for box in ((147, 356, 224, 543), (302, 393, 362, 544)):
        leg_box = tuple(round(v * walk_source.size[i % 2] / (979, 650)[i % 2])
                        for i, v in enumerate(box))
        legs = ImageOps.mirror(walk.crop(leg_box))
        mask = Image.new('L', legs.size, 255)
        draw = ImageDraw.Draw(mask)
        for row in range(24):
            draw.line((0, row, legs.width, row), fill=round(255*row/24))
        alternate.paste(legs, leg_box[:2], mask)
    walk_a = remove_paper(walk)
    walk_b = remove_paper(alternate)
    bbox = walk_a.getchannel('A').point(lambda a: 255 if a > 90 else 0).getbbox()
    sprites['walk_a'] = walk_a.crop(bbox)
    sprites['walk_b'] = walk_b.crop(bbox)
    return sprites


def place(frame, sprite, x, y, height, *, angle=0, opacity=1):
    pic = sprite.resize((max(1, round(sprite.width * height / sprite.height)),
                         max(1, round(height))), Image.Resampling.LANCZOS)
    if angle:
        pic = pic.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
    alpha = pic.getchannel('A')
    if opacity < 1:
        alpha = alpha.point(lambda a: round(a * opacity))
    frame.paste(pic, (round(x), round(y)), alpha)


def shine(draw, x, y, amount, color=GOLD):
    if amount <= 0:
        return
    for angle in (-.95, -.38, .2):
        dx, dy = math.cos(angle), math.sin(angle)
        line(draw, [(x+13*dx, y+13*dy), (x+(13+16*amount)*dx, y+(13+16*amount)*dy)], color, 3)


def standing_pose(art, degrees):
    body = art['standing_body'].copy()
    arm = art['standing_arm'].rotate(degrees, resample=Image.Resampling.BICUBIC,
                                    center=(body.width*87/144, body.height*134/291))
    body.alpha_composite(arm)
    return body


def runner(frame, art, t, duration):
    progress = min(1, t / duration)
    x = 103 + progress * 895
    phase = 2 * math.pi * 2.25 * t
    ground = 548
    hip_x = x + 114
    hip_y = ground - 94 - 8 * abs(math.sin(phase))
    draw = ImageDraw.Draw(frame)
    draw.ellipse((hip_x-86, ground-4, hip_x+58, ground+5), fill='#efebe3')
    for offset, color in ((math.pi, '#64605b'), (0, INK)):
        beat = phase+offset
        sweep = math.sin(beat)
        shoe_x = hip_x+63*sweep
        shoe_y = ground-7-39*max(0, math.cos(beat))
        knee_x = (hip_x+shoe_x)/2 + (30 if sweep < 0 else 10)
        knee_y = (hip_y+shoe_y)/2 + 8
        line(draw, [(hip_x, hip_y), (knee_x, knee_y), (shoe_x, shoe_y)], color, 5)
        draw.ellipse((shoe_x-9, shoe_y-3, shoe_x+14, shoe_y+7), fill=PAPER, outline=color, width=3)
    place(frame, art['runner_top'], x, hip_y-209, 216, angle=2*math.sin(phase))
    for i in range(3):
        trail = 15 + 15 * (math.sin(phase-i)+1)
        line(draw, [(x-22-trail, hip_y-70+i*19), (x-22, hip_y-72+i*19)], '#a3b0b9', 2)


def feed_at_library(frame, art, t):
    approach = ease(t / .68)
    draw = ImageDraw.Draw(frame)
    draw.ellipse((486, 555, 847, 565), fill='#efebe3')
    bowl_x = 631
    bowl_y = 484 + 2*math.sin(t*3)
    bowl = [(bowl_x-25, bowl_y), (bowl_x-17, bowl_y+12),
            (bowl_x-8, bowl_y+15), (bowl_x+13, bowl_y+15),
            (bowl_x+24, bowl_y+11), (bowl_x+29, bowl_y)]
    draw.polygon(bowl, fill='#e6ddd0')
    line(draw, bowl, INK, 2)
    draw.ellipse((bowl_x-25, bowl_y-6, bowl_x+29, bowl_y+3),
                 fill='#ba9675', outline=INK, width=2)
    for dx, dy in ((-14, -5), (-8, -7), (0, -8), (7, -7), (14, -6)):
        draw.ellipse((bowl_x+dx-3, bowl_y+dy-3, bowl_x+dx+3, bowl_y+dy+2),
                     fill='#a97b53', outline='#795c44')
    place(frame, art['girl_feeding'], 649, 337, 228, angle=.7*math.sin(t*3))
    place(frame, art['cat_facing_right'], 482+19*approach, 433+3*approach, 128,
          angle=-2+5*approach+.9*math.sin(t*6))


def walk_away(frame, art, t, duration):
    progress = ease(t/duration)
    phase = t*2.15
    stride = math.sin(phase*math.pi)
    feet_y = 548-129*progress-3*abs(stride)
    height = 312-107*progress
    center = 624+12*progress
    sprite = art['walk_a'] if stride >= 0 else art['walk_b']
    width = sprite.width*height/sprite.height
    draw = ImageDraw.Draw(frame)
    draw.ellipse((center-width*.46, feet_y-4, center+width*.46, feet_y+6),
                 fill='#efe7d9')
    place(frame, sprite, center-width/2, feet_y-height, height)


def render_frame(t, lengths, spoken, art, backgrounds):
    feed, run = lengths[1], lengths[3]
    starts = np.cumsum([0, *lengths]).tolist()
    idx = next((i for i in range(len(lengths)) if t < starts[i+1]), len(lengths))
    local = t-starts[idx]
    if idx in (0, 1):
        frame = backgrounds['campus'].copy()
        draw = ImageDraw.Draw(frame)
        boy_x, boy_y, boy_height = 320, 149, 412
        if idx == 0:
            intro = ease(local/.65)
            raise_phone = ease((local-.1)/.88)
            pose = standing_pose(art, -66*(1-raise_phone))
            place(frame, pose, boy_x, boy_y, boy_height, opacity=intro)
            if local > .55:
                draw.text((724, 265), '有一个大学生叫', font=HAND, fill=INK)
            if local > 1.32:
                draw.text((718, 311), '小帅', font=NAME, fill=BLUE)
                u = ease((local-1.32)/.48)
                line(draw, [(724, 408), (724+176*u, 397), (724+189*u, 401)], '#d6aa75', 4)
            notice = ease((local-.95)/.3)*ease((1.75-local)/.4)
            shine(draw, 492, 288, notice, BLUE)
        else:
            lean = ease((local-feed*.42)/.4)
            pose = standing_pose(art, 5*lean+4*math.sin(local*7)*math.exp(-local))
            place(frame, pose, boy_x, boy_y, boy_height)
            for i in range(2):
                pulse = max(0, 1-abs(local-(.38+i*.48))/.22)
                shine(draw, 492, 288, pulse, BLUE)
            if local > feed*.46:
                appear = ease((local-feed*.46)/.45)
                x = 802+22*(1-appear)
                draw.rounded_rectangle((x-85, 178, x+108, 363), radius=15,
                                       fill='#f9f1e3', outline='#967e65', width=2)
                place(frame, art['cat'], x-38, 209, 126, opacity=appear)
                line(draw, curve(((719, 288), (638, 284), (560, 284), (521, 301))), MUTED, 2)
                shine(draw, 903, 185, ease((local-feed*.55)/.30))
    elif idx == 2:
        frame = backgrounds['library'].copy()
        feed_at_library(frame, art, local)
    elif idx == 3:
        frame = backgrounds['path'].copy()
        runner(frame, art, local, run)
    elif idx == 4:
        frame = backgrounds['library'].copy()
        advance = ease(local/.67)
        draw = ImageDraw.Draw(frame)
        draw.ellipse((342, 576, 939, 593), fill='#eeeadf')
        place(frame, art['feeding'], 334, 169+6*(1-advance), 419,
              angle=.4*math.sin(local*2))
        cat_x = 619-26*advance
        place(frame, art['cat'], cat_x, 467-9*advance+1.4*math.sin(local*7), 124,
              angle=-9*advance+2.4*math.sin(local*3))
        shine(draw, 687, 505, max(0, math.sin(local*3.4))*.5)
    else:
        frame = backgrounds['walk'].copy()
        walk_away(frame, art, min(local, lengths[5]), lengths[5])

    draw = ImageDraw.Draw(frame)
    if idx < len(CAPTIONS) and (idx not in (2, 3) or local < spoken[idx]):
        draw.text((640, 653), CAPTIONS[idx], font=SUBTITLE, fill=INK, anchor='mm')
    return frame


def media_duration(ffmpeg, path):
    process = subprocess.run([ffmpeg, '-hide_banner', '-i', str(path)],
                             capture_output=True, text=True, encoding='utf-8', errors='replace')
    match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', process.stderr)
    if not match:
        raise ValueError(f'Cannot read duration from {path.name}')
    h, m, s = map(float, match.groups())
    return h*3600 + m*60 + s


def make_bed(path, lengths):
    rate = 48000
    duration = sum(lengths)+.35
    signal = np.zeros(round(duration*rate), dtype='float32')

    def pluck(start, hz, volume, seconds, decay):
        t = np.arange(round(rate*seconds))/rate
        env = np.minimum(1, t/.014)*np.exp(-t*decay)*np.minimum(1, (seconds-t)/.05)
        voice = (np.sin(2*np.pi*hz*t)+.26*np.sin(4*np.pi*hz*t))*env*volume
        first = round(start*rate)
        length = min(len(voice), len(signal)-first)
        signal[first:first+length] += voice[:length]

    melody = (261.63, 329.63, 392, 440, 392, 329.63, 293.66, 392)
    for i, t in enumerate(np.arange(.12, duration-.2, .53)):
        pluck(t, melody[i % len(melody)], .016, .63, 5)
        if i % 4 == 0:
            pluck(t, 130.81 if i % 8 == 0 else 146.83, .009, 1.05, 3)
    pluck(lengths[0]+lengths[1]*.51, 783.99, .043, .32, 10)
    run_start = sum(lengths[:3])
    feeding_start = sum(lengths[:4])
    ending_start = sum(lengths[:5])
    for t in np.arange(run_start+.1, feeding_start-.06, .23):
        pluck(t, 88, .021, .09, 32)
    pluck(ending_start+.14, 523.25, .026, .7, 5)
    pluck(ending_start+.29, 659.25, .022, .7, 5)
    # Duck music and footsteps while the short running line is delivered.
    run_samples = np.arange(round(run_start*rate), round((run_start+lengths[3])*rate))
    relative = run_samples/rate-run_start
    signal[run_samples] *= 1-.65*np.minimum(1, np.maximum(0, (lengths[3]-relative)/.25))
    signal *= np.minimum(1, np.arange(len(signal))[::-1]/(rate*.28))
    with wave.open(str(path), 'wb') as out:
        out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        out.writeframes(np.asarray(np.clip(signal, -1, 1)*32767, dtype='<i2').tobytes())


def timestamp(seconds):
    ms = round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--draft', action='store_true', help='Visual timing placeholder without narration')
    parser.add_argument('--stills', action='store_true')
    args = parser.parse_args()
    paths = [next(iter(sorted((ROOT/'audio').glob(f'{name}.*'))), None) for name in CLIPS]
    if args.draft:
        spoken = [4.8, 4.5, 2.42, 1.63, 2.04, 3.46]
    else:
        if any(path is None for path in paths):
            parser.error(f'Place the Doubao clips in audio/ using names {", ".join(CLIPS)}.')
        spoken = [media_duration(args.ffmpeg, path) for path in paths]
    pads = [.22, .20, .12, .20, .22, .65]
    lengths = [math.ceil((voice+pad)*FPS)/FPS for voice, pad in zip(spoken, pads)]
    # Keep the established running speed and tail after the spoken sentence.
    lengths[3] = max(lengths[3], 48 / FPS)
    duration = sum(lengths)+.35
    art = sprite_sheet()
    backgrounds = {name: background(name) for name in ('campus', 'path', 'library', 'walk')}
    output = ROOT/'output'
    output.mkdir(exist_ok=True)
    if args.stills:
        marks = [lengths[0]*.7, lengths[0]+lengths[1]*.8, sum(lengths[:2])+.6,
                 sum(lengths[:3])+.6, sum(lengths[:4])+1.3, sum(lengths[:5])+1.6]
        sheet = Image.new('RGB', (960, 810), PAPER)
        for i, t in enumerate(marks):
            image = render_frame(t, lengths, spoken, art, backgrounds)
            image.save(output/f'frame-{i+1}.jpg', quality=92)
            sheet.paste(image.resize((480, 270), Image.Resampling.LANCZOS), ((i%2)*480,(i//2)*270))
        sheet.save(output/'storyboard.jpg', quality=92)
        return

    make_bed(output/'sound-bed.wav', lengths)
    command = [args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-y',
               '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}',
               '-r', str(FPS), '-i', '-', '-i', str(output/'sound-bed.wav')]
    if args.draft:
        title = '第一段-画面预览-无旁白.mp4'
        command += ['-map', '0:v', '-map', '1:a']
    else:
        title = '第一段-偶遇广场-更新跑步台词.mp4'
        for path in paths:
            command += ['-i', str(path)]
        filters = [f'[{i+2}:a]aresample=48000,aformat=channel_layouts=mono,'
                   f'volume={1.5 if CLIPS[i] == "run" else 1},'
                   f'apad,atrim=0:{length:.6f}[v{i}]' for i, length in enumerate(lengths)]
        voice_inputs = ''.join(f'[v{i}]' for i in range(len(CLIPS)))
        filters += [f'{voice_inputs}concat=n={len(CLIPS)}:v=0:a=1,volume=1.15[n]',
                    '[1:a][n]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93[a]']
        command += ['-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[a]']
    command += ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(output/title)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for i in range(round(duration*FPS)):
            frame = render_frame(i/FPS, lengths, spoken, art, backgrounds)
            encoder.stdin.write(frame.tobytes())
        encoder.stdin.close()
        if encoder.wait() != 0:
            raise RuntimeError('FFmpeg render failed')
    starts = np.cumsum([0, *lengths]).tolist()
    srt = '\n\n'.join(f'{i+1}\n{timestamp(starts[i])} --> {timestamp(starts[i]+spoken[i])}\n{line}'
                     for i, line in enumerate(CAPTIONS))
    (output / Path(title).with_suffix('.srt')).write_text(srt+'\n', encoding='utf-8-sig')
    print(f'{output/title} — {duration:.2f}s')


if __name__ == '__main__':
    main()
