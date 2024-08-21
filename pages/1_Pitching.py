import streamlit as st
import time

def main():
    st.set_page_config(page_title="Redirecting to Pitching Dashboard", layout="wide")
    
    # URL of your pitching app
    pitching_app_url = "https://pitchingmock.streamlit.app/"
    
    st.title("Redirecting to Pitching Dashboard...")
    st.write(f"If you are not redirected automatically, please [click here]({pitching_app_url}).")
    
    # JavaScript for redirection
    redirect_js = f"""
    <script>
        var pitchingAppUrl = "{pitching_app_url}";
        var countdown = 3;
        
        function updateCountdown() {{
            document.getElementById("countdown").innerHTML = countdown;
            if (countdown > 0) {{
                countdown -= 1;
                setTimeout(updateCountdown, 1000);
            }} else {{
                window.location.href = pitchingAppUrl;
            }}
        }}
        
        updateCountdown();
    </script>
    <p>Redirecting in <span id='countdown'>3</span> seconds...</p>
    <meta http-equiv="refresh" content="3;url={pitching_app_url}">
    """
    
    # Use st.markdown with unsafe_allow_html for the JavaScript, countdown, and meta refresh
    st.markdown(redirect_js, unsafe_allow_html=True)
    
    # Streamlit's native functionality to show a spinner while waiting
    with st.spinner("Redirecting..."):
        time.sleep(3)

if __name__ == "__main__":
    main()
