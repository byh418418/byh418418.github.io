#!/usr/bin/env python3
"""Instagram export -> posts-data.js 병합 생성

- 기존 27개 항목은 캡션 수기 편집 가능성이 있으므로 그대로 보존
- 신규 포스트 / 릴스만 export에서 추출해 추가
- 전체를 게시 시각 내림차순 정렬
"""
import json, os, re, unicodedata, datetime

import glob as _glob

# 저장소 루트 = 이 스크립트(_tools/)의 상위 폴더. 로컬·클라우드 어디서 clone해도 동작
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_export():
    """인스타 export 폴더 탐색 (로컬에서 폴더를 연결했을 때만 존재)

    IG_EXPORT 환경변수로 직접 지정 가능 (export가 여러 개일 때 사용)
    """
    if os.environ.get('IG_EXPORT'):
        return os.path.abspath(os.environ['IG_EXPORT'])
    for pat in ('/sessions/*/mnt/instagram-*', os.path.join(SITE, '..', 'instagram-*')):
        hits = sorted(_glob.glob(pat))
        if hits:
            return os.path.abspath(hits[-1])
    raise SystemExit(
        '인스타 export 폴더를 못 찾음.\n'
        '  → 클라우드 모드에서는 불가능한 작업입니다.\n'
        '  → 로컬에서 export 폴더를 연결한 뒤 실행하세요.')


WORK = _find_export()
MEDIA = os.path.join(WORK, 'your_instagram_activity', 'media')



def fix(s):
    """인스타 export의 latin-1 mojibake 복원"""
    if not s:
        return ''
    try:
        return s.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def mid(uri):
    return os.path.basename(uri).rsplit('.', 1)[0]


# ── 제목 생성 (기존 데이터 스타일: 첫 줄, 장식 제거, 50자 + …) ──────────
EMOJI = re.compile(
    '[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF'
    '\U00002190-\U000021FF\U00002B00-\U00002BFF️‍]+')


def make_title(caption):
    line = caption.strip().split('\n')[0].strip()
    line = EMOJI.sub('', line).strip()
    line = line.strip('[]《》()<>').strip()
    line = re.sub(r'\s+', ' ', line)
    if len(line) > 50:
        line = line[:49].rstrip() + '…'
    return line or 'Fotopop'


# ── 위치 추출 ───────────────────────────────────────────────────────────
KNOWN = [
    ('Pradera Concepción', 'Pradera Concepción'),
    ('Cayalá', 'Cayalá'),
    ('Cayala', 'Cayalá'),
    ('Majadas Once', 'Majadas Once'),
    ('Planeta Maya', 'Planeta Maya'),
    ('Tikal Futura', 'Tikal Futura'),
    ('AVIA', 'AVIA'),
    ('Vidēre', 'Vidēre'),
    ('Videre', 'Vidēre'),
]


def make_location(caption):
    hits = []
    for needle, label in KNOWN:
        if needle.lower() in caption.lower() and label not in hits:
            hits.append(label)
    if not hits:
        return None
    return ' · '.join(hits[:2])


# ── 해시태그 ────────────────────────────────────────────────────────────
def make_tags(caption):
    return re.findall(r'#(\w+)', caption)[:6]


def caption_of(entry):
    return fix(entry.get('title') or (entry['media'][0].get('title') if entry.get('media') else '') or '')


def ts_of(entry):
    return entry.get('creation_timestamp') or entry['media'][0]['creation_timestamp']


def main():
    posts = json.load(open(os.path.join(MEDIA, 'posts_1.json'), encoding='utf-8'))
    reels = json.load(open(os.path.join(MEDIA, 'reels.json'), encoding='utf-8'))['ig_reels_media']

    # 9월 작업 직전 백업을 기준으로 병합 (재실행 가능하도록)
    base = os.path.join(SITE, '.backup-20261022', 'posts-data.js')
    src = open(base if os.path.exists(base) else os.path.join(SITE, 'posts-data.js'),
               encoding='utf-8').read()
    old = json.loads(src[src.index('['):src.rindex(']') + 1])
    old_ids = {i.rsplit('.', 1)[0] for p in old for i in p['images']}
    old_ids |= {v.rsplit('.', 1)[0] for p in old for v in p.get('videos', {}).values()}

    manifest = {'images': [], 'videos': []}
    seen_media = set()

    def add_media(uri):
        """manifest 등록 후 사이트에서 쓸 파일명 반환"""
        name = mid(uri)
        ext = os.path.splitext(uri)[1].lower()
        if name in seen_media:
            return name + ('.mp4' if ext == '.mp4' else '.jpg')
        seen_media.add(name)
        if ext == '.mp4':
            manifest['videos'].append({'uri': uri, 'name': name})
            return name + '.mp4'
        manifest['images'].append({'uri': uri, 'name': name + '.jpg'})
        return name + '.jpg'

    # ── 기존 항목: 타임스탬프만 export에서 찾아 붙임 ──────────────────
    ts_by_id = {}
    for e in posts + reels:
        for m in e['media']:
            ts_by_id[mid(m['uri'])] = ts_of(e)

    merged = []
    for p in old:
        t = max((ts_by_id.get(i.rsplit('.', 1)[0], 0) for i in p['images']), default=0)
        p.setdefault('type', 'post')
        p.setdefault('videos', {})
        merged.append((t, p))

    # ── 신규 포스트 ───────────────────────────────────────────────────
    n_new_post = 0
    for e in posts:
        ids = [mid(m['uri']) for m in e['media']]
        if any(i in old_ids for i in ids):
            continue
        n_new_post += 1
        cap = caption_of(e)
        files = [add_media(m['uri']) for m in e['media']]
        # 캐러셀 순서 유지: 영상은 포스터 jpg로 자리를 대신하고 videos 맵에 연결
        slides, videos = [], {}
        for f in files:
            if f.endswith('.mp4'):
                poster = f[:-4] + '.jpg'
                videos[poster] = f
                slides.append(poster)
            else:
                slides.append(f)
        merged.append((ts_of(e), {
            'title': make_title(cap),
            'caption': cap,
            'images': slides,
            'cover': slides[0] if slides else None,
            'location': make_location(cap),
            'tags': make_tags(cap),
            'type': 'post',
            'videos': videos,
        }))

    # ── 릴스 ──────────────────────────────────────────────────────────
    n_reel = 0
    for e in reels:
        ids = [mid(m['uri']) for m in e['media']]
        if any(i in old_ids for i in ids):
            continue
        n_reel += 1
        cap = caption_of(e)
        m = e['media'][0]
        vid = add_media(m['uri'])
        poster = vid[:-4] + '.jpg'
        merged.append((ts_of(e), {
            'title': make_title(cap),
            'caption': cap,
            'images': [poster],
            'cover': poster,
            'location': make_location(cap),
            'tags': make_tags(cap),
            'type': 'reel',
            'videos': {poster: vid},
        }))

    # ── 정렬 & 출력 ───────────────────────────────────────────────────
    merged.sort(key=lambda x: x[0], reverse=True)
    data = []
    for t, p in merged:
        p['date'] = datetime.date.fromtimestamp(t).isoformat() if t else None
        data.append(p)

    body = json.dumps(data, ensure_ascii=False, indent=1)
    with open(os.path.join(SITE, 'posts-data.js'), 'w', encoding='utf-8') as f:
        f.write('window.FOTOPOP_POSTS = ' + body + ';\n')

    with open(os.path.join(SITE, '_tools', 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print(f'기존 {len(old)} + 신규포스트 {n_new_post} + 릴스 {n_reel} = 총 {len(data)}개')
    print(f'manifest: 이미지 {len(manifest["images"])} / 영상 {len(manifest["videos"])}')


if __name__ == '__main__':
    main()
