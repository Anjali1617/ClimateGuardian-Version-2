# ==========================================
# AUTHENTICATION MODULE
# Handles user login, signup, and session management using CSV files
# ==========================================

import streamlit as st
import pandas as pd
import hashlib
import os
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import base64

# --- CSV Database file paths ---
USERS_DB = "users_database.csv"
ACTIVITIES_DB = "user_activities.csv"
CERTIFICATES_DB = "certificates_database.csv"

def init_csv_files():
    """Initialize CSV files with headers if they don't exist, and perform migrations."""
    if not os.path.exists(USERS_DB):
        pd.DataFrame(columns=['username', 'email', 'password_hash', 'full_name', 'created_at', 'eco_score', 'role']).to_csv(USERS_DB, index=False)
    else:
        # Migrate existing users to have a role
        try:
            df = pd.read_csv(USERS_DB)
            if 'role' not in df.columns:
                df['role'] = 'person'
                df.to_csv(USERS_DB, index=False)
        except Exception:
            pass
    
    if not os.path.exists(ACTIVITIES_DB):
        pd.DataFrame(columns=['id', 'timestamp', 'username', 'action', 'points']).to_csv(ACTIVITIES_DB, index=False)
        
    if not os.path.exists(CERTIFICATES_DB):
        pd.DataFrame(columns=['certificate_id', 'username', 'eco_score', 'rank', 'issued_date']).to_csv(CERTIFICATES_DB, index=False)

# Initialize the database on module load
init_csv_files()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username, email):
    """Check if user already exists in CSV"""
    try:
        df = pd.read_csv(USERS_DB)
        return not df[(df['username'] == username) | (df['email'] == email)].empty
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return False

def create_user(username, email, password, full_name, role='person'):
    """Create a new user account in CSV"""
    try:
        df = pd.read_csv(USERS_DB)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['username', 'email', 'password_hash', 'full_name', 'created_at', 'eco_score', 'role'])

    new_user = pd.DataFrame([{
        'username': username,
        'email': email,
        'password_hash': hash_password(password),
        'full_name': full_name,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'eco_score': 0,
        'role': role
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_DB, index=False)
    return True

def verify_user(username, password, expected_role='person'):
    """Verify user credentials and role from CSV"""
    try:
        df = pd.read_csv(USERS_DB)
        user = df[df['username'] == username]
        if not user.empty:
            actual_role = user.iloc[0].get('role', 'person')
            # Check if passwords match AND role matches
            if user.iloc[0]['password_hash'] == hash_password(password):
                if actual_role == expected_role:
                    return True
        return False
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return False

def get_user_info(username):
    """Get user information from CSV"""
    try:
        df = pd.read_csv(USERS_DB)
        user = df[df['username'] == username]
        if not user.empty:
            return user.iloc[0].to_dict()
        return None
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None

def update_user_score(username, new_score):
    """Update user's eco score in CSV"""
    try:
        df = pd.read_csv(USERS_DB)
        df.loc[df['username'] == username, 'eco_score'] = new_score
        df.to_csv(USERS_DB, index=False)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass # Or handle error appropriately

def log_activity(username, action, points):
    """Log user activity to persistent CSV storage"""
    try:
        df = pd.read_csv(ACTIVITIES_DB)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['id', 'timestamp', 'username', 'action', 'points'])
    
    new_id = (df['id'].max() + 1) if not df.empty and 'id' in df.columns and not df['id'].isnull().all() else 1
    
    new_activity = pd.DataFrame([{
        'id': new_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'username': username,
        'action': action,
        'points': points
    }])
    df = pd.concat([df, new_activity], ignore_index=True)
    df.to_csv(ACTIVITIES_DB, index=False)

def get_all_activities():
    """Load all activities for global dashboard from CSV"""
    try:
        return pd.read_csv(ACTIVITIES_DB)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['id', 'timestamp', 'username', 'action', 'points'])

def login_page():
    """Display login page"""
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 10px auto 50px auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid #4CAF50;
        }
        .auth-title {
            text-align: center;
            color: #2e7d32;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .auth-icon {
            text-align: center;
            font-size: 5em;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Icon and Title
        st.markdown('<div class="auth-icon">🌿</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-title">Welcome Back!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Login to Climate Guardian</p>', unsafe_allow_html=True)
        
        tab_person, tab_admin = st.tabs(["🧑 Person Login", "🛡️ Admin Login"])
        
        # Person Login Tab
        with tab_person:
            with st.form("login_form_person"):
                username_p = st.text_input("👤 Username", placeholder="Enter your username", key="user_p")
                password_p = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="pass_p")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_button_p = st.form_submit_button("🚀 Login as Person", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("📝 Sign Up", use_container_width=True):
                        st.session_state['show_signup'] = True
                        st.rerun()
            
            if login_button_p:
                if not username_p or not password_p:
                    st.error("⚠️ Please fill in all fields!")
                elif verify_user(username_p, password_p, expected_role='person'):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username_p
                    st.session_state['role'] = 'person'
                    user_info = get_user_info(username_p)
                    st.session_state['user_info'] = user_info
                    
                    if user_info and 'eco_score' in user_info:
                        st.session_state['eco_score'] = int(user_info['eco_score'])
                    
                    st.query_params["user"] = username_p
                    st.query_params["logged_in"] = "true"
                    st.query_params["role"] = "person"
                    
                    st.success(f"✅ Welcome back, {username_p}! 🌍")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username, password, or role!")
        
        # Admin Login Tab
        with tab_admin:
            with st.form("login_form_admin"):
                username_a = st.text_input("👤 Username", placeholder="Enter your username", key="user_a")
                password_a = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="pass_a")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_button_a = st.form_submit_button("🚀 Login as Admin", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("📝 Sign Up", use_container_width=True):
                        st.session_state['show_signup'] = True
                        st.rerun()
            
            if login_button_a:
                if not username_a or not password_a:
                    st.error("⚠️ Please fill in all fields!")
                elif verify_user(username_a, password_a, expected_role='admin'):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username_a
                    st.session_state['role'] = 'admin'
                    user_info = get_user_info(username_a)
                    st.session_state['user_info'] = user_info
                    
                    if user_info and 'eco_score' in user_info:
                        st.session_state['eco_score'] = int(user_info['eco_score'])
                    
                    st.query_params["user"] = username_a
                    st.query_params["logged_in"] = "true"
                    st.query_params["role"] = "admin"
                    
                    st.success(f"✅ Welcome back Admin, {username_a}! 🛡️")
                    st.rerun()
                else:
                    st.error("❌ Invalid username, password, or role!")

        # Footer
        st.markdown("---")
        st.markdown("""
            <p style='text-align: center; color: #666; font-size: 0.9em;'>
                🌍 Join us in saving the planet! 🌱
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def signup_page():
    """Display signup page"""
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 10px auto 50px auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid #4CAF50;
        }
        .auth-title {
            text-align: center;
            color: #2e7d32;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .auth-icon {
            text-align: center;
            font-size: 5em;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Icon and Title
        st.markdown('<div class="auth-icon">🌱</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="auth-title">Join Us!</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Create your Climate Guardian account</p>', unsafe_allow_html=True)
        
        tab_person, tab_admin = st.tabs(["🧑 Person Signup", "🛡️ Admin Signup"])
        
        # Person Signup Tab
        with tab_person:
            with st.form("signup_form_person"):
                full_name_p = st.text_input("👨 Full Name", placeholder="Enter your full name", key="fn_p")
                email_p = st.text_input("📧 Email", placeholder="your.email@example.com", key="em_p")
                username_p = st.text_input("👤 Username", placeholder="Choose a username", key="usr_p")
                password_p = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="pwd_p")
                confirm_password_p = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="cpwd_p")
                
                terms_p = st.checkbox("I agree to help save the planet! 🌍", key="terms_p")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    signup_button_p = st.form_submit_button("🌟 Create Person Account", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("← Back to Login", use_container_width=True):
                        st.session_state['show_signup'] = False
                        st.rerun()
            
            if signup_button_p:
                if not all([full_name_p, email_p, username_p, password_p, confirm_password_p]):
                    st.error("⚠️ Please fill in all fields!")
                elif not terms_p:
                    st.error("⚠️ Please accept the terms to continue!")
                elif password_p != confirm_password_p:
                    st.error("❌ Passwords don't match!")
                elif len(password_p) < 6:
                    st.error("⚠️ Password must be at least 6 characters!")
                elif user_exists(username_p, email_p):
                    st.error("❌ Username or email already exists!")
                else:
                    if create_user(username_p, email_p, password_p, full_name_p, role='person'):
                        st.success("✅ Account created successfully! 🎉")
                        st.balloons()
                        st.info("👉 Please login with your credentials")
                        st.session_state['show_signup'] = False
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Error creating account. Please try again.")

        # Admin Signup Tab
        with tab_admin:
            with st.form("signup_form_admin"):
                full_name_a = st.text_input("👨 Full Name", placeholder="Enter your full name", key="fn_a")
                email_a = st.text_input("📧 Email", placeholder="your.email@example.com", key="em_a")
                username_a = st.text_input("👤 Username", placeholder="Choose a username", key="usr_a")
                password_a = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="pwd_a")
                confirm_password_a = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="cpwd_a")
                
                terms_a = st.checkbox("I agree to help save the planet! 🌍", key="terms_a")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    signup_button_a = st.form_submit_button("🌟 Create Admin Account", use_container_width=True)
                with col_btn2:
                    if st.form_submit_button("← Back to Login", use_container_width=True):
                        st.session_state['show_signup'] = False
                        st.rerun()
            
            if signup_button_a:
                if not all([full_name_a, email_a, username_a, password_a, confirm_password_a]):
                    st.error("⚠️ Please fill in all fields!")
                elif not terms_a:
                    st.error("⚠️ Please accept the terms to continue!")
                elif password_a != confirm_password_a:
                    st.error("❌ Passwords don't match!")
                elif len(password_a) < 6:
                    st.error("⚠️ Password must be at least 6 characters!")
                elif user_exists(username_a, email_a):
                    st.error("❌ Username or email already exists!")
                else:
                    if create_user(username_a, email_a, password_a, full_name_a, role='admin'):
                        st.success("✅ Admin Account created successfully! 🎉")
                        st.balloons()
                        st.info("👉 Please login with your credentials")
                        st.session_state['show_signup'] = False
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Error creating account. Please try again.")
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <p style='text-align: center; color: #666; font-size: 0.9em;'>
                Already have an account? Click "Back to Login" above! 🌿
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# LEADERBOARD FUNCTIONS
# ==========================================

def get_leaderboard_data():
    """Get sorted leaderboard data with rankings from CSV, calculating scores from activities."""
    try:
        df = pd.read_csv(USERS_DB)
        # Calculate eco score for each user from their activities
        df['eco_score'] = df['username'].apply(get_user_eco_score_from_activities)
        df = df.sort_values('eco_score', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1
        return df[['rank', 'username', 'full_name', 'eco_score']]
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['rank', 'username', 'full_name', 'eco_score'])

def get_user_eco_score_from_activities(username):
    """Calculate user's eco score by summing all their activities from the activity log"""
    try:
        df = pd.read_csv(ACTIVITIES_DB)
        user_activities = df[df['username'] == username]
        if not user_activities.empty:
            return round(user_activities['points'].sum(), 1)
        return 0
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return 0

def get_user_rank(username):
    """Get user's current global rank"""
    leaderboard = get_leaderboard_data()
    if not leaderboard.empty and 'username' in leaderboard.columns:
        user_row = leaderboard[leaderboard['username'] == username]
        if not user_row.empty:
            return int(user_row.iloc[0]['rank'])
    return None

def get_user_percentile(username):
    """Calculate the user's percentile based on their rank."""
    rank = get_user_rank(username)
    if rank is None:
        return 0

    leaderboard = get_leaderboard_data()
    total_users = len(leaderboard)

    if total_users <= 1:
        return 100

    # Percentile Rank = ( (N - R) / (N - 1) ) * 100
    # Where N is total users and R is rank.
    # A rank of 1 gets 100 percentile, a rank of N gets 0.
    percentile = ((total_users - rank) / (total_users - 1)) * 100
    return round(percentile, 1)

# ==========================================
# CERTIFICATE FUNCTIONS
# ==========================================

def generate_certificate_pdf(username, eco_score, rank, total_users):
    """Generate certificate PDF with ReportLab"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    w, h = landscape(letter)

    # Get full name from database
    user_info = get_user_info(username)
    full_name = user_info.get('full_name', username) if user_info else username

    # 🌿 Background
    c.setFillColor(colors.HexColor("#e9f7ef"))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # 🎀 Curved ribbon (top-left)
    c.setFillColor(colors.HexColor("#2e7d32"))
    path = c.beginPath()
    path.moveTo(0, h)
    path.curveTo(300, h-30, 400, h-120, 450, h-180)
    path.lineTo(450, h)
    path.close()
    c.drawPath(path, fill=1, stroke=0)

    # 🌱 Abstract leaf shapes (right side)
    c.setFillColor(colors.HexColor("#43a047"))
    leaf = c.beginPath()
    leaf.moveTo(w-200, 100)
    leaf.curveTo(w-50, 250, w-50, 450, w-220, 580)
    leaf.curveTo(w-160, 420, w-180, 260, w-200, 100)
    leaf.close()
    c.drawPath(leaf, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#66bb6a"))
    leaf2 = c.beginPath()
    leaf2.moveTo(w-260, 120)
    leaf2.curveTo(w-140, 280, w-160, 450, w-300, 600)
    leaf2.close()
    c.drawPath(leaf2, fill=1, stroke=0)

    # 🏅 Golden Award Seal
    cx, cy = w/2 + 220, h/2 + 50
    c.setFillColor(colors.HexColor("#f9a825"))
    c.circle(cx, cy, 45, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#ffd54f"))
    c.circle(cx, cy, 38, fill=1, stroke=0)

    c.setFillColor(colors.darkgreen)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(cx, cy+5, "BEST")
    c.drawCentredString(cx, cy-10, "AWARD")

    # 📜 Certificate Title
    c.setFillColor(colors.HexColor("#1b5e20"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w/2 - 100, h - 1.7*inch, "CERTIFICATE")

    c.setFont("Helvetica", 16)
    c.drawCentredString(w/2 - 100, h - 2.3*inch, "OF APPRECIATION")

    # 👤 Name (Full Name instead of username)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(w/2 - 100, h - 3.5*inch, full_name)

    # 📝 Content
    c.setFont("Helvetica", 14)
    c.drawCentredString(
        w/2 - 100,
        h - 4.2*inch,
        "For outstanding contribution towards climate sustainability"
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        w/2 - 100,
        h - 4.9*inch,
        f"ECO SCORE: {eco_score}"
    )

    c.setFont("Helvetica", 13)
    c.drawCentredString(
        w/2 - 100,
        h - 5.4*inch,
        f"Rank #{rank} among {total_users} Climate Guardians"
    )

    # ✍ Signatures (moved text above signature line)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(2.75*inch, 1.5*inch, "Director")
    c.line(1.5*inch, 1.2*inch, 4*inch, 1.2*inch)

    c.drawCentredString(w-2.75*inch, 1.5*inch, "Climate Guardian")
    c.line(w-4*inch, 1.2*inch, w-1.5*inch, 1.2*inch)

    # 📅 Date
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(
        w/2,
        0.7*inch,
        f"Issued on {datetime.now().strftime('%d %B %Y')}"
    )

    c.save()
    buffer.seek(0)
    return buffer

def issue_certificate(username):
    """Issue certificate to user (if eligible) and save to CSV."""
    is_eligible, eco_score = check_certificate_eligibility(username)
    
    if not is_eligible:
        return False, f"User must have at least 500 eco-points. Current score: {eco_score}"
    
    if get_certificate_info(username):
        return False, "Certificate already issued to this user"
    
    certificate_id = f"CERT_{username}_{int(datetime.now().timestamp())}"
    leaderboard = get_leaderboard_data()
    rank = get_user_rank(username) or len(leaderboard)
    total_users = len(leaderboard)
    
    try:
        df = pd.read_csv(CERTIFICATES_DB)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['certificate_id', 'username', 'eco_score', 'rank', 'issued_date'])
        
    new_cert = pd.DataFrame([{
        'certificate_id': certificate_id,
        'username': username,
        'eco_score': eco_score,
        'rank': rank,
        'issued_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    df = pd.concat([df, new_cert], ignore_index=True)
    df.to_csv(CERTIFICATES_DB, index=False)
    
    log_activity(username, "Certificate Issued", 50) # Award bonus points for getting a cert
    return True, certificate_id

def check_certificate_eligibility(username):
    """Check if user is eligible for certificate based on their activity score."""
    eco_score = get_user_eco_score_from_activities(username)
    return eco_score >= 500, eco_score

def get_certificate_info(username):
    """Get certificate information for a user from CSV."""
    try:
        df = pd.read_csv(CERTIFICATES_DB)
        cert = df[df['username'] == username]
        if not cert.empty:
            return cert.iloc[0].to_dict()
        return None
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None

def get_all_certificates():
    """Get all issued certificates from CSV."""
    try:
        return pd.read_csv(CERTIFICATES_DB)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['certificate_id', 'username', 'eco_score', 'rank', 'issued_date'])

def logout():
    """Logout user"""
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['user_info'] = None
    # Reset eco score on logout
    if 'eco_score' in st.session_state:
        st.session_state['eco_score'] = 0
    # Clear persistence
    st.query_params.clear()
    st.rerun()
