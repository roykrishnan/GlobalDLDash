import streamlit as st

def main():
    st.set_page_config(page_title="Redirecting to Hitting Dashboard", layout="wide")
    
    # URL of your Hitting app
    hitting_app_url = "https://hittingmock.streamlit.app/"
    
    st.title("Redirecting to Hitting Dashboard...")
    st.write(f"If you are not redirected automatically, please [click here]({hitting_app_url}).")
    
    # JavaScript for redirection
    redirect_js = f"""
    <script>
        var hittingAppUrl = "{hitting_app_url}";
        var countdown = 3;
        
        function updateCountdown() {{
            document.getElementById("countdown").innerHTML = countdown;
            if (countdown > 0) {{
                countdown -= 1;
                setTimeout(updateCountdown, 1000);
            }} else {{
                window.location.href = hittingAppUrl;
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
        window.location.href = "{hitting_app_url}";
        </script>
        """
        st.components.v1.html(js)

if __name__ == "__main__":
    main()
