#!/usr/bin/env python3
"""지점별 사진 검토용 HTML 생성 (브라우저에서 열어 보고 걸러내기)"""
import os, json

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'google-maps-photos')

LABEL = {
    '00_공용_전지점': '공용 · 전 지점',
    '01_Videre': 'Booth 01 · Vidēre (Nivel 2)',
    '02_Tikal_Futura': 'Booth 02 · Planeta Maya, Tikal Futura',
    '03_AVIA': 'Booth 03 · AVIA (Nivel 3)',
    '04_Majadas_Once': 'Booth 04 · Majadas Once (Nivel 2)',
    '05_Pradera_Concepcion': 'Booth 05 · Pradera Concepción (팝업 ~10.31)',
}
SUBNOTE = {
    '_홍보그래픽': '텍스트 위주 홍보물 — 구글에서 노출이 낮거나 거부될 수 있음. 필요할 때만 골라 쓰기.',
    '_제외_단색카드': '로고만 있는 단색 이미지 — 업로드 비추천.',
}

CSS = """
body{font-family:system-ui,'Malgun Gothic',sans-serif;margin:0;background:#f5f5f5;color:#111}
header{position:sticky;top:0;background:#ce1212;color:#fff;padding:14px 22px;z-index:10}
header h1{margin:0;font-size:18px}
header p{margin:4px 0 0;font-size:13px;opacity:.9}
nav{background:#111;padding:8px 22px;position:sticky;top:60px;z-index:9}
nav a{color:#fff;text-decoration:none;font-size:13px;margin-right:16px;opacity:.8}
nav a:hover{opacity:1;text-decoration:underline}
section{padding:22px}
h2{font-size:17px;margin:0 0 4px;border-left:5px solid #ce1212;padding-left:9px}
.meta{font-size:13px;color:#666;margin:0 0 12px}
.sub{background:#fff8d6;border:1px solid #e8d98a;padding:8px 11px;border-radius:5px;
  font-size:12.5px;margin:14px 0 10px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:9px}
.c{background:#fff;border-radius:5px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.14)}
.c img{width:100%;aspect-ratio:1;object-fit:cover;display:block;cursor:pointer}
.c .n{font-size:10.5px;padding:4px 6px;color:#666;font-family:ui-monospace,monospace}
"""


def cards(folder, files):
    out = ['<div class="g">']
    for f in files:
        rel = f'{folder}/{f}'.replace('\\', '/')
        out.append(f'<div class="c"><a href="{rel}" target="_blank">'
                   f'<img loading="lazy" src="{rel}"></a><div class="n">{f[:14]}</div></div>')
    out.append('</div>')
    return ''.join(out)


def main():
    tops = sorted(d for d in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, d)))
    html = ['<!doctype html><meta charset="utf-8"><title>Fotopop · 구글맵 사진 정리</title>',
            f'<style>{CSS}</style>',
            '<header><h1>Fotopop — 구글 비즈니스 프로필 사진</h1>',
            '<p>지점별로 분류했어. 마음에 안 드는 건 해당 폴더에서 파일만 지우고 업로드하면 돼.</p></header>',
            '<nav>' + ''.join(
                f'<a href="#{t}">{LABEL.get(t, t)}</a>' for t in tops) + '</nav>']

    for t in tops:
        p = os.path.join(OUT, t)
        main_files = sorted(f for f in os.listdir(p) if f.endswith('.jpg'))
        subs = sorted(d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d)))
        html.append(f'<section id="{t}"><h2>{LABEL.get(t, t)}</h2>')
        html.append(f'<p class="meta">업로드 추천 <b>{len(main_files)}장</b>'
                    f' · 폴더명 <code>{t}</code></p>')
        html.append(cards(t, main_files))
        for sd in subs:
            sf = sorted(f for f in os.listdir(os.path.join(p, sd)) if f.endswith('.jpg'))
            if not sf:
                continue
            html.append(f'<div class="sub"><b>{sd}</b> ({len(sf)}장) — {SUBNOTE.get(sd, "")}</div>')
            html.append(cards(f'{t}/{sd}', sf))
        html.append('</section>')

    with open(os.path.join(OUT, '_사진보기.html'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    print('생성:', os.path.join(OUT, '_사진보기.html'))


if __name__ == '__main__':
    main()
