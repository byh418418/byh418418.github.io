# FOTOPOP 웹사이트

인스타그램 데이터 기반 매거진/룩북 스타일 포트폴리오 사이트.

## 구성
```
index.html        ← 메인 페이지 (전부 여기 들어있음)
posts-data.js     ← 인스타 게시물 데이터 (캡션/이미지/위치)
images/           ← 원본 이미지 (모달 확대용)
images/thumb/     ← 썸네일 (갤러리 로딩 빠르게)
fonts/            ← Aileron 폰트 넣는 자리 (아래 참고)
```

## 브랜드 가이드 적용 ✅
- **컬러**: 메인 = Pop Red `#ce1212` / Lens Black / Paper White / 배경 Shell Grey `#efefef`. 부스 컬러로만 Soda Blue `#0047ab`, Pink 사용.
- **폰트**: 제목·로고·슬로건 = **Archivo Black** (Google Fonts, 자동 로드) / 본문·캡션 = **Aileron**.
- **로고**: Fotopop 워드마크.
- **부스 3곳**: 🔴 Red(1호점·Vidēre N2) · 🔵 Blue(2호점·CC Tikal Futura) · 🩷 Pink(3호점·AVIA N3).

## ⚠️ Aileron 폰트 넣기 (본문 폰트)
Aileron은 Google Fonts에 없어서 파일을 직접 넣어야 해. `fonts/` 폴더에 아래 3개를 넣어줘:
```
fonts/Aileron-Regular.woff2
fonts/Aileron-SemiBold.woff2
fonts/Aileron-Bold.woff2
```
> 파일이 없으면 자동으로 Helvetica/Arial로 표시돼서 사이트는 정상 작동해. 넣으면 Aileron으로 바뀜.
> (woff2가 없고 .ttf/.otf만 있으면 `index.html` 상단 `@font-face`의 `format('woff2')`와 파일명만 맞춰주면 돼.)

## 미리보기 (내 컴퓨터에서)
`index.html`을 더블클릭하면 브라우저에서 바로 열려.

## GitHub Pages 올리기 (무료 배포)

1. github.com 로그인 → 우측 상단 **+** → **New repository**
2. 이름 예: `fotopop` (Public 선택) → **Create repository**
3. 새 repo 화면에서 **uploading an existing file** 클릭
4. 이 폴더 안의 `index.html`, `posts-data.js`, `images` 폴더를 **통째로 드래그** 해서 업로드 → **Commit changes**
5. repo 상단 **Settings** → 왼쪽 **Pages**
6. **Source** 를 `Deploy from a branch`, Branch 를 `main` / `/(root)` 로 설정 → **Save**
7. 1~2분 뒤 `https://<내아이디>.github.io/fotopop/` 주소로 사이트 오픈 🎉

> 이미지가 많아서 업로드가 좀 걸릴 수 있어. 한 번에 다 안 올라가면 `images` 폴더만 따로 나눠서 올려도 돼.

## 콘텐츠 수정하기
- **글/캡션 고치기**: `posts-data.js` 에서 해당 게시물의 `"caption"` 텍스트만 수정
- **사진 교체**: `images/` 와 `images/thumb/` 에 같은 파일명으로 덮어쓰기
- **연락처/위치**: `index.html` 맨 아래 `contact` 섹션에서 수정
```
```
