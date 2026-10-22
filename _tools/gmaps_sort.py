#!/usr/bin/env python3
"""인스타 사진을 구글 비즈니스 프로필용 지점별 폴더로 분류 + 최적화"""
import json, os, re, shutil
from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, 'google-maps-photos')
LONG_EDGE = 1600
QUALITY = 86

STORES = [
    ('05_Pradera_Concepcion', ['pradera concepci', 'fotopop-up', 'primo de roma']),
    ('04_Majadas_Once',       ['majadas']),
    ('02_Tikal_Futura',       ['tikal futura', 'planeta maya']),
    ('03_AVIA',               ['avia']),
    ('01_Videre',             ['videre', 'vidēre']),
]
SHARED = '00_공용_전지점'
PROMO_SUB = '_홍보그래픽'
FLAT_SUB = '_제외_단색카드'
FLAT_EDGE = 1.5   # 이 값 미만이면 사실상 단색 브랜드 카드

# 홍보 그래픽 판별: 캡션이 오픈/이전/이벤트 고지성이거나 제목이 포스터형
PROMO_TITLE = re.compile(
    r'grand open|ya abierto|nos mudamos|loading|open soon|opening|giveaway|'
    r'sorteo|ganador|drop loading|día de|dia de|regalo|cupon|cupón|promo|'
    r'booth open|new drop|abre hoy|next week|guía rápida|guia rapida|'
    r'frame collection|próxima|proxima apertura',
    re.I)


def classify(post):
    """지점 키워드 매칭. 3곳 이상 언급된 브랜드 전체 공지는 공용 처리."""
    cap = post['caption'].lower()
    hits = [name for name, keys in STORES if any(k in cap for k in keys)]
    return [] if len(hits) >= 3 else hits


def is_promo(post):
    text = (post['title'] + ' ' + post['caption'][:300])
    return bool(PROMO_TITLE.search(text))


_flat_cache = {}


def is_flat(src):
    """로고만 박힌 단색 배경 카드인지 (엣지 밀도로 판정)"""
    if src in _flat_cache:
        return _flat_cache[src]
    import numpy as np
    a = np.asarray(Image.open(src).convert('L').resize((160, 160)), dtype=float)
    edge = (np.abs(np.diff(a, axis=1)).mean() + np.abs(np.diff(a, axis=0)).mean()) / 2
    _flat_cache[src] = edge < FLAT_EDGE
    return _flat_cache[src]


def save_optimized(src, dst):
    im = Image.open(src).convert('RGB')
    if max(im.size) > LONG_EDGE:
        im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return os.path.getsize(dst)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    s = open(os.path.join(SITE, 'posts-data.js'), encoding='utf-8').read()
    posts = json.loads(s[s.index('['):s.rindex(']') + 1])

    plan = {}          # folder -> list of (date, seq, srcfile, title)
    for p in posts:
        photos = [i for i in p['images'] if i not in p.get('videos', {})]
        if not photos:
            continue
        targets = classify(p) or [SHARED]
        promo = is_promo(p)
        for n, f in enumerate(photos, 1):
            if is_flat(os.path.join(SITE, 'images', f)):
                sub = FLAT_SUB
            elif promo:
                sub = PROMO_SUB
            else:
                sub = ''
            for t in targets:
                plan.setdefault(os.path.join(t, sub) if sub else t, []).append(
                    (p['date'], n, f, p['title']))

    report = {}
    for folder, items in sorted(plan.items()):
        d = os.path.join(OUT, folder)
        os.makedirs(d, exist_ok=True)
        items.sort(key=lambda x: (x[0] or '', x[1]), reverse=True)
        total = 0
        for idx, (date, n, f, title) in enumerate(items, 1):
            name = f'{idx:03d}_{date}_{n:02d}.jpg'
            total += save_optimized(os.path.join(SITE, 'images', f),
                                    os.path.join(d, name))
        report[folder] = {'count': len(items), 'mb': round(total / 1048576, 1)}
        print(f'{folder:38} {len(items):4}장  {report[folder]["mb"]:6.1f}MB')

    json.dump(report, open(os.path.join(OUT, '_report.json'), 'w'),
              ensure_ascii=False, indent=1)
    print('\n총', sum(v['count'] for v in report.values()), '장 /',
          round(sum(v['mb'] for v in report.values()), 1), 'MB')


if __name__ == '__main__':
    main()
