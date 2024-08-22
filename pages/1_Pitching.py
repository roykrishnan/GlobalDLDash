import streamlit as st

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
    """
    
    # Use st.markdown with unsafe_allow_html for the JavaScript and countdown
    st.markdown(redirect_js, unsafe_allow_html=True)
    
    # Add a button for manual redirection
    if st.button("Redirect Now"):
        js = f"""
        <script>
        window.location.href = "{pitching_app_url}";
        </script>
        """
        st.components.v1.html(js)

if __name__ == "__main__":
    main()
