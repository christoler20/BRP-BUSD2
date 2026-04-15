"""
Berkeley and BUSD Educational History Timeline — Streamlit App
==============================================================
A data-driven, filterable timeline tracing how California law,
Berkeley housing policy, community organizing, and BUSD reform
shaped educational access over time.

Data lives in events.json. The app adapts automatically to the
curated 20-point timeline dataset.
"""

import html
import json
import pathlib
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Berkeley and BUSD Educational History Timeline",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — editorial / academic aesthetic
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown(
        """
        <style>
        /* ── Fonts ─────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');

        /* ── Root variables ────────────────────────────────────── */
        :root {
            --clr-bg:        #f5f0e8;
            --clr-fg:        #1f1c18;
            --clr-primary:   #8c5a1e;
            --clr-muted:     #877b6d;
            --clr-border:    #d5cfc5;
            --clr-card:      rgba(249, 245, 238, 0.94);
            --clr-california:#8c5a1e;
            --clr-national:  #8f3b2e;
            --clr-berkeley:  #245f99;
            --clr-busd:      #2f7d57;
            --font-display:  'Playfair Display', Georgia, serif;
            --font-body:     'Source Sans 3', 'Source Sans Pro', sans-serif;
        }

        /* ── Global overrides ──────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--clr-bg) !important;
        }
        .stApp {
            background-color: var(--clr-bg) !important;
        }
        /* Hide Streamlit chrome */
        #MainMenu, header[data-testid="stHeader"], footer {
            visibility: hidden;
        }

        /* ── Hero ──────────────────────────────────────────────── */
        .hero-wrapper {
            background: linear-gradient(180deg, rgba(31, 28, 24, 0.94) 0%, rgba(47, 39, 31, 0.9) 100%);
            padding: 4.5rem 2rem 3.5rem;
            text-align: center;
            border-radius: 0 0 0.75rem 0.75rem;
            margin: -1rem -1rem 2.5rem;
        }
        .hero-wrapper h1 {
            font-family: var(--font-display);
            font-size: 2.8rem;
            font-weight: 700;
            color: #f5f0e8;
            line-height: 1.15;
            margin: 0 0 1rem;
        }
        .hero-wrapper h1 em {
            color: var(--clr-primary);
            font-style: italic;
        }
        .hero-wrapper .hero-sub {
            color: rgba(245, 240, 232, 0.6);
            font-family: var(--font-body);
            font-size: 1.1rem;
            max-width: 640px;
            margin: 0 auto;
            line-height: 1.7;
        }

        /* ── Project context block ─────────────────────────────── */
        .context-block {
            max-width: 52rem;
            margin: 0 auto 2.5rem;
            border: 1px solid var(--clr-border);
            border-radius: 0.5rem;
            padding: 1.75rem 2rem;
            background: var(--clr-card);
            box-shadow: 0 2px 10px rgba(31, 28, 24, 0.04);
        }
        .context-block h2 {
            font-family: var(--font-display);
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0 0 0.15rem;
            color: var(--clr-fg);
        }
        .context-block .label {
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.72rem;
            color: var(--clr-primary);
            font-weight: 600;
            font-family: var(--font-body);
            margin-bottom: 1.25rem;
        }
        .context-block .body-text {
            font-family: var(--font-body);
            font-size: 0.95rem;
            line-height: 1.8;
            color: rgba(31, 28, 24, 0.78);
        }
        .context-block .body-text p + p {
            margin-top: 0.85rem;
        }

        /* ── Metrics bar ───────────────────────────────────────── */
        .metrics-bar {
            display: flex;
            gap: 2rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }
        .metric-item {
            text-align: center;
        }
        .metric-item .num {
            font-family: var(--font-display);
            font-size: 2rem;
            font-weight: 700;
            color: var(--clr-primary);
            line-height: 1;
        }
        .metric-item .lbl {
            font-family: var(--font-body);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--clr-muted);
            margin-top: 0.25rem;
        }

        /* ── Event card ────────────────────────────────────────── */
        .event-card {
            background: var(--clr-card);
            border: 1px solid var(--clr-border);
            border-radius: 0.6rem;
            padding: 1.75rem 2rem;
            margin-bottom: 1.5rem;
            position: relative;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: box-shadow 0.2s ease;
        }
        .event-card:hover {
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }

        /* Timeline dot */
        .event-card::before {
            content: '';
            position: absolute;
            left: -28px;
            top: 1.75rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--clr-primary);
            border: 3px solid #9e6b1e;
        }

        .event-year {
            font-family: var(--font-display);
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--clr-primary);
            margin-bottom: 0.2rem;
        }

        .event-badge {
            display: inline-block;
            padding: 0.15rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-family: var(--font-body);
            margin-right: 0.4rem;
            margin-bottom: 0.65rem;
        }
        .badge-california { background: rgba(140,90,30,0.14); color: var(--clr-california); }
        .badge-national   { background: rgba(143,59,46,0.14); color: var(--clr-national); }
        .badge-berkeley   { background: rgba(36,95,153,0.14); color: var(--clr-berkeley); }
        .badge-busd       { background: rgba(47,125,87,0.14); color: var(--clr-busd); }

        .topic-tag {
            display: inline-block;
            padding: 0.12rem 0.55rem;
            border-radius: 9999px;
            font-size: 0.65rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-family: var(--font-body);
            background: rgba(31, 28, 24, 0.06);
            color: var(--clr-muted);
            margin-right: 0.35rem;
            margin-bottom: 0.65rem;
        }

        .event-title {
            font-family: var(--font-display);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.65rem;
            color: var(--clr-fg);
        }

        .event-desc {
            font-family: var(--font-body);
            font-size: 0.93rem;
            line-height: 1.75;
            color: rgba(31, 28, 24, 0.74);
        }

        .event-img {
            margin-top: 1rem;
            border-radius: 0.4rem;
            max-width: 100%;
            max-height: 280px;
            object-fit: cover;
        }

        .event-meta {
            margin-top: 0.75rem;
            font-family: var(--font-body);
            font-size: 0.78rem;
            color: var(--clr-muted);
            line-height: 1.6;
        }
        .event-meta a {
            color: var(--clr-primary);
            text-decoration: none;
            overflow-wrap: anywhere;
        }
        .event-meta a:hover {
            text-decoration: underline;
        }

        /* ── Timeline vertical line ────────────────────────────── */
        .timeline-container {
            position: relative;
            padding-left: 2.25rem;
            max-width: 56rem;
            margin: 0 auto;
        }
        .timeline-container::before {
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--clr-border);
        }

        /* ── Year divider ──────────────────────────────────────── */
        .year-divider {
            font-family: var(--font-display);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--clr-muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            padding: 0.75rem 0 0.5rem 0;
            margin-top: 1.5rem;
            border-bottom: 1px solid var(--clr-border);
            margin-bottom: 1rem;
        }
        .year-divider:first-child {
            margin-top: 0;
        }

        /* ── No results ────────────────────────────────────────── */
        .no-events {
            text-align: center;
            padding: 3rem 1rem;
            font-family: var(--font-body);
            color: var(--clr-muted);
            font-size: 1rem;
        }

        /* ── Sidebar tweaks ────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #ede7db;
        }
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
            font-family: var(--font-display);
        }

        /* ── Filter pills (in main content) ────────────────────── */
        .filter-section {
            max-width: 56rem;
            margin: 0 auto 1.5rem;
        }

        /* ── Streamlit widget styling ──────────────────────────── */
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stRadio"] label,
        div[data-testid="stSelectbox"] label {
            font-family: var(--font-body) !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: var(--clr-muted) !important;
        }

        /* ── Responsive ────────────────────────────────────────── */
        @media (max-width: 768px) {
            .hero-wrapper { padding: 3rem 1rem 2.5rem; }
            .hero-wrapper h1 { font-size: 2rem; }
            .event-card { padding: 1.25rem 1.25rem; }
            .timeline-container { padding-left: 1.5rem; }
            .context-block { padding: 1.25rem 1.25rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "events.json"

@st.cache_data
def load_events():
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data["events"]


def get_filter_options(events):
    """Derive unique categories and topics from the dataset."""
    categories = sorted({e["category"] for e in events})
    topics = sorted({t for e in events for t in e.get("topics", []) if t})
    years = sorted({e["year"] for e in events})
    return categories, topics, years


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def render_hero():
    st.markdown(
        """
        <div class="hero-wrapper">
            <h1>Berkeley, California, and BUSD in <em>20 Historical Points</em></h1>
            <p class="hero-sub">
                A concise public timeline showing how state law, housing exclusion,
                community organizing, desegregation, and present-day repair shaped
                educational access in Berkeley.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_context():
    st.markdown(
        """
        <div class="context-block">
            <h2>How to Read This Timeline</h2>
            <div class="label">Project Context</div>
            <div class="body-text">
                <p>This version condenses a much longer historical record into 20 points designed for a quick but connected read. The sequence moves from California’s early systems of unfreedom and school exclusion to Berkeley housing segregation, district desegregation, Black community institution-building, and current repair efforts.</p>
                <p>Each entry was selected because it helps explain educational access in Berkeley and BUSD rather than offering isolated background. The timeline combines state, national, Berkeley, and BUSD milestones so readers can see how law, housing, school policy, and community action shaped one another over time.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(events, filtered_events):
    total = len(events)
    shown = len(filtered_events)
    years_spanned = (
        max(e["year"] for e in events) - min(e["year"] for e in events)
        if events else 0
    )
    cats = len({e["category"] for e in events})
    st.markdown(
        f"""
        <div class="metrics-bar">
            <div class="metric-item">
                <div class="num">{shown}</div>
                <div class="lbl">Events Shown</div>
            </div>
            <div class="metric-item">
                <div class="num">{total}</div>
                <div class="lbl">Total Events</div>
            </div>
            <div class="metric-item">
                <div class="num">{years_spanned}+</div>
                <div class="lbl">Years Spanned</div>
            </div>
            <div class="metric-item">
                <div class="num">{cats}</div>
                <div class="lbl">Categories</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_event_card(event):
    """Render a single event as an HTML card."""
    cat = html.escape(event["category"])
    cat_class = f"badge-{event['category'].lower()}"
    badges_html = f'<span class="event-badge {cat_class}">{cat}</span>'

    topics_html = ""
    for t in event.get("topics", []):
        if t:
            topics_html += f'<span class="topic-tag">{html.escape(t)}</span>'

    img_html = ""
    if event.get("image_url"):
        alt = html.escape(event["title"])
        img_url = html.escape(event["image_url"])
        img_html = f'<img src="{img_url}" alt="{alt}" class="event-img" loading="lazy">'

    meta_parts = []
    if event.get("image_caption"):
        meta_parts.append(f'<em>{html.escape(event["image_caption"])}</em>')
    if event.get("image_source"):
        meta_parts.append(f'Image: {html.escape(event["image_source"])}')
    if event.get("source_citation"):
        cite = html.escape(event["source_citation"])
        if event.get("source_url"):
            cite = f'<a href="{html.escape(event["source_url"])}" target="_blank" rel="noopener noreferrer">{cite}</a>'
        meta_parts.append(cite)
    meta_html = ""
    if meta_parts:
        meta_html = '<p class="event-meta">' + " · ".join(meta_parts) + "</p>"

    title = html.escape(event["title"])
    description = html.escape(event["description"])

    card_html = (
        f'<div class="event-card">'
        f'<div class="event-year">{event["year"]}</div>'
        f'{badges_html} {topics_html}'
        f'<div class="event-title">{title}</div>'
        f'<div class="event-desc">{description}</div>'
        f'{img_html}'
        f'{meta_html}'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    inject_css()

    events = load_events()
    all_categories, all_topics, all_years = get_filter_options(events)

    # ── Hero ──────────────────────────────────────────────────
    render_hero()

    # ── Context ───────────────────────────────────────────────
    render_context()

    # ── Filters ───────────────────────────────────────────────
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        selected_categories = st.multiselect(
            "Category",
            options=all_categories,
            default=all_categories,
            help="Filter events by geographic scope",
        )
    with col2:
        selected_topics = st.multiselect(
            "Topic",
            options=all_topics,
            default=[],
            help="Narrow by topic tag (leave empty for all)",
        )
    with col3:
        if all_years:
            year_min, year_max = int(min(all_years)), int(max(all_years))
            year_range = st.slider(
                "Year Range",
                min_value=year_min,
                max_value=year_max,
                value=(year_min, year_max),
            )
        else:
            year_range = (0, 9999)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Apply filters ─────────────────────────────────────────
    filtered = events

    if selected_categories:
        filtered = [e for e in filtered if e["category"] in selected_categories]
    else:
        filtered = []  # nothing selected → no results

    if selected_topics:
        filtered = [
            e for e in filtered
            if any(t in selected_topics for t in e.get("topics", []))
        ]

    filtered = [
        e for e in filtered
        if year_range[0] <= e["year"] <= year_range[1]
    ]

    # Sort chronologically
    filtered.sort(key=lambda e: (e["year"], e["title"]))

    # ── Metrics ───────────────────────────────────────────────
    render_metrics(events, filtered)

    # ── Timeline ──────────────────────────────────────────────
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    if not filtered:
        st.markdown(
            '<p class="no-events">No events match the selected filters. '
            "Try broadening your selection.</p>",
            unsafe_allow_html=True,
        )
    else:
        current_year = None
        for event in filtered:
            if event["year"] != current_year:
                current_year = event["year"]
                st.markdown(
                    f'<div class="year-divider">{current_year}</div>',
                    unsafe_allow_html=True,
                )
            render_event_card(event)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
