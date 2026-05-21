/**
 * blogs-data.js — Dynamic Blog Registry
 *
 * Each blog profile has its own folder under frontend/blogs/{profile}/.
 * The frontend fetches the active blog config, then loads articles from
 * the correct profile folder.
 *
 * articles.json entry shape:
 * {
 *   id: "guides/optimize-mount-and-blade-gameplay.md",  ← relative path from profile root
 *   category: "guides",
 *   title: "...",
 *   description: "...",
 *   date: "YYYY-MM-DD",
 *   tags: ["guides"],
 *   readTime: "6 min",
 *   file: "guides/optimize-mount-and-blade-gameplay.md",
 *   blog: "mount-and-blade",
 *   blogLabel: "Mount And Blade Blog"
 * }
 */

const R2_PUBLIC_URL = (typeof window !== 'undefined' && window.CONFIG && window.CONFIG.R2_PUBLIC_URL)
  ? window.CONFIG.R2_PUBLIC_URL
  : '';

const BASE_URL = R2_PUBLIC_URL || '';

/* ── Blog Config ──────────────────────────────────────── */
let _blogConfig = null;

async function loadBlogConfig() {
  if (_blogConfig) return _blogConfig;

  try {
    const localConfig = document.querySelector('[data-blog-config]');
    if (localConfig) {
      _blogConfig = JSON.parse(localConfig.getAttribute('data-blog-config'));
      return _blogConfig;
    }
    const res = await fetch(`${BASE_URL}/_blog_config.json`);
    if (res.ok) {
      const data = await res.json();
      _blogConfig = {
        profile: data.profile || 'ml-blog',
        label: data.label || 'Machine Learning Blog',
      };
    }
  } catch (_) {
    _blogConfig = { profile: 'ml-blog', label: 'Machine Learning Blog' };
  }
  return _blogConfig;
}

/* ── Category Metadata ─────────────────────────────────── */
const CATEGORY_META = {
  ml: {
    label: 'Machine Learning', shortLabel: 'ML',
    description: 'Algorithms, theory, and applied ML from fundamentals to production.',
    icon: '🧠', color: '#7c6af7', bgColor: 'rgba(124, 106, 247, 0.12)',
  },
  dl: {
    label: 'Deep Learning', shortLabel: 'DL',
    description: 'Neural networks, architectures, training tricks, and modern DL research.',
    icon: '🔬', color: '#4fc8b8', bgColor: 'rgba(79, 200, 184, 0.12)',
  },
  nlp: {
    label: 'Natural Language Processing', shortLabel: 'NLP',
    description: 'Text processing, transformers, LLMs, and language understanding.',
    icon: '📝', color: '#e879a0', bgColor: 'rgba(232, 121, 160, 0.12)',
  },
  cv: {
    label: 'Computer Vision', shortLabel: 'CV',
    description: 'Image processing, object detection, segmentation, and visual AI.',
    icon: '👁️', color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.12)',
  },
  genai: {
    label: 'Generative AI', shortLabel: 'Gen AI',
    description: 'Diffusion models, LLMs, RAG, agents, and the frontier of AI generation.',
    icon: '✨', color: '#a78bfa', bgColor: 'rgba(167, 139, 250, 0.12)',
  },
  ainews: {
    label: 'AI News', shortLabel: 'AI News',
    description: 'Breaking developments, model releases, and industry analysis.',
    icon: '📡', color: '#34d399', bgColor: 'rgba(52, 211, 153, 0.12)',
  },
  statistics: {
    label: 'Statistics for AI', shortLabel: 'Stats',
    description: 'Probability, statistical tests, distributions, and the math behind ML.',
    icon: '📊', color: '#fb923c', bgColor: 'rgba(251, 146, 60, 0.12)',
  },
  guides: {
    label: 'Game Guides', shortLabel: 'Guides',
    description: 'Tips, strategies, and guides for Mount & Blade games.',
    icon: '🎮', color: '#e74c3c', bgColor: 'rgba(231, 76, 60, 0.12)',
  },
  combat: {
    label: 'Combat', shortLabel: 'Combat',
    description: 'Combat tips and strategies for Mount & Blade.',
    icon: '⚔️', color: '#c0392b', bgColor: 'rgba(192, 57, 43, 0.12)',
  },
  mods: {
    label: 'Modding', shortLabel: 'Mods',
    description: 'Modding guides and community mods for Mount & Blade.',
    icon: '🛠️', color: '#8e44ad', bgColor: 'rgba(142, 68, 173, 0.12)',
  },
  multiplayer: {
    label: 'Multiplayer', shortLabel: 'MP',
    description: 'Multiplayer guides and server info for Mount & Blade.',
    icon: '🌐', color: '#2980b9', bgColor: 'rgba(41, 128, 185, 0.12)',
  },
  faction: {
    label: 'Faction Guides', shortLabel: 'Factions',
    description: 'Faction strategies and lore for Mount & Blade.',
    icon: '🏰', color: '#27ae60', bgColor: 'rgba(39, 174, 96, 0.12)',
  },
  builds: {
    label: 'Character Builds', shortLabel: 'Builds',
    description: 'Character builds and perk guides for Mount & Blade.',
    icon: '📋', color: '#f39c12', bgColor: 'rgba(243, 156, 18, 0.12)',
  },
  recipes: {
    label: 'Recipes', shortLabel: 'Recipes',
    description: 'Delicious recipes and cooking guides.',
    icon: '🍳', color: '#e67e22', bgColor: 'rgba(230, 126, 34, 0.12)',
  },
  techniques: {
    label: 'Cooking Techniques', shortLabel: 'Techniques',
    description: 'Master cooking techniques step by step.',
    icon: '🔪', color: '#d35400', bgColor: 'rgba(211, 84, 0, 0.12)',
  },
  equipment: {
    label: 'Kitchen Equipment', shortLabel: 'Gear',
    description: 'Reviews and guides for kitchen equipment.',
    icon: '🍽️', color: '#95a5a6', bgColor: 'rgba(149, 165, 166, 0.12)',
  },
  investing: {
    label: 'Investing', shortLabel: 'Investing',
    description: 'Investment strategies and financial advice.',
    icon: '📈', color: '#27ae60', bgColor: 'rgba(39, 174, 96, 0.12)',
  },
  budgeting: {
    label: 'Budgeting', shortLabel: 'Budget',
    description: 'Budget tips and money management guides.',
    icon: '💰', color: '#8e44ad', bgColor: 'rgba(142, 68, 173, 0.12)',
  },
  crypto: {
    label: 'Cryptocurrency', shortLabel: 'Crypto',
    description: 'Crypto news, guides, and analysis.',
    icon: '₿', color: '#f39c12', bgColor: 'rgba(243, 156, 18, 0.12)',
  },
};

const ALL_CATEGORIES = ['ml', 'dl', 'nlp', 'cv', 'genai', 'ainews', 'statistics'];

/* ── Cache ─────────────────────────────────────────────── */
const _cache = {};

/* ── Core Fetch ────────────────────────────────────────── */
async function loadCategoryArticles(cat) {
  if (_cache[cat] !== undefined) return _cache[cat];

  const config = await loadBlogConfig();
  const baseUrl = `${R2_PUBLIC_URL}/blogs/${config.profile}`;

  try {
    const res = await fetch(`${baseUrl}/${cat}/articles.json`);
    if (!res.ok) {
      _cache[cat] = [];
      return [];
    }
    const data = await res.json();
    _cache[cat] = Array.isArray(data) ? data : [];
    return _cache[cat];
  } catch (_) {
    _cache[cat] = [];
    return [];
  }
}

async function getBlogsByCategory(cat, sort = 'newest') {
  const articles = await loadCategoryArticles(cat);
  const sorted = [...articles].sort((a, b) =>
    sort === 'newest'
      ? new Date(b.date) - new Date(a.date)
      : new Date(a.date) - new Date(b.date)
  );
  return sorted;
}

async function getBlogById(id) {
  const config = await loadBlogConfig();
  const baseUrl = `${R2_PUBLIC_URL}/blogs/${config.profile}`;

  const parts = id.split('/');
  if (parts.length >= 2) {
    const cat = parts[0];
    const articles = await loadCategoryArticles(cat);
    const found = articles.find(a => a.id === id || a.file === id);
    if (found) return found;
  }

  for (const cat of Object.keys(CATEGORY_META)) {
    const articles = await loadCategoryArticles(cat);
    const found = articles.find(a => a.id === id || a.file === id);
    if (found) return found;
  }
  return null;
}

async function getRecentBlogs(n = 6) {
  const config = await loadBlogConfig();
  const cats = config.profile === 'ml-blog'
    ? ALL_CATEGORIES
    : Object.keys(CATEGORY_META);

  const all = await Promise.all(cats.map(loadCategoryArticles));
  const flat = all.flat();
  flat.sort((a, b) => new Date(b.date) - new Date(a.date));
  return flat.slice(0, n);
}

async function getTotalCount() {
  const config = await loadBlogConfig();
  const cats = config.profile === 'ml-blog'
    ? ALL_CATEGORIES
    : Object.keys(CATEGORY_META);

  const all = await Promise.all(cats.map(loadCategoryArticles));
  return all.reduce((sum, arr) => sum + arr.length, 0);
}

async function getBlogInfo() {
  return loadBlogConfig();
}

/* ── Formatting ─────────────────────────────────────────── */
function formatDate(dateStr) {
  if (!dateStr) return '';
  const [y, m, d] = dateStr.split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
}