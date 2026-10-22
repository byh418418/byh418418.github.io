/* jsdom으로 index.html을 실제 실행해 렌더링 + 모달 동작 검증 */
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs'), path = require('path');

// 저장소 루트 = 이 스크립트(_tools/)의 상위 폴더. 로컬·클라우드 어디서 clone해도 동작
const SITE = path.dirname(__dirname);
const errs = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

// HTMLMediaElement 스텁 (jsdom 미구현)
const dom = new JSDOM(fs.readFileSync(path.join(SITE, 'index.html'), 'utf8'), {
  runScripts: 'dangerously',
  resources: undefined,
  url: 'file://' + SITE + '/index.html',
  virtualConsole: vc,
  beforeParse(win) {
    win.HTMLMediaElement.prototype.play = function () { this.__played = true; return Promise.resolve(); };
    win.HTMLMediaElement.prototype.pause = function () { this.__played = false; };
    win.HTMLMediaElement.prototype.load = function () { };
    win.IntersectionObserver = class { constructor() { } observe() { } unobserve() { } disconnect() { } };
  },
});

const { window } = dom;
const doc = window.document;

// posts-data.js를 수동 주입 (jsdom이 외부 스크립트를 안 불러오므로)
const pd = fs.readFileSync(path.join(SITE, 'posts-data.js'), 'utf8');
window.eval(pd);
// 인라인 스크립트 재실행
const inline = [...fs.readFileSync(path.join(SITE, 'index.html'), 'utf8')
  .matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
window.eval(inline);

const POSTS = window.FOTOPOP_POSTS;
const check = (label, cond, extra = '') =>
  console.log((cond ? '  OK  ' : '  FAIL') + '  ' + label + (extra ? '  → ' + extra : ''));

console.log('=== 렌더링 ===');
const cells = doc.querySelectorAll('.grid .cell');
check(`피드 셀 ${cells.length}개 == 포스트 ${POSTS.length}개`, cells.length === POSTS.length);

const feats = doc.querySelectorAll('#features .feature');
check(`룩북 ${feats.length}개 == 6`, feats.length === 6);

const booths = doc.querySelectorAll('.booth-grid .booth');
check(`부스 카드 ${booths.length}개 == 5`, booths.length === 5);
check('부스 인덱스 라벨 5 Locations', doc.querySelector('.booths .idx').textContent.includes('5'));

const plays = doc.querySelectorAll('.grid .cell .play');
const nVid = POSTS.filter(p => p.videos && Object.keys(p.videos).length).length;
check(`재생 아이콘 ${plays.length}개 == 영상 포함 포스트 ${nVid}개`, plays.length === nVid);

const badges = doc.querySelectorAll('.grid .cell .badge');
const nReel = POSTS.filter(p => p.type === 'reel').length;
check(`REEL 배지 ${badges.length}개 == 릴스 ${nReel}개`, badges.length === nReel);

console.log('\n=== 모달: 이미지 포스트 ===');
const iImg = POSTS.findIndex(p => !p.videos || !Object.keys(p.videos).length);
window.openModal(iImg);
const mImg = doc.getElementById('mImg'), mVid = doc.getElementById('mVid');
check('모달 열림', doc.getElementById('modal').classList.contains('open'));
check('img 표시 / video 숨김', mImg.style.display !== 'none' && mVid.style.display === 'none');
check('img src 정상', mImg.getAttribute('src').startsWith('images/'), mImg.getAttribute('src'));

console.log('\n=== 모달: 릴스(영상) ===');
const iReel = POSTS.findIndex(p => p.type === 'reel');
window.openModal(iReel);
check('video 표시 / img 숨김', mVid.style.display === 'block' && mImg.style.display === 'none');
check('video src = images/video/', (mVid.getAttribute('src') || '').startsWith('images/video/'), mVid.getAttribute('src'));
check('poster 지정됨', !!mVid.getAttribute('poster'), mVid.getAttribute('poster'));
check('자동재생 시도됨', mVid.__played === true);

console.log('\n=== 모달: 영상+사진 혼합 캐러셀 ===');
const iMix = POSTS.findIndex(p => p.videos && Object.keys(p.videos).length && p.images.length > 1);
const pm = POSTS[iMix];
window.openModal(iMix);
let switched = { toVideo: 0, toImage: 0 };
for (let k = 0; k < pm.images.length; k++) {
  const file = pm.images[k];
  const isVid = !!pm.videos[file];
  const showingVid = mVid.style.display === 'block';
  if (isVid !== showingVid) console.log(`  FAIL  슬라이드 ${k} (${file}) 표시 불일치`);
  isVid ? switched.toVideo++ : switched.toImage++;
  doc.getElementById('mNext').click();
}
check(`혼합 캐러셀 ${pm.images.length}장 전환 (영상 ${switched.toVideo} / 사진 ${switched.toImage})`, true);

console.log('\n=== 영상 정지 처리 ===');
window.openModal(iReel);
window.closeModal();
check('닫을 때 재생 중지', mVid.__played === false);
check('닫을 때 src 해제', !mVid.getAttribute('src'));

console.log('\n=== 파일 존재 확인 ===');
let miss = [];
doc.querySelectorAll('img[src]').forEach(i => {
  const s = i.getAttribute('src');
  if (s && !s.startsWith('data:') && !fs.existsSync(path.join(SITE, s))) miss.push(s);
});
check(`DOM 내 <img> 경로 ${miss.length}개 누락`, miss.length === 0, miss.slice(0, 3).join(', '));

console.log('\n=== JS 에러 ===');
check(`에러 ${errs.length}건`, errs.length === 0, errs.slice(0, 3).join(' | '));
