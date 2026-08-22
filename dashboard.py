"""
YouTube Newsletter Dashboard
A beautiful web interface to manage your newsletter.
"""

import streamlit as st
import os
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent
CHANNELS_FILE = PROJECT_DIR / "get_videos.py"
PROMPT_FILE = PROJECT_DIR / "write_articles.py"
TRACKER_FILE = PROJECT_DIR / "processed_videos.json"
NEWSLETTERS_DIR = PROJECT_DIR / "newsletters"
PLIST_FILE = Path.home() / "Library/LaunchAgents/com.youtube.newsletter.plist"

# Create newsletters directory if it doesn't exist
NEWSLETTERS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="The Digest",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - Editorial Magazine Aesthetic
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&family=Sora:wght@300;400;500;600&display=swap');

    :root {
        --bg-primary: #0d0d0d;
        --bg-secondary: #161616;
        --bg-tertiary: #1a1a1a;
        --bg-card: #1e1e1e;
        --accent-gold: #d4a855;
        --accent-gold-dim: #a68542;
        --accent-gold-glow: rgba(212, 168, 85, 0.15);
        --text-primary: #e8e4dd;
        --text-secondary: #9a958c;
        --text-dim: #5c5850;
        --border-subtle: #2a2a2a;
        --success: #5cb85c;
        --error: #c9302c;
    }

    /* Main container */
    .stApp {
        background: var(--bg-primary);
        background-image:
            radial-gradient(ellipse at top right, rgba(212, 168, 85, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at bottom left, rgba(212, 168, 85, 0.02) 0%, transparent 50%);
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }

    [data-testid="stSidebar"] .stRadio > label {
        font-family: 'Sora', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        font-family: 'Sora', sans-serif;
        font-weight: 400;
        font-size: 0.95rem;
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: var(--bg-tertiary);
        border-color: var(--border-subtle);
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: var(--accent-gold-glow);
        border-color: var(--accent-gold-dim);
        color: var(--accent-gold);
    }

    /* Typography */
    h1, h2, h3 {
        font-family: 'Cormorant Garamond', Georgia, serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    h1 {
        font-size: 2.75rem !important;
        letter-spacing: -0.02em;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 1rem;
        margin-bottom: 2rem !important;
    }

    h2 {
        font-size: 1.75rem !important;
        color: var(--accent-gold) !important;
        margin-top: 2rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
        font-weight: 400 !important;
        font-style: italic;
    }

    p, li, span, div {
        font-family: 'Sora', sans-serif;
        color: var(--text-primary);
    }

    /* Cards */
    [data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        font-family: 'Sora', sans-serif;
        font-weight: 500;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Sora', sans-serif;
        font-weight: 500;
        font-size: 0.9rem;
        letter-spacing: 0.03em;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
        border: 1px solid var(--border-subtle);
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .stButton > button:hover {
        border-color: var(--accent-gold-dim);
        background: var(--accent-gold-glow);
        color: var(--accent-gold);
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dim) 100%);
        color: var(--bg-primary);
        border: none;
        font-weight: 600;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(212, 168, 85, 0.25);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        color: var(--text-primary);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-gold-dim);
        box-shadow: 0 0 0 2px var(--accent-gold-glow);
    }

    /* Selectbox styling */
    .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
    }

    .stSelectbox > div > div > div {
        color: var(--text-primary) !important;
        background: var(--bg-tertiary) !important;
    }

    .stSelectbox [data-baseweb="select"] {
        background: var(--bg-tertiary) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
    }

    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
    }

    [data-baseweb="popover"] li {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }

    [data-baseweb="popover"] li:hover {
        background: var(--bg-tertiary) !important;
    }

    [role="listbox"] {
        background: var(--bg-card) !important;
    }

    [role="option"] {
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
    }

    [role="option"]:hover {
        background: var(--accent-gold-glow) !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem;
    }

    [data-testid="stMetric"] label {
        font-family: 'Sora', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-secondary);
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--accent-gold);
    }

    /* Info boxes */
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        border-left: 3px solid var(--accent-gold);
    }

    /* Code blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: var(--bg-tertiary);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: var(--accent-gold);
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 2rem 0;
    }

    /* Channel item styling */
    .channel-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    .channel-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        color: var(--text-primary);
    }

    /* Success/Error messages */
    .stSuccess {
        background: rgba(92, 184, 92, 0.15) !important;
        border: 1px solid rgba(92, 184, 92, 0.4) !important;
        border-left: 3px solid var(--success) !important;
    }

    .stError {
        background: rgba(201, 48, 44, 0.15) !important;
        border: 1px solid rgba(201, 48, 44, 0.4) !important;
        border-left: 3px solid var(--error) !important;
    }

    .stWarning {
        background: rgba(212, 168, 85, 0.15) !important;
        border: 1px solid rgba(212, 168, 85, 0.4) !important;
        border-left: 3px solid var(--accent-gold) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-subtle);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-dim);
    }

    /* Logo/Title styling */
    .masthead {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid var(--accent-gold);
        margin-bottom: 2rem;
    }

    .masthead h1 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .masthead .tagline {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }

    /* Newsletter card */
    .newsletter-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }

    .newsletter-card:hover {
        border-color: var(--accent-gold-dim);
    }

    .newsletter-date {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--accent-gold);
        margin-bottom: 0.5rem;
    }

    .newsletter-meta {
        font-family: 'Sora', sans-serif;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_channels():
    """Extract channel handles from the Python file."""
    with open(CHANNELS_FILE) as f:
        content = f.read()

    match = re.search(r'CHANNELS\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not match:
        return []

    channels_block = match.group(1)
    handles = re.findall(r'["\'](@[\w]+)["\']', channels_block)
    return handles


def save_channels(channels):
    """Save channels back to the Python file."""
    with open(CHANNELS_FILE) as f:
        content = f.read()

    channels_str = "CHANNELS = [\n"
    for ch in channels:
        channels_str += f'    "{ch}",\n'
    channels_str += "]"

    content = re.sub(
        r'CHANNELS\s*=\s*\[.*?\]',
        channels_str,
        content,
        flags=re.DOTALL
    )

    with open(CHANNELS_FILE, "w") as f:
        f.write(content)


def extract_handle_from_url(url_or_handle):
    """Extract @handle from a YouTube URL or return as-is if already a handle."""
    text = url_or_handle.strip()

    if text.startswith("@"):
        return text

    patterns = [
        r'youtube\.com/@([\w]+)',
        r'youtube\.com/c/([\w]+)',
        r'youtube\.com/channel/([\w-]+)',
        r'youtube\.com/user/([\w]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            handle = match.group(1)
            if not handle.startswith("@"):
                handle = "@" + handle
            return handle

    if text and not text.startswith("http"):
        return "@" + text if not text.startswith("@") else text

    return None


def get_schedule():
    """Read current schedule from plist."""
    if PLIST_FILE.exists():
        with open(PLIST_FILE) as f:
            content = f.read()

        weekday = 3
        hour = 7

        weekday_match = re.search(r'<key>Weekday</key>\s*<integer>(\d+)</integer>', content)
        if weekday_match:
            weekday = int(weekday_match.group(1))

        hour_match = re.search(r'<key>Hour</key>\s*<integer>(\d+)</integer>', content)
        if hour_match:
            hour = int(hour_match.group(1))

        return weekday, hour
    return 3, 7


def save_schedule(weekday, hour):
    """Save schedule to plist and reload."""
    if PLIST_FILE.exists():
        with open(PLIST_FILE) as f:
            content = f.read()

        content = re.sub(
            r'(<key>Weekday</key>\s*<integer>)\d+(</integer>)',
            f'\\g<1>{weekday}\\2',
            content
        )
        content = re.sub(
            r'(<key>Hour</key>\s*<integer>)\d+(</integer>)',
            f'\\g<1>{hour}\\2',
            content
        )

        with open(PLIST_FILE, "w") as f:
            f.write(content)

        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(PLIST_FILE)],
                      capture_output=True)
        subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(PLIST_FILE)],
                      capture_output=True)
        return True
    return False


def get_newsletters():
    """Get list of saved newsletters."""
    newsletters = []
    if NEWSLETTERS_DIR.exists():
        for json_file in sorted(NEWSLETTERS_DIR.glob("newsletter_*.json"), reverse=True):
            with open(json_file) as f:
                data = json.load(f)
                data["json_path"] = str(json_file)
                newsletters.append(data)
    return newsletters


# ============================================
# SIDEBAR NAVIGATION
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 700;
                    letter-spacing: 0.1em; color: #d4a855;">THE DIGEST</div>
        <div style="font-family: 'Sora', sans-serif; font-size: 0.7rem; letter-spacing: 0.15em;
                    text-transform: uppercase; color: #5c5850; margin-top: 0.25rem;">Newsletter Studio</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        ["Generate", "Channels", "Writing Style", "Archive", "Schedule"],
        label_visibility="visible"
    )

# ============================================
# PAGE: Generate Newsletter
# ============================================
if page == "Generate":
    st.markdown("""
    <div class="masthead">
        <h1>THE DIGEST</h1>
        <div class="tagline">Your personal YouTube newsletter, crafted by AI</div>
    </div>
    """, unsafe_allow_html=True)

    # Centered generate button
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        if st.button("Generate & Send Newsletter", type="primary", use_container_width=True):
            with st.spinner("Crafting your newsletter..."):
                try:
                    # Note: If this fails with ModuleNotFoundError, replace "python3" with your full Python path
                    # Find it by running: which python3
                    result = subprocess.run(
                        ["python3", str(PROJECT_DIR / "main.py")],
                        capture_output=True,
                        text=True,
                        cwd=str(PROJECT_DIR),
                        timeout=600
                    )

                    if "Newsletter sent successfully" in result.stdout:
                        st.success("Newsletter sent! Check your inbox.")
                    elif "No new videos" in result.stdout:
                        st.info("No new videos to process. All caught up!")
                    else:
                        st.warning("Completed with notes. See log below.")

                    with st.expander("View Output Log"):
                        st.code(result.stdout + result.stderr, language="text")

                except subprocess.TimeoutExpired:
                    st.error("Process timed out. Try again.")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.caption("Fetches new videos, writes articles with AI, and sends to your inbox")

    # Stats at the bottom
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)

    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            data = json.load(f)
        video_count = len(data.get("videos", {}))
    else:
        video_count = 0

    channels = get_channels()
    weekday, hour = get_schedule()
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    with col1:
        st.metric("Articles Sent", video_count)

    with col2:
        st.metric("Channels", len(channels))

    with col3:
        st.metric("Next Run", f"{days[weekday]} {hour}:00")

# ============================================
# PAGE: Channels
# ============================================
elif page == "Channels":
    st.markdown("## Your Channels")

    # Initialize session state for feedback messages
    if "channel_added" not in st.session_state:
        st.session_state.channel_added = None

    channels = get_channels()

    # Show success/error message if there is one
    if st.session_state.channel_added:
        if st.session_state.channel_added.startswith("✓"):
            st.success(st.session_state.channel_added)
        else:
            st.error(st.session_state.channel_added)
        st.session_state.channel_added = None

    # Add new channel section
    st.markdown("#### Add a Channel")
    st.caption("Paste a YouTube channel URL or @handle, then press Enter or click Add")

    # Use a form so Enter key submits
    with st.form(key="add_channel_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            new_input = st.text_input(
                "Channel URL or handle",
                placeholder="https://youtube.com/@channelname or @channelname",
                label_visibility="collapsed"
            )
        with col2:
            add_clicked = st.form_submit_button("Add", type="primary", use_container_width=True)

    if add_clicked and new_input:
        handle = extract_handle_from_url(new_input)
        if handle:
            if handle not in channels:
                channels.append(handle)
                save_channels(channels)
                st.session_state.channel_added = f"✓ Added {handle}"
                st.rerun()
            else:
                st.session_state.channel_added = f"Channel {handle} is already in your list"
                st.rerun()
        else:
            st.session_state.channel_added = "Could not parse that URL. Try pasting the full YouTube channel URL."
            st.rerun()

    st.divider()

    # Display current channels
    st.markdown(f"#### Your Channels ({len(channels)})")

    if channels:
        for i, channel in enumerate(channels):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    border: 1px solid #2a2a2a;
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.95rem;
                    color: #e8e4dd;
                ">{channel}</div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Remove", key=f"del_{i}", type="secondary"):
                    channels.pop(i)
                    save_channels(channels)
                    st.session_state.channel_added = f"✓ Removed {channel}"
                    st.rerun()
    else:
        st.info("No channels yet. Add your first channel above!")

# ============================================
# PAGE: Writing Style
# ============================================
elif page == "Writing Style":
    st.markdown("## Writing Style")
    st.write("Customize how Claude AI writes your articles.")

    with open(PROMPT_FILE) as f:
        content = f.read()

    match = re.search(r'prompt = f"""(.+?)"""', content, re.DOTALL)

    if match:
        current_prompt = match.group(1)

        new_prompt = st.text_area(
            "Article prompt",
            value=current_prompt,
            height=450,
            label_visibility="collapsed"
        )

        if st.button("Save Changes", type="primary"):
            new_content = content[:match.start(1)] + new_prompt + content[match.end(1):]
            with open(PROMPT_FILE, "w") as f:
                f.write(new_content)
            st.success("Writing style saved!")

# ============================================
# PAGE: Archive
# ============================================
elif page == "Archive":
    st.markdown("## Archive")

    # Tabs for newsletters vs individual videos
    tab1, tab2 = st.tabs(["Newsletters", "Processed Videos"])

    with tab1:
        newsletters = get_newsletters()

        if newsletters:
            st.markdown(f"**{len(newsletters)} newsletters sent**")

            for nl in newsletters:
                st.markdown(f"""
                <div class="newsletter-card">
                    <div class="newsletter-date">{nl.get('date', 'Unknown date')}</div>
                    <div class="newsletter-meta">
                        {nl.get('article_count', 0)} articles from {', '.join(nl.get('channels', [])[:3])}{'...' if len(nl.get('channels', [])) > 3 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    html_file = NEWSLETTERS_DIR / nl.get('html_file', '')
                    if html_file.exists():
                        with open(html_file) as f:
                            html_content = f.read()
                        st.download_button(
                            "Download HTML",
                            html_content,
                            file_name=nl.get('html_file', 'newsletter.html'),
                            mime="text/html",
                            key=f"html_{nl.get('timestamp')}"
                        )
                with col2:
                    epub_file = NEWSLETTERS_DIR / nl.get('epub_file', '')
                    if epub_file.exists():
                        with open(epub_file, "rb") as f:
                            epub_content = f.read()
                        st.download_button(
                            "Download EPUB",
                            epub_content,
                            file_name=nl.get('epub_file', 'newsletter.epub'),
                            mime="application/epub+zip",
                            key=f"epub_{nl.get('timestamp')}"
                        )

                st.markdown("---")
        else:
            st.info("No newsletters yet. Generate your first one from the Generate tab!")

    with tab2:
        if TRACKER_FILE.exists():
            with open(TRACKER_FILE) as f:
                data = json.load(f)

            videos = data.get("videos", {})

            if videos:
                sorted_videos = sorted(
                    videos.items(),
                    key=lambda x: x[1].get("processed_at", ""),
                    reverse=True
                )

                st.markdown(f"**{len(videos)} videos processed**")

                for video_id, info in sorted_videos:
                    with st.expander(f"{info.get('channel', 'Unknown')} — {info.get('title', 'Unknown')[:50]}..."):
                        st.write(f"**{info.get('title', 'Unknown')}**")
                        st.caption(f"From {info.get('channel', 'Unknown')}")

                        processed = info.get('processed_at', 'Unknown')
                        if processed != 'Unknown':
                            try:
                                dt = datetime.fromisoformat(processed)
                                processed = dt.strftime("%B %d, %Y at %I:%M %p")
                            except:
                                pass
                        st.caption(f"Processed: {processed}")

                        st.markdown(f"[Watch on YouTube](https://www.youtube.com/watch?v={video_id})")

                st.divider()

                if st.button("Clear All History", type="secondary"):
                    st.warning("This will allow all videos to be re-processed.")
            else:
                st.info("No videos processed yet.")
        else:
            st.info("No videos processed yet.")

# ============================================
# PAGE: Schedule
# ============================================
elif page == "Schedule":
    st.markdown("## Schedule")
    st.write("Set when your newsletter runs automatically.")

    weekday, hour = get_schedule()
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    col1, col2 = st.columns(2)

    with col1:
        new_day = st.selectbox(
            "Day",
            options=list(range(7)),
            format_func=lambda x: days[x],
            index=weekday
        )

    with col2:
        new_hour = st.selectbox(
            "Time",
            options=list(range(24)),
            format_func=lambda x: f"{x:02d}:00" + (" AM" if x < 12 else " PM"),
            index=hour
        )

    st.markdown(f"**Currently scheduled:** {days[weekday]} at {hour:02d}:00")

    if new_day != weekday or new_hour != hour:
        st.markdown(f"**New schedule:** {days[new_day]} at {new_hour:02d}:00")

        if st.button("Update Schedule", type="primary"):
            if save_schedule(new_day, new_hour):
                st.success(f"Updated to {days[new_day]} at {new_hour:02d}:00!")
            else:
                st.error("Couldn't update schedule")

    st.divider()

    st.caption("Your Mac must be awake at the scheduled time for the newsletter to run automatically.")

# ============================================
# Footer
# ============================================
st.markdown("---")
st.caption("The Digest • Powered by Claude AI")
