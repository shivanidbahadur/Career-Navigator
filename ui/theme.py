"""
UI-only theme helpers for the AI Career Navigator.

This module is pure presentation: it injects a global "Aurora Glass" theme
with 3D effects (tilting glass cards, floating orbs, animated rings,
gradient shimmer text). It never reads or writes app logic / session data.
"""

import os
import re

import streamlit as st


def apply_theme():
    """Inject the global theme + ambient 3D background layer (once)."""

    st.markdown(
        """
        <style>
        /* ============ FONTS & ROOT ============ */
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');

        :root {
            --ink: #eef1ff;
            --ink-dim: #a5b0d6;
            --violet: #8b7bff;
            --cyan: #4fd1ff;
            --pink: #ff6ec7;
            --card: rgba(255, 255, 255, 0.045);
            --card-border: rgba(255, 255, 255, 0.10);
        }

        /* ============ APP BACKGROUND (aurora) ============ */
        html, body, .stApp {
            background: #070b1c !important;
            color: var(--ink) !important;
            font-family: 'Space Grotesk', 'Segoe UI', sans-serif !important;
        }

        .stApp {
            background:
                radial-gradient(1200px 700px at 85% -10%, rgba(124, 92, 255, .22), transparent 60%),
                radial-gradient(1000px 600px at -10% 30%, rgba(56, 199, 255, .14), transparent 55%),
                radial-gradient(900px 700px at 60% 110%, rgba(255, 90, 190, .12), transparent 55%),
                #070b1c !important;
            animation: auroraShift 18s ease-in-out infinite alternate;
        }

        @keyframes auroraShift {
            0%   { background-position: 0% 0%, 0% 0%, 0% 0%; }
            50%  { background-position: 3% 2%, -2% 3%, 2% -2%; }
            100% { background-position: -2% 3%, 3% -2%, -3% 2%; }
        }

        /* ============ AMBIENT 3D LAYER ============ */
        .fg-scene {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            perspective: 900px;
            overflow: hidden;
        }

        /* Floating glowing orbs */
        .fg-orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(46px);
            opacity: .5;
            will-change: transform;
        }
        .fg-orb.o1 { width: 380px; height: 380px; left: -90px;  top: -110px; background: radial-gradient(circle at 35% 35%, #7c5cff, transparent 68%); animation: float1 14s ease-in-out infinite; }
        .fg-orb.o2 { width: 300px; height: 300px; right: -70px; top: 22%;    background: radial-gradient(circle at 35% 35%, #37c8ff, transparent 68%); animation: float2 17s ease-in-out infinite; }
        .fg-orb.o3 { width: 340px; height: 340px; left: 32%;    bottom: -140px; background: radial-gradient(circle at 35% 35%, #ff5ab1, transparent 68%); animation: float3 20s ease-in-out infinite; }

        @keyframes float1 { 0%,100% { transform: translate3d(0,0,0) scale(1); } 50% { transform: translate3d(40px,26px,0) scale(1.07); } }
        @keyframes float2 { 0%,100% { transform: translate3d(0,0,0) scale(1); } 50% { transform: translate3d(-44px,34px,0) scale(0.94); } }
        @keyframes float3 { 0%,100% { transform: translate3d(0,0,0) scale(1); } 50% { transform: translate3d(26px,-40px,0) scale(1.05); } }

        /* Spinning 3D rings */
        .fg-ring {
            position: absolute;
            border-radius: 50%;
            border: 1.5px solid rgba(150, 130, 255, 0.16);
            transform: rotateX(72deg);
            will-change: transform;
        }
        .fg-ring.r1 { width: 560px; height: 560px; right: -180px; top: 6%;  animation: spinRing 26s linear infinite; }
        .fg-ring.r2 { width: 340px; height: 340px; left: -110px;  bottom: 4%; border-color: rgba(80, 205, 255, 0.14); animation: spinRing 34s linear infinite reverse; }

        @keyframes spinRing {
            from { transform: rotateX(72deg) rotateZ(0deg); }
            to   { transform: rotateX(72deg) rotateZ(360deg); }
        }

        /* Twinkling particles */
        .fg-star {
            position: absolute;
            width: 3px; height: 3px;
            border-radius: 50%;
            background: rgba(255,255,255,.85);
            box-shadow: 0 0 9px 2px rgba(160,140,255,.55);
            animation: twinkle 4s ease-in-out infinite;
        }
        @keyframes twinkle { 0%,100% { opacity: .15; } 50% { opacity: .95; } }

        /* ============ LIFT MAIN CONTENT ABOVE SCENE ============ */
        .stApp > div, section[data-testid="stSidebar"],
        div[data-testid="stAppViewContainer"] { position: relative; z-index: 1; }

        /* ============ SIDEBAR ============ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(13,18,46,.92), rgba(20,16,58,.94)) !important;
            border-right: 1px solid rgba(140,120,255,.18);
            backdrop-filter: blur(18px);
        }
        section[data-testid="stSidebar"] * { color: #e6e9ff !important; }
        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,.05);
            border: 1px solid rgba(255,255,255,.09);
            border-radius: 12px;
            color: #dfe4ff !important;
            transition: all .25s ease;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(139,123,255,.16);
            border-color: rgba(139,123,255,.55);
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(90,70,220,.25);
        }

        /* ============ HEADINGS / TEXT ============ */
        h1, h2, h3, .stApp h1, .stApp h2, .stApp h3 {
            font-family: 'Sora', 'Space Grotesk', sans-serif !important;
            color: #f4f5ff !important;
            letter-spacing: -.5px;
        }
        p, label, span, li { color: var(--ink-dim) !important; }

        .fg-gradient-text {
            background: linear-gradient(92deg, #a78bfa 0%, #63d3ff 50%, #ff8ad4 100%);
            background-size: 220% 100%;
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 7s ease-in-out infinite;
        }
        @keyframes shimmer { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }

        /* ============ 3D TILT GLASS CARDS ============ */
        .fg-tilt {
            position: relative;
            border-radius: 22px;
            padding: 24px;
            background: linear-gradient(150deg, rgba(255,255,255,.075), rgba(255,255,255,.03) 55%);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(14px);
            transform-style: preserve-3d;
            transform: perspective(800px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
            transition: transform .18s ease, box-shadow .25s ease, border-color .25s ease;
            box-shadow: 0 18px 44px rgba(4, 8, 30, .45);
            will-change: transform;
            overflow: hidden;
        }
        .fg-tilt::before {              /* glare highlight that follows the cursor */
            content: "";
            position: absolute;
            inset: -60%;
            background: radial-gradient(circle at var(--mx,50%) var(--my,50%),
                        rgba(255,255,255,.16), transparent 42%);
            opacity: 0;
            transition: opacity .25s ease;
            pointer-events: none;
        }
        .fg-tilt:hover {
            border-color: rgba(150,130,255,.45);
            box-shadow: 0 26px 60px rgba(80,60,220,.30), 0 0 0 1px rgba(150,130,255,.12) inset;
        }
        .fg-tilt:hover::before { opacity: 1; }

        /* ============ LINKED (CLICKABLE) CARDS ============ */
        .fg-card {
            display: block;
            color: inherit;
            text-decoration: none;
            border-radius: 22px;
            cursor: pointer;
        }
        .fg-card:link,
        .fg-card:visited,
        .fg-card:hover,
        .fg-card:active {
            color: inherit;
            text-decoration: none;
        }
        .fg-card:focus-visible {
            outline: 2px solid rgba(150, 130, 255, .8);
            outline-offset: 3px;
        }
        /* Arrow affordance so a card reads as something you can open. */
        .fg-card .fg-tilt::after {
            content: "\\2192";
            position: absolute;
            top: 20px;
            right: 24px;
            font-size: 17px;
            line-height: 1;
            color: rgba(196, 181, 253, .45);
            transition: transform .2s ease, color .2s ease;
        }
        .fg-card:hover .fg-tilt::after {
            color: #c4b5fd;
            transform: translateX(4px);
        }

        /* ============ TOOL STEP NAVIGATION (bottom of each tool) ============ */
        .fg-stepnav {
            margin: 36px 0 12px;
            padding: 18px 22px 20px;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(139,123,255,.12), rgba(79,209,255,.07));
            border: 1px solid rgba(150,130,255,.24);
            backdrop-filter: blur(10px);
        }
        .fg-stepnav-top {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .fg-stepnav-chip {
            font-size: 11.5px;
            letter-spacing: .16em;
            text-transform: uppercase;
            color: #c4b5fd;
            border: 1px solid rgba(150,130,255,.35);
            border-radius: 999px;
            padding: 4px 12px;
            white-space: nowrap;
        }
        .fg-stepnav-title {
            font-weight: 700;
            font-size: 15.5px;
            color: var(--ink);
        }
        .fg-stepnav-rail {
            height: 7px;
            border-radius: 999px;
            background: rgba(255,255,255,.08);
            overflow: hidden;
        }
        .fg-stepnav-rail span {
            display: block;
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--cyan), var(--violet), var(--pink));
            box-shadow: 0 0 18px rgba(139,123,255,.55);
            transition: width .5s ease;
        }

        .fg-pop { animation: popIn .55s cubic-bezier(.22,.9,.32,1.2) both; }
        @keyframes popIn {
            from { opacity: 0; transform: perspective(800px) translateY(22px) rotateX(7deg) scale(.97); }
            to   { opacity: 1; transform: perspective(800px) translateY(0) rotateX(0) scale(1); }
        }

        .fg-icon {
            width: 52px; height: 52px;
            display: flex; align-items: center; justify-content: center;
            font-size: 26px;
            border-radius: 16px;
            margin-bottom: 14px;
            background: linear-gradient(140deg, rgba(139,123,255,.28), rgba(79,209,255,.18));
            border: 1px solid rgba(160,140,255,.35);
            box-shadow: 0 10px 24px rgba(90,70,220,.35);
            transform: translateZ(38px);
            animation: bob 4.5s ease-in-out infinite;
        }
        @keyframes bob { 0%,100% { transform: translateZ(38px) translateY(0); } 50% { transform: translateZ(38px) translateY(-6px); } }

        .fg-title { font-family:'Sora',sans-serif; font-weight: 800; font-size: 16.5px; color: #f2f3ff !important; margin-bottom: 6px; transform: translateZ(26px); }
        .fg-text  { font-size: 13.5px; line-height: 1.55; color: #aab4da !important; transform: translateZ(18px); }

        /* ============ HERO ============ */
        .fg-hero {
            position: relative;
            border-radius: 30px;
            padding: 44px 46px;
            overflow: hidden;
            background:
                radial-gradient(600px 300px at 85% 0%, rgba(124,92,255,.22), transparent 60%),
                linear-gradient(140deg, rgba(20,26,64,.85), rgba(14,18,44,.82));
            border: 1px solid rgba(150,130,255,.22);
            box-shadow: 0 30px 80px rgba(3,6,26,.6), 0 1px 0 rgba(255,255,255,.06) inset;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .fg-hero .fg-eyebrow {
            display: inline-flex; align-items: center; gap: 8px;
            font-size: 13.5px; font-weight: 600; letter-spacing: 1.6px;
            text-transform: uppercase;
            color: #b9aaff !important;
            margin-bottom: 14px;
        }
        .fg-hero h1 {
            margin: 0;
            font-size: clamp(38px, 5vw, 64px);
            font-weight: 800;
            line-height: 1.04;
            letter-spacing: -2px;
            color: #ffffff !important;
        }
        .fg-hero p { margin: 16px 0 0; max-width: 700px; font-size: 16.5px; line-height: 1.7; color: #b3bde0 !important; }

        /* Animated entrance */
        .fg-rise { animation: riseIn .7s cubic-bezier(.2,.8,.25,1) both; }
        .fg-rise.d1 { animation-delay: .08s; } .fg-rise.d2 { animation-delay: .16s; } .fg-rise.d3 { animation-delay: .24s; }
        @keyframes riseIn { from { opacity: 0; transform: translateY(26px); } to { opacity: 1; transform: translateY(0); } }

        /* ============ SECTION TITLES ============ */
        .fg-section {
            display: flex; align-items: center; gap: 12px;
            margin: 30px 0 16px;
        }
        .fg-section .bar {
            width: 34px; height: 6px; border-radius: 99px;
            background: linear-gradient(90deg, #8b7bff, #4fd1ff);
            box-shadow: 0 0 14px rgba(120,100,255,.7);
        }
        .fg-section h2 { margin: 0; font-size: 22px; font-weight: 800; color: #eef0ff !important; }

        /* ============ STATUS / METRIC CARDS ============ */
        .fg-stat {
            padding: 22px;
            border-radius: 20px;
            background: linear-gradient(160deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
            border: 1px solid rgba(255,255,255,.10);
            backdrop-filter: blur(12px);
            transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
        }
        .fg-stat:hover {
            transform: translateY(-5px);
            border-color: rgba(150,130,255,.45);
            box-shadow: 0 18px 40px rgba(80,60,220,.28);
        }
        .fg-stat .lbl { font-size: 12.5px; letter-spacing: 1.2px; text-transform: uppercase; color: #8f9ac2 !important; }
        .fg-stat .val { margin-top: 8px; font-family: 'Sora', sans-serif; font-size: 21px; font-weight: 800; color: #f4f5ff !important; }

        /* ============ STREAMLIT WIDGETS ============ */
        .stButton > button, .stDownloadButton > button {
            border-radius: 13px;
            border: 1px solid rgba(150,130,255,.4);
            background: linear-gradient(140deg, rgba(139,123,255,.16), rgba(79,209,255,.10));
            color: #e8eaff !important;
            font-weight: 700;
            min-height: 46px;
            transition: all .22s ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            border-color: rgba(160,140,255,.85);
            box-shadow: 0 12px 28px rgba(90,70,220,.35);
        }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
        .stButton > button[data-testid="stBaseButton-primary"],
        .stDownloadButton > button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #6f5cf1, #3fb6ff);
            border: none;
            color: #fff !important;
            box-shadow: 0 12px 30px rgba(95,80,235,.45);
            text-shadow: 0 1px 2px rgba(10, 12, 40, .45);
        }
        /* Keep the label white all the way down the button's inner markup. */
        .stButton > button[kind="primary"] *,
        .stButton > button[data-testid="stBaseButton-primary"] *,
        .stDownloadButton > button[kind="primary"] *,
        .stDownloadButton > button[data-testid="stBaseButton-primary"] * {
            color: #fff !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(255,255,255,.04);
            border: 1px solid rgba(255,255,255,.10);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        div[data-testid="stExpander"] details { border: none !important; background: transparent !important; }

        div[data-testid="stForm"], div[data-testid="element-container"] .stForm {
            background: rgba(255,255,255,.035);
            border: 1px solid rgba(255,255,255,.09);
            border-radius: 20px;
            padding: 26px;
            backdrop-filter: blur(12px);
        }

        .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stMultiSelect div[data-baseweb="select"] > div,
        .stSelectbox div[data-baseweb="select"] > div {
            background: rgba(10,14,36,.6) !important;
            color: #eef1ff !important;
            border-color: rgba(255,255,255,.14) !important;
            border-radius: 12px !important;
        }
        .stMultiSelect span[data-baseweb="tag"] { background: rgba(139,123,255,.28) !important; color: #eef1ff !important; border-radius: 8px !important; }

        div[data-testid="stMetric"], [data-testid="stMetricValue"] {
            color: #f2f4ff !important;
        }
        [data-testid="stMetricLabel"] p { color: #99a3c9 !important; }

        .stTabs [data-baseweb="tab-list"] { gap: 6px; }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,.05);
            border-radius: 12px 12px 0 0;
            border: 1px solid rgba(255,255,255,.08);
            border-bottom: none;
            color: #c9d0ee !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(140deg, rgba(139,123,255,.25), rgba(79,209,255,.15)) !important;
            color: white !important;
            box-shadow: 0 -6px 18px rgba(90,70,220,.25);
        }

        hr { border-color: rgba(255,255,255,.10) !important; }
        div[data-testid="stProgress"] > div { background: rgba(255,255,255,.08); border-radius: 99px; }
        div[data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, #7c5cff, #37c8ff, #ff5ab1) !important;
            border-radius: 99px;
            animation: glowPulse 2.6s ease-in-out infinite;
        }
        @keyframes glowPulse { 0%,100% { filter: brightness(1); } 50% { filter: brightness(1.28); } }

        .stAlert, div[data-testid="stAlert"],
        div[data-testid="stAlert"] > div {
            background: rgba(139,123,255,.10) !important;
            border: 1px solid rgba(150,130,255,.28) !important;
            border-radius: 16px !important;
            color: #dfe4ff !important;
            backdrop-filter: blur(8px);
        }
        .stAlert p, div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
            color: #dfe4ff !important;
        }
        div[data-testid="stAlert"] svg { color: #b9aaff !important; }

        div[data-testid="stDataFrame"], div[data-testid="stTable"], table {
            background: rgba(12,16,40,.6) !important;
            color: #e6e9ff !important;
            border-radius: 16px !important;
        }
        .stTable th, thead th { color: #b9aaff !important; }
        table td, table th { border-color: rgba(255,255,255,.08) !important; }

        a { color: #8fd4ff !important; }

        /* Resume preview iframe looks like a clean paper document */
        iframe[title="st.iframe"], [data-testid="stIframe"] iframe {
            background: #ffffff;
            border-radius: 14px;
            box-shadow: 0 18px 44px rgba(3, 6, 24, .5);
            border: none;
        }

        /* ============ SCROLLBAR ============ */
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #6f5cf1, #3fb6ff);
            border-radius: 99px;
            border: 2px solid #070b1c;
        }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,.03); }

        /* ============ HIDE STREAMLIT CHROME ============ */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { background: transparent !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Ambient 3D scene (fixed background layer) + card tilt interaction.
    st.markdown(
        """
        <div class="fg-scene">
          <div class="fg-orb o1"></div>
          <div class="fg-orb o2"></div>
          <div class="fg-orb o3"></div>
          <div class="fg-ring r1"></div>
          <div class="fg-ring r2"></div>
          <div class="fg-star" style="left:12%; top:22%;"></div>
          <div class="fg-star" style="left:28%; top:64%; animation-delay:.8s;"></div>
          <div class="fg-star" style="left:55%; top:18%; animation-delay:1.6s;"></div>
          <div class="fg-star" style="left:74%; top:48%; animation-delay:2.2s;"></div>
          <div class="fg-star" style="left:88%; top:76%; animation-delay:3s;"></div>
          <div class="fg-star" style="left:41%; top:84%; animation-delay:1.2s;"></div>
          <div class="fg-star" style="left:66%; top:88%; animation-delay:2.6s;"></div>
          <div class="fg-star" style="left:9%;  top:80%; animation-delay:3.4s;"></div>
        </div>

        <script>
        (function () {
          function bindTilt(root) {
            root.querySelectorAll('.fg-tilt').forEach(function (card) {
              if (card.dataset.tiltBound) return;
              card.dataset.tiltBound = "1";
              card.addEventListener('mousemove', function (e) {
                var r = card.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width;
                var py = (e.clientY - r.top) / r.height;
                card.style.setProperty('--ry', ((px - .5) * 12).toFixed(2) + 'deg');
                card.style.setProperty('--rx', ((.5 - py) * 10).toFixed(2) + 'deg');
                card.style.setProperty('--mx', (px * 100).toFixed(1) + '%');
                card.style.setProperty('--my', (py * 100).toFixed(1) + '%');
              });
              card.addEventListener('mouseleave', function () {
                card.style.setProperty('--rx', '0deg');
                card.style.setProperty('--ry', '0deg');
              });
            });
          }
          function bindParallax() {
            var scene = document.querySelector('.fg-scene');
            if (!scene || scene.dataset.parallaxBound) return;
            scene.dataset.parallaxBound = "1";
            window.addEventListener('mousemove', function (e) {
              var dx = (e.clientX / window.innerWidth - .5);
              var dy = (e.clientY / window.innerHeight - .5);
              scene.style.transform = 'translate3d(' + (dx * 14) + 'px,' + (dy * 10) + 'px,0)';
            });
          }
          function tick() { bindTilt(document); bindParallax(); }
          new MutationObserver(tick).observe(document.body, { childList: true, subtree: true });
          document.addEventListener('DOMContentLoaded', tick);
          tick();
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# Reusable presentation snippets (HTML only — no app logic)
# ------------------------------------------------------------------

# The six Career Toolkit tools, in the order a student should walk them.
# (icon, title, card description, page script)
TOOL_STEPS = [
    (
        "🎯",
        "Career Recommendations",
        "Find career paths that match your profile, skills and interests.",
        "pages/2_careers.py",
    ),
    (
        "📊",
        "Skill-Gap Analysis",
        "Understand the skills you already have and the areas you need to improve.",
        "pages/7_Dashboard.py",
    ),
    (
        "🗺️",
        "Learning Roadmap",
        "Follow a personalized step-by-step plan toward your target career.",
        "pages/3_Roadmap.py",
    ),
    (
        "💼",
        "Jobs & Internships",
        "Explore opportunities that match your career profile.",
        "pages/4_Jobs.py",
    ),
    (
        "📄",
        "Resume Builder",
        "Create a professional, ATS-friendly resume.",
        "pages/5_Resume.py",
    ),
    (
        "🎤",
        "AI Mock Interview",
        "Practice personalized interview questions and receive feedback.",
        "pages/6_Interview.py",
    ),
]


def section_title(title: str, emoji: str = ""):
    """Animated section heading with a glowing gradient bar."""
    st.markdown(
        f"""
        <div class="fg-section fg-rise">
            <span class="bar"></span>
            <h2>{emoji} {title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_url(script_path: str) -> str:
    """
    URL path Streamlit serves a page script on: the file name without its
    ordering prefix and extension, so 'pages/3_Roadmap.py' -> '/Roadmap'.
    """
    name = os.path.splitext(os.path.basename(script_path))[0]
    return "/" + re.sub(r"^\d+[_-]?", "", name)


def tilt_card(
    icon: str,
    title: str,
    text: str,
    delay: str = "",
    page: str | None = None,
):
    """
    3D tilting glass card (cursor-reactive via the injected JS).

    Pass `page` (a script path such as 'pages/3_Roadmap.py') to make the
    whole card open that page when clicked.
    """
    card = f"""
        <div class="fg-tilt fg-pop {delay}" style="min-height:158px; margin-bottom:18px;">
            <div class="fg-icon">{icon}</div>
            <div class="fg-title">{title}</div>
            <div class="fg-text">{text}</div>
        </div>
        """

    if page:
        card = f'<a class="fg-card" href="{page_url(page)}">{card}</a>'

    st.markdown(card, unsafe_allow_html=True)


def tool_step_nav(current_page: str):
    """
    Bottom-of-page walkthrough for the six Career Toolkit tools.

    Shows "Tool N of 6" with a progress rail, then Previous / Next buttons
    that open the neighbouring tool with st.switch_page — so a student can
    move down the toolkit one tool at a time instead of hunting the sidebar.

    Call it once, at the very end of a tool page, e.g.
    `tool_step_nav("pages/3_Roadmap.py")`.
    """
    scripts = [page for _, _, _, page in TOOL_STEPS]
    if current_page not in scripts:
        return

    index = scripts.index(current_page)
    total = len(TOOL_STEPS)
    icon, title, _, _ = TOOL_STEPS[index]

    prev_step = TOOL_STEPS[index - 1] if index > 0 else None
    next_step = TOOL_STEPS[index + 1] if index + 1 < total else None

    key = re.sub(r"\W+", "_", os.path.splitext(os.path.basename(current_page))[0])
    pct = round((index + 1) / total * 100, 2)

    st.html(
        f'<div class="fg-stepnav fg-rise">'
        f'<div class="fg-stepnav-top">'
        f'<span class="fg-stepnav-chip">Tool {index + 1} of {total}</span>'
        f'<span class="fg-stepnav-title">{icon} {title}</span>'
        f"</div>"
        f'<div class="fg-stepnav-rail"><span style="width:{pct}%"></span></div>'
        f"</div>"
    )

    back_col, next_col = st.columns(2, gap="small")

    with back_col:
        back_label = f"← {prev_step[1]}" if prev_step else "← Back to Toolkit"
        back_page = prev_step[3] if prev_step else "app.py"
        if st.button(back_label, key=f"stepnav_back_{key}", use_container_width=True):
            st.switch_page(back_page)

    with next_col:
        next_label = f"{next_step[1]} →" if next_step else "Finish · Back to Toolkit"
        next_page = next_step[3] if next_step else "app.py"
        if st.button(
            next_label,
            key=f"stepnav_next_{key}",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page(next_page)


def stat_card(label: str, value: str):
    """Hover-lifting status/metric card."""
    st.markdown(
        f"""
        <div class="fg-stat fg-pop">
            <div class="lbl">{label}</div>
            <div class="val">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
