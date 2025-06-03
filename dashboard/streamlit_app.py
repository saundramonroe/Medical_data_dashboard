# pylint: disable=line-too-long
"""
Medical Data Analysis Dashboard

This Streamlit application provides an interactive dashboard for analyzing medical transcription data.
Users can upload CSV files, visualize data through charts, generate word clouds, and export results.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Configure page
st.set_page_config(
    page_title="Medical Data Analysis Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🩺 Medical Data Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📁 Data Upload & Controls")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type="csv",
    help="Upload your medical transcription CSV file"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None

# Process uploaded file
if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file)
        st.session_state.data = df
        # Clean column names
        df.columns = df.columns.str.strip()
        # Data preprocessing
        for col in ['description', 'medical_specialty', 'transcription', 'keywords']:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)
        # Calculate metrics
        if 'transcription' in df.columns:
            df['transcription_length'] = df['transcription'].str.len()
        if 'keywords' in df.columns:
            df['keywords_count'] = df['keywords'].str.split(',').str.len()
        st.sidebar.success(f"✅ Data loaded successfully! {len(df)} records found.")   
    except Exception as e:
        st.sidebar.error(f"Error loading file: {str(e)}")
        st.session_state.data = None

# Main dashboard
if st.session_state.data is not None:
    df = st.session_state.data
    # Sidebar controls
    st.sidebar.subheader("🎛️ Analysis Controls")
    # Specialty filter
    specialties = ['All'] + sorted(df['medical_specialty'].unique().tolist()) if 'medical_specialty' in df.columns else ['All']
    selected_specialty = st.sidebar.selectbox("Filter by Specialty:", specialties) 
    # Filter data
    if selected_specialty != 'All':
        filtered_df = df[df['medical_specialty'] == selected_specialty]
    else:
        filtered_df = df 
    # Chart type selector
    chart_type = st.sidebar.selectbox(
        "Chart Type:",
        ["Bar Chart", "Pie Chart", "Donut Chart"]
    )
    # Statistics Section
    st.header("📊 Key Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>{}</h2>
            <p>Total Records</p>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    with col2:
        specialties_count = filtered_df['medical_specialty'].nunique() if 'medical_specialty' in filtered_df.columns else 0
        st.markdown("""
        <div class="metric-card">
            <h2>{}</h2>
            <p>Medical Specialties</p>
        </div>
        """.format(specialties_count), unsafe_allow_html=True)
    with col3:
        avg_length = int(filtered_df['transcription_length'].mean()) if 'transcription_length' in filtered_df.columns else 0
        st.markdown("""
        <div class="metric-card">
            <h2>{:,}</h2>
            <p>Avg Text Length</p>
        </div>
        """.format(avg_length), unsafe_allow_html=True)
    with col4:
        avg_keywords = round(filtered_df['keywords_count'].mean(), 1) if 'keywords_count' in filtered_df.columns else 0
        st.markdown("""
        <div class="metric-card">
            <h2>{}</h2>
            <p>Avg Keywords</p>
        </div>
        """.format(avg_keywords), unsafe_allow_html=True)
    # Charts Section
    st.header("📈 Data Visualizations")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Medical Specialties Distribution") 
        if 'medical_specialty' in filtered_df.columns:
            specialty_counts = filtered_df['medical_specialty'].value_counts().head(10) 
            if chart_type == "Bar Chart":
                fig = px.bar(
                    x=specialty_counts.index, 
                    y=specialty_counts.values,
                    title="Medical Specialties",
                    labels={'x': 'Specialty', 'y': 'Count'}
                )
            elif chart_type == "Pie Chart":
                fig = px.pie(
                    values=specialty_counts.values, 
                    names=specialty_counts.index,
                    title="Medical Specialties"
                )
            else:  # Donut Chart
                fig = px.pie(
                    values=specialty_counts.values, 
                    names=specialty_counts.index,
                    title="Medical Specialties",
                    hole=0.4
                )    
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Text Length Distribution") 
        if 'transcription_length' in filtered_df.columns:
            fig = px.histogram(
                filtered_df, 
                x='transcription_length',
                title="Transcription Length Distribution",
                nbins=20
            )
            st.plotly_chart(fig, use_container_width=True)
    # Word Cloud Section
    st.header("☁️ Word Cloud Analysis")
    col1, col2 = st.columns(2)
    with col1:
        if 'keywords' in filtered_df.columns:
            # Generate word cloud
            all_keywords = ' '.join(filtered_df['keywords'].astype(str))
            if all_keywords.strip():
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis'
                ).generate(all_keywords)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Keywords Word Cloud', fontsize=16)
                st.pyplot(fig)
    with col2:
        st.subheader("Top Keywords")
        if 'keywords' in filtered_df.columns:
            # Get word frequencies
            all_keywords = ' '.join(filtered_df['keywords'].astype(str))
            words = re.findall(r'\b\w{3,}\b', all_keywords.lower())
            word_freq = Counter(words) 
            # Create DataFrame for top words
            top_words_df = pd.DataFrame(
                word_freq.most_common(15),
                columns=['Word', 'Frequency']
            )  
            if not top_words_df.empty:
                fig = px.bar(
                    top_words_df,
                    x='Frequency',
                    y='Word',
                    orientation='h',
                    title="Most Common Keywords"
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
    # Insights Section
    st.header("💡 Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'medical_specialty' in filtered_df.columns:
            top_specialty = filtered_df['medical_specialty'].mode().iloc[0]
            specialty_count = filtered_df['medical_specialty'].value_counts().iloc[0]
            
            st.info(f"""
            **🏆 Most Common Specialty** 
            {top_specialty}
            
            ({specialty_count} records)
            """)
    with col2:
        if 'transcription_length' in filtered_df.columns:
            avg_len = int(filtered_df['transcription_length'].mean())
            max_len = int(filtered_df['transcription_length'].max())    
            st.info(f"""
            **📏 Text Length Analysis** 
            Average: {avg_len:,} characters
            Maximum: {max_len:,} characters
            """)
    with col3:
        if 'keywords_count' in filtered_df.columns:
            avg_kw = round(filtered_df['keywords_count'].mean(), 1)
            max_kw = int(filtered_df['keywords_count'].max())
            st.info(f"""
            **🔍 Keywords Analysis**
            Average: {avg_kw} keywords
            Maximum: {max_kw} keywords
            """)
    # Data Table Section
    st.header("📋 Data Preview")
    # Display options
    show_rows = st.slider("Number of rows to display:", 5, 50, 10)
    # Display table
    display_columns = ['description', 'medical_specialty', 'sample_name']
    if 'transcription_length' in filtered_df.columns:
        display_columns.append('transcription_length')
    if 'keywords_count' in filtered_df.columns:
        display_columns.append('keywords_count')
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    st.dataframe(
        filtered_df[available_columns].head(show_rows),
        use_container_width=True
    )
    # Export Section
    st.header("💾 Export Results")
    col1, col2 = st.columns(2) 
    with col1:
        if st.button("📊 Download Analysis Summary"):
            summary = {
                'total_records': len(filtered_df),
                'specialties_count': filtered_df['medical_specialty'].nunique() if 'medical_specialty' in filtered_df.columns else 0,
                'avg_transcription_length': avg_length,
                'avg_keywords': avg_keywords
            } 
            summary_df = pd.DataFrame([summary])
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="Download Summary CSV",
                data=csv,
                file_name="medical_analysis_summary.csv",
                mime="text/csv"
            )
    with col2:
        if st.button("📄 Download Filtered Data"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Filtered CSV",
                data=csv,
                file_name="filtered_medical_data.csv",
                mime="text/csv"
            )
else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to the Medical Data Analysis Dashboard!
    This interactive dashboard helps you analyze medical transcription data with powerful visualizations and insights.
    ### 🚀 Getting Started:
    1. **Upload your CSV file** using the sidebar
    2. **Explore interactive visualizations** 
    3. **Filter by medical specialty**
    4. **Generate insights and export results**
    
    ### 📋 Expected CSV Format:
    Your CSV should contain columns like:
    - `description`: Brief description of the case
    - `medical_specialty`: Medical specialty/department  
    - `transcription`: Full medical transcription text
    - `keywords`: Relevant medical keywords
    - `sample_name`: Case or sample identifier
    
    ### 🎯 Features:
    - **Interactive Charts**: Bar, pie, and donut charts
    - **Word Cloud Analysis**: Visualize common medical terms
    - **Statistical Insights**: Key metrics and analysis
    - **Data Filtering**: Filter by specialty or other criteria
    - **Export Capabilities**: Download results and summaries
    
    Upload your data to begin analysis! 📊
    """)
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🩺 Medical Data Analysis Dashboard | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)