#!/usr/bin/env python3
"""Instagram export -> fotopop 사이트 미디어 배치 (이미지 리사이즈 + 썸네일)"""
import json, os, subprocess, sys

import glob as _glob
from PIL import Image, ImageOps

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

IMGD = os.path.join(SITE, 'images')
THMD = os.path.join(IMGD, 'thumb')
VIDD = os.path.join(IMGD, 'video')   # 영상은 images/video/ 아래
os.makedirs(THMD, exist_ok=True)
os.makedirs(VIDD, exist_ok=True)

FULL_MAX = 1920
THUMB_MAX = 800


def place_image(src, name):
    """원본(최대 1920) + 썸네일(최대 800) 생성. 이미 있으면 skip."""
    dst_full = os.path.join(IMGD, name)
    dst_thm = os.path.join(THMD, name)
    made = []
    if not os.path.exists(dst_full):
        im = Image.open(src)
        im = ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        im.save(dst_full, 'JPEG', quality=88, optimize=True, progressive=True)
        made.append('full')
    if not os.path.exists(dst_thm):
        im = Image.open(dst_full)
        im.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        im.save(dst_thm, 'JPEG', quality=82, optimize=True, progressive=True)
        made.append('thumb')
    return made


def place_video(src, name):
    """웹용 h264 mp4로 재인코딩 + 포스터 프레임 추출."""
    dst = os.path.join(VIDD, name + '.mp4')
    poster = name + '.jpg'
    dst_poster_full = os.path.join(IMGD, poster)
    dst_poster_thm = os.path.join(THMD, poster)

    if not os.path.exists(dst):
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-i', src,
            '-vf', "scale='min(720,iw)':-2",
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '28',
            '-profile:v', 'main', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '96k',
            '-movflags', '+faststart', dst
        ], check=True)

    if not os.path.exists(dst_poster_full):
        tmp = '/tmp/_poster.jpg'
        # 0.5초 지점 프레임 (첫 프레임이 검은 경우 방지)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0.5',
                        '-i', src, '-frames:v', '1', tmp], check=True)
        im = Image.open(tmp).convert('RGB')
        im.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        im.save(dst_poster_full, 'JPEG', quality=88, optimize=True, progressive=True)
    if not os.path.exists(dst_poster_thm):
        im = Image.open(dst_poster_full)
        im.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        im.save(dst_poster_thm, 'JPEG', quality=82, optimize=True, progressive=True)
    return poster


if __name__ == '__main__':
    manifest = json.load(open(os.path.join(SITE, '_tools', 'manifest.json'), encoding='utf-8'))
    n_img = n_vid = 0
    for item in manifest['images']:
        src = os.path.join(WORK, item['uri'])
        if place_image(src, item['name']):
            n_img += 1
            print('IMG', item['name'], flush=True)
    for item in manifest['videos']:
        src = os.path.join(WORK, item['uri'])
        place_video(src, item['name'])
        n_vid += 1
        print('VID', item['name'], flush=True)
    print(f'\n완료: 이미지 {n_img}개, 영상 {n_vid}개')
