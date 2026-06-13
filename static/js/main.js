
// ─── Theme Toggle ───────────────────────────
const html = document.documentElement;
const themeBtn = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('theme') || 'light';
html.setAttribute('data-theme', savedTheme);
updateThemeBtn(savedTheme);

if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    const cur = html.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeBtn(next);
  });
}
function updateThemeBtn(t) {
  if (themeBtn) themeBtn.textContent = t === 'dark' ? '☀' : '☾';
}

// ─── Mobile Menu ────────────────────────────
const mobileBtn = document.getElementById('mobileMenuBtn');
const mobileNav = document.getElementById('mobileNav');
if (mobileBtn && mobileNav) {
  mobileBtn.addEventListener('click', () => {
    mobileNav.classList.toggle('open');
    mobileBtn.textContent = mobileNav.classList.contains('open') ? '✕' : '☰';
  });
  // Close on outside click
  document.addEventListener('click', e => {
    if (!mobileBtn.contains(e.target) && !mobileNav.contains(e.target)) {
      mobileNav.classList.remove('open');
      mobileBtn.textContent = '☰';
    }
  });
}

// ─── Hero Slider ────────────────────────────
const sliderTrack = document.getElementById('sliderTrack');
const sliderPrev  = document.getElementById('sliderPrev');
const sliderNext  = document.getElementById('sliderNext');
const dots = document.querySelectorAll('.dot');
let currentSlide = 0;
let totalSlides = 0;
let sliderTimer;

if (sliderTrack) {
  totalSlides = sliderTrack.children.length;

  function goToSlide(n) {
    currentSlide = ((n % totalSlides) + totalSlides) % totalSlides;
    sliderTrack.style.transform = `translateX(${currentSlide * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === currentSlide));
  }
  function startAutoplay() {
    clearInterval(sliderTimer);
    sliderTimer = setInterval(() => goToSlide(currentSlide + 1), 5500);
  }

  sliderPrev && sliderPrev.addEventListener('click', () => { goToSlide(currentSlide - 1); startAutoplay(); });
  sliderNext && sliderNext.addEventListener('click', () => { goToSlide(currentSlide + 1); startAutoplay(); });
  dots.forEach((dot, i) => dot.addEventListener('click', () => { goToSlide(i); startAutoplay(); }));

  // Touch swipe
  let tx = 0;
  sliderTrack.addEventListener('touchstart', e => tx = e.touches[0].clientX, { passive: true });
  sliderTrack.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 45) { goToSlide(dx > 0 ? currentSlide - 1 : currentSlide + 1); startAutoplay(); }
  }, { passive: true });

  goToSlide(0);
  startAutoplay();
}

// ─── Navbar scroll effect ───────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (navbar) navbar.style.boxShadow = window.scrollY > 8 ? '0 4px 20px rgba(0,0,0,.15)' : '';
}, { passive: true });

// ─── Reading Progress Bar ───────────────────
const articleBody = document.getElementById('articleBody');
if (articleBody) {
  const bar = document.createElement('div');
  bar.id = 'readingProgress';
  document.body.prepend(bar);
  window.addEventListener('scroll', () => {
    const { top, height } = articleBody.getBoundingClientRect();
    const viewH = window.innerHeight;
    const total = height + top - viewH;
    const progress = Math.min(Math.max(-top / total, 0), 1);
    bar.style.transform = `scaleX(${progress})`;
  }, { passive: true });
}

// ─── Auto-dismiss flash messages ────────────
document.querySelectorAll('.flash').forEach(el => {
  el.style.transition = 'opacity .35s ease, transform .35s ease';
  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(-10px)';
    setTimeout(() => el.remove(), 380);
  }, 4800);
});

// ─── Scroll-reveal for cards ────────────────
if ('IntersectionObserver' in window) {
  const cards = document.querySelectorAll('.article-card, .stat-card, .sidebar-section');
  const cardObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        cardObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });
  cards.forEach(c => {
    c.style.opacity = '0.01';
    cardObs.observe(c);
  });
}

// ─── Active category link highlight ─────────
const currentPath = window.location.pathname;
document.querySelectorAll('.cat-link, .admin-nav-link').forEach(link => {
  if (link.getAttribute('href') === currentPath) link.classList.add('active');
});

// ─── Confirm delete forms ───────────────────
document.querySelectorAll('form[data-confirm]').forEach(form => {
  form.addEventListener('submit', e => {
    if (!confirm(form.dataset.confirm)) e.preventDefault();
  });
});

// ─── Back to top ────────────────────────────
const backTop = document.createElement('button');
backTop.innerHTML = '⤊';
backTop.setAttribute('aria-label', 'العودة للأعلى');
backTop.style.cssText = `
  position:fixed; bottom:1.5rem; left:1.5rem; width:44px; height:44px;
  background:var(--primary); color:#fff; border:none; border-radius:50%;
  font-size:1.2rem; cursor:pointer; box-shadow:0 4px 16px rgba(230,57,70,.4);
  opacity:0; transform:translateY(10px); transition:all .3s;
  display:flex; align-items:center; justify-content:center; z-index:999;
`;
document.body.appendChild(backTop);
window.addEventListener('scroll', () => {
  const show = window.scrollY > 400;
  backTop.style.opacity = show ? '1' : '0';
  backTop.style.transform = show ? 'translateY(0)' : 'translateY(10px)';
}, { passive: true });
backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
