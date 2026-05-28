import streamlit as st
import time
import database as db  # Connects to your working database.py file

# Initialize database tables
db.init_db()

st.set_page_config(page_title="Study Burrow", page_icon="🐇", layout="centered")

# ==========================================
# USER ROUTING & AUTHENTICATION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# Standard app tracking states
if "exp" not in st.session_state:
    st.session_state.exp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "time_left" not in st.session_state:
    st.session_state.time_left = 25 * 60

# --- LOGIN GATEWAY SCREEN ---
if not st.session_state.logged_in:
    st.title("🐇 Welcome to the Study Burrow!")
    st.subheader("Login or Enter as a Guest to begin tracking.")
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Sign Up", "👤 Guest Mode"])
    
    with tab1:
        login_user = st.text_input("Username", key="l_user")
        login_pass = st.text_input("Password", type="password", key="l_pass")
        if st.button("Log In"):
            user_data = db.login_user(login_user, login_pass)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.session_state.level = user_data["level"]
                st.session_state.exp = user_data["exp"]
                st.success(f"Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        reg_user = st.text_input("Choose Username", key="r_user")
        reg_pass = st.text_input("Choose Password", type="password", key="r_pass")
        if st.button("Create Account"):
            if reg_user and reg_pass:
                if db.register_user(reg_user, reg_pass):
                    st.success("Account created! Please switch to the Login tab.")
                else:
                    st.error("Username already taken.")
            else:
                st.error("Please fill out all fields.")
                
    with tab3:
        st.info("💡 Guest data is temporary and will clear when the browser tab closes.")
        if st.button("Continue as Guest ➡️"):
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
            st.session_state.level = 1
            st.session_state.exp = 0
            st.rerun()

    st.stop() # Freeze view here until an option above routes them through

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
# 4. BACKGROUND MUSIC LIBRARY
# ==========================================
# 5. BACKGROUND MUSIC LIBRARY
# ==========================================
with st.sidebar:
    st.divider()
    st.subheader("🎵 Music Player")
    
    music_files = {
        "for the moment - almost here": "1.mp3.mpeg",
        "better kind of sweet - instrumental": "2.mp3.mpeg",
        "coffeeshop stories - almost here": "3.mp3.mpeg",
        "drive-through dinner - tmagnus ringblom": "4.mp3.mpeg",
        "coffee in winter - kimano": "5.mp3.mpeg"
    }
    
    chosen_track = st.selectbox("Select a track:", list(music_files.keys()))
    
    try:
        filename = music_files[chosen_track]
        with open(filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mpeg", loop=True, autoplay=True)
    except FileNotFoundError:
        st.error(f"Missing file: {filename}. Please upload it to your repo.")

# ==========================================
# 5. MAIN APP INTERFACE
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
# 6. LIVE TIMER LOOP LOGIC
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

    # 💾 SAVE DATA TO DATABASE HERE
    db.save_user_progress(
        st.session_state.username, 
        st.session_state.level, 
        st.session_state.exp
    )
    st.balloons()
    st.success(f"🎉 Session complete! You earned + {earned_exp} EXP for your Bunny!")
    if st.session_state.level > old_level:
        st.toast(f"✨ WOW! Your Bunny evolved into Level {st.session_state.level} ! ✨")
            
        # Reset clock for the next session
        st.session_state.time_left = chosen_seconds
        time.sleep(2) # Give user a second to read before refreshing UI
        st.rerun()
# ==========================================
# 7. SIDEBAR SETTINGS & LOGOUT
# ==========================================
with st.sidebar:
    st.subheader("⚙️ Account Controls")
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
