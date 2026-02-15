import streamlit as st
from rag_agent import GeorgianTaxRAGAgent
import os
from pathlib import Path


st.set_page_config(
    page_title=" Georgian Tax RAG",
    page_icon="🇬🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
    }
    .source-box {
        background-color: #fff9e6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffa500;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-header">🇬🇪 Georgian Tax Documents Q&A</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">საგადასახადო დოკუმენტების შესახებ კითხვა-პასუხი</p>', unsafe_allow_html=True)

st.markdown("---")


@st.cache_resource
def load_agent():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
       
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            st.info("გთხოვთ დააყენოთ API key Streamlit Cloud Secrets-ში")
            st.stop()
    return GeorgianTaxRAGAgent(api_key)


with st.sidebar:
    st.header(" ინფორმაცია")
    
    try:
        agent = load_agent()
        doc_count = agent.collection.count()
        st.success(f" სისტემა მზადაა!")
        st.info(f"დოკუმენტები ბაზაში: {doc_count} chunks")
    except Exception as e:
        st.error(f" შეცდომა: {e}")
        st.stop()
    
    st.markdown("---")
    
    st.subheader("💡 მაგალითები")
    example_questions = [
        "რა არის დღგ?",
        "როგორ ხდება დავების განხილვა?",
        "რა არის საგადასახადო შემოწმება?",
        "როგორ უნდა გავასაჩივრო გადაწყვეტილება?",
        "რა არის საგადასახადო მოთხოვნა?"
    ]
    
    for i, q in enumerate(example_questions):
        if st.button(q, key=f"example_{i}"):
            st.session_state.question = q
    
    st.markdown("---")
    
    st.subheader("ℹ️ როგორ მუშაობს")
    st.markdown("""
    1.  **ძებნა** - სისტემა ეძებს შესაბამის დოკუმენტებს
    2.  **ანალიზი** - Claude აანალიზებს კონტექსტს
    3.  **პასუხი** - გიბრუნებთ პასუხს წყაროების მითითებით
    """)
    
    st.markdown("---")
    st.caption("Powered by Claude Sonnet 4 ")


col1, col2 = st.columns([3, 1])

with col1:

    if 'question' not in st.session_state:
        st.session_state.question = ""
    
    question = st.text_input(
        " დასვით კითხვა ქართულად:",
        value=st.session_state.question,
        placeholder="მაგ: რა არის დღგ?",
        key="question_input"
    )

with col2:
    st.write("")  
    st.write("") 
    search_button = st.button("🔍 ძებნა", type="primary", use_container_width=True)


if search_button and question:
    with st.spinner("🔄 ვამუშავებ თქვენს კითხვას..."):
        try:
            
            result = agent.answer_question(question)
            
          
            st.markdown("###  პასუხი:")
            st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
            
            st.markdown("### 📚 გამოყენებული წყაროები:")
            sources = list(set(result['sources']))
            
            for i, source in enumerate(sources, 1):
                st.markdown(f'<div class="source-box"><b>{i}.</b> {source}</div>', unsafe_allow_html=True)
            
            with st.expander(" დამატებითი ინფორმაცია"):
                st.write(f"**გამოყენებული ჩანქების რაოდენობა:** {result['context_used']}")
                st.write(f"**სულ წყაროები:** {len(sources)}")
            
            st.session_state.question = ""
            
        except Exception as e:
            st.error(f" შეცდომა: {e}")
            st.info("გთხოვთ, სცადოთ თავიდან ან დაუკავშირდით ადმინისტრატორს.")

elif search_button and not question:
    st.warning(" გთხოვთ, შეიყვანოთ კითხვა!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with  for Georgian Tax Administration | 
    <a href='https://github.com/your-username/georgian-tax-rag'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
