# FOTOPOP 웹사이트

인스타그램 데이터 기반 매거진/룩북 스타일 포트폴리오 사이트.

## 구성
```
index.html        ← 메인 페이지 (전부 여기 들어있음)
posts-data.js     ← 인스타 게시물 데이터 (캡션/이미지/영상/위치/날짜)
images/           ← 원본 이미지 (모달 확대용, 최대 1920px)
images/thumb/     ← 썸네일 (갤러리 로딩 빠르게, 최대 800px)
images/video/     ← 릴스·동영상 (720p h264 mp4, 웹 스트리밍용)
fonts/            ← Aileron 폰트 넣는 자리 (아래 참고)
```

## posts-data.js 형식
```js
{
  "title":    "짧은 제목",
  "caption":  "인스타 캡션 원문",
  "images":   ["파일명.jpg", ...],   // 캐러셀 순서. 영상은 포스터 jpg가 자리를 차지
  "cover":    "대표.jpg",
  "location": "Majadas Once · Vidēre",
  "tags":     ["해시태그"],
  "type":     "post" | "reel",
  "videos":   { "포스터.jpg": "영상.mp4" },   // 비어있으면 사진만
  "date":     "2026-08-09"
}
```
> 모달은 슬라이드 파일명이 `videos`에 있으면 `<video>`로, 없으면 `<img>`로 렌더링해.

## 브랜드 가이드 적용 ✅
- **컬러**: 메인 = Pop Red `#ce1212` / Lens Black / Paper White / 배경 Shell Grey `#efefef`. 부스 컬러로만 Soda Blue `#0047ab`, Pink 사용.
- **폰트**: 제목·로고·슬로건 = **Archivo Black** (Google Fonts, 자동 로드) / 본문·캡션 = **Aileron**.
- **로고**: Fotopop 워드마크.
- **부스 5곳**: 🔴 Red(1호점·Vidēre N2) · 🔵 Blue(2호점·Planeta Maya, Tikal Futura) · 🩷 Pink(3호점·AVIA N3) · 🔴🔵 Red+Blue(4호점·Majadas Once N2) · 🩷 Pink(5호점·Pradera Concepción N1, 팝업 2026.08.01–10.31).
  > 팝업(5호점)은 10/31 종료 예정. 끝나면 `index.html`의 booths 섹션에서 카드 1개 지우고 `[ 5 Locations ]` → `[ 4 Locations ]`, contact 섹션 숫자도 같이 수정.

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
- **메인 대표작(Lookbook)**: `index.html` 의 `const LOOKBOOK = [...]` 에서 파일명 6개를 바꾸면 됨
- **연락처/위치**: `index.html` 맨 아래 `contact` 섹션에서 수정

## 인스타 새 게시물 반영하기
1. 인스타 → 계정 센터 → 내 정보 다운로드. **형식 JSON / 기간 전체 / 고화질**, 정보는 "콘텐츠"만 선택
2. 받은 zip 을 Claude 에게 주면 신규분만 골라 반영해줌 (기존 캡션 수정본은 보존됨)
3. 처리 내용: mojibake 인코딩 복원 → 이미지 리사이즈 + 썸네일 → 영상 720p 압축 + 포스터 추출 → `posts-data.js` 병합·정렬

> ⚠️ export zip 에는 DM·로그인 기록 등 개인정보가 함께 들어있음. **zip 자체를 repo 에 넣지 말 것.**
```
```
