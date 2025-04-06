import streamlit as st

def render_footer():
    st.markdown("""
<style>
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #1f2833;
    color: #c5c6c7;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    z-index:9999;
}
</style>
<footer>
    ⏰ Heure actuelle : <span id='time'></span> · 🤖 CogOS prêt à réfléchir pour vous.
</footer>
<script>
function updateTime() {
    const now = new Date();
    document.getElementById('time').textContent = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();
</script>
""", unsafe_allow_html=True)
