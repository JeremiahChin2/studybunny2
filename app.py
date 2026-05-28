import streamlit as st
import time

# ==========================================
# 1. PAGE CONFIGURATION & INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Study Burrow",
    page_icon="🐇",
    layout="centered"
)

# Initialize Session State variables if they don't exist
if "exp" not in st.session_state:
    st.session_state.exp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "time_left" not in st.session_state:
    st.session_state.time_left = 25 * 60  # Default 25 minutes in seconds

# ==========================================
# 2. GAMIFICATION LOGIC (EXP & LEVELS)
# ==========================================
# Each level requires Level * 100 EXP (e.g., Lvl 1->2 needs 100, Lvl 2->3 needs 200)
def get_exp_needed_for_level(lvl):
    return lvl * 100

def check_level_up():
    while True:
        needed = get_exp_needed_for_level(st.session_state.level)
        if st.session_state.exp >= needed:
            st.session_state.exp -= needed
            st.session_state.level += 1
        else:
            break

def get_bunny_tier(lvl):
    if lvl <= 2:
        return "Baby Bunny 🍼", "🐇"
    elif lvl <= 5:
        return "Studious Sprout 🌱", "🐇🥕"
    elif lvl <= 9:
        return "Honor Roll Rabbit 📚", "🦘" # Looking larger
    else:
        return "Professor Rabbit 🎓", "🐇🧠"

# Calculate current progress percentage
exp_needed = get_exp_needed_for_level(st.session_state.level)
progress_percentage = min(st.session_state.exp / exp_needed, 1.0)
tier_name, bunny_emoji = get_bunny_tier(st.session_state.level)

# ==========================================
# 3. SIDEBAR & APP INTRO
# ==========================================
with st.sidebar:
    st.title("🐾 How to Play")
    st.markdown("""
    1. **Choose your focus time** from the dropdown or set a custom time.
    2. Click **Start Timer** to begin studying.
    3. Stay focused! If the timer finishes, your bunny gets **10 EXP for every minute** you studied.
    4. Help your bunny evolve into a **Professor Rabbit**!
    """)
    st.divider()
    st.caption("Pro-tip: Don't refresh the page while the timer is running, or your bunny will lose track of time!")


# ==========================================
# BACKGROUND MUSIC (Native Component)
# ==========================================
try:
    # Open the file using its exact current name on GitHub
    with open("music.mp3.mpeg", "rb") as audio_file:
        audio_bytes = audio_file.read()
    
    # Render the native audio player widget in the sidebar
    with st.sidebar:
        st.divider()
        st.subheader("🎵 Background Music")
        st.audio(audio_bytes, format="audio/mpeg", loop=True)
except FileNotFoundError:
    pass

# ==========================================
# 4. MAIN APP INTERFACE
# ==========================================
st.title("🐇 Study Burrow Tracker")
st.subheader("Keep focused, level up your pet!")

# Layout: Split into Bunny Status and Timer Control
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown(f"### Current Form: **{tier_name}**")
    # Giant bunny display
    st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{bunny_emoji}</h1>", unsafe_allow_html=True)
    
    # Display Level & EXP
    st.metric(label="Bunny Level", value=f"Lv. {st.session_state.level}")
    st.write(f"**EXP:** {st.session_state.exp} / {exp_needed}")
    st.progress(progress_percentage)

with col2:
    st.markdown("### ⏱️ Study Clock")
    
    # Selection for Study Duration
    duration_option = st.selectbox(
        "Select your study duration:",
        options=["25 Minutes (Standard Pomodoro)", "50 Minutes", "5 Minutes (Test Run)", "Custom"],
        disabled=st.session_state.timer_running
    )
    
    if duration_option == "Custom":
        custom_minutes = st.number_input("Enter minutes:", min_value=1, max_value=180, value=25, disabled=st.session_state.timer_running)
        chosen_seconds = custom_minutes * 60
    elif "25 Minutes" in duration_option:
        chosen_seconds = 25 * 60
    elif "50 Minutes" in duration_option:
        chosen_seconds = 50 * 60
    else:
        chosen_seconds = 5 * 60

    # If the timer isn't running and the user changes options, update the display time
    if not st.session_state.timer_running and st.session_state.time_left != chosen_seconds:
        # Check if they clicked reset or changed selection
        if st.session_state.get('last_option') != duration_option:
            st.session_state.time_left = chosen_seconds
            st.session_state.last_option = duration_option

    # Dynamic Timer Visual Component
    timer_placeholder = st.empty()
    
    # Timer Action Buttons
    b1, b2 = st.columns(2)
    with b1:
        if not st.session_state.timer_running:
            if st.button("▶️ Start Timer", use_container_width=True):
                st.session_state.timer_running = True
                st.rerun()
        else:
            if st.button("⏸️ Pause Timer", use_container_width=True):
                st.session_state.timer_running = False
                st.rerun()
                
    with b2:
        if st.button("🔄 Reset Timer", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.time_left = chosen_seconds
            st.rerun()

# ==========================================
# 5. LIVE TIMER LOOP LOGIC
# ==========================================
# Render the current time static state first
mins, secs = divmod(st.session_state.time_left, 60)
timer_placeholder.markdown(f"<h1 style='text-align: center; font-size: 60px; color: #ff4b4b;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)

# If running, enter the live countdown loop
if st.session_state.timer_running:
    while st.session_state.time_left > 0 and st.session_state.timer_running:
        time.sleep(1)
        st.session_state.time_left -= 1
        
        # Update UI text dynamically without reloading the whole script
        mins, secs = divmod(st.session_state.time_left, 60)
        timer_placeholder.markdown(f"<h1 style='text-align: center; font-size: 60px; color: #ff4b4b;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
        
    # Check if timer finished naturally
    if st.session_state.time_left == 0 and st.session_state.timer_running:
        st.session_state.timer_running = False
        
        # Calculate earned EXP: 10 EXP per minute of the *chosen* session
        earned_exp = int((chosen_seconds / 60) * 10)
        st.session_state.exp += earned_exp
        
        # Process levels and trigger celebrations
        old_level = st.session_state.level
        check_level_up()
        
        st.balloons()
        st.success(f"🎉 Session complete! You earned +{earned_exp} EXP for your Bunny!")
        
        if st.session_state.level > old_level:
            st.toast(f"✨ WOW! Your Bunny evolved into Level {st.session_state.level}! ✨")
            
        # Reset clock for the next session
        st.session_state.time_left = chosen_seconds
        time.sleep(2) # Give user a second to read before refreshing UI
        st.rerun()
