import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Xerpihan Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data with improved error handling
@st.cache_data
def load_data():
    try:
        combined_data = pd.read_csv("xerpihan_combined_data.csv")
        growth_data = pd.read_csv("xerpihan_combined_data_with_growth.csv")
        metrics = pd.read_csv("xerpihan_comprehensive_metrics.csv")
        final_summary = pd.read_csv("xerpihan_final_summary.csv")
        financial_metrics = pd.read_csv("xerpihan_financial_metrics.csv")
        forecast_combined = pd.read_csv("xerpihan_forecast_combined.csv")
        return combined_data, growth_data, metrics, final_summary, financial_metrics, forecast_combined
    except FileNotFoundError as e:
        st.error(f"Error: File '{e.filename}' tidak ditemukan. Pastikan semua file CSV ada di direktori yang benar.")
        return None, None, None, None, None, None
    except Exception as e:
        st.error(f"Error saat memuat data: {str(e)}. Periksa format file CSV dan pastikan kolom yang diharapkan ada.")
        return None, None, None, None, None, None

# Sidebar
st.sidebar.title("Navigasi")
page = st.sidebar.radio(
    "Pilih halaman",
    ["Overview", "Financial Analysis", "Risk Analysis", "Portfolio Optimization", "Forecasting"]
)

# Load data once
data = load_data()
if data[0] is None:  # Jika combined_data adalah None, berarti ada error
    st.stop()

combined_data, growth_data, metrics, final_summary, financial_metrics, forecast_combined = data

# Overview Page
if page == "Overview":
    st.title("Xerpihan Financial Analysis Dashboard")
    st.header("Indikator Kinerja Utama")
    
    try:
        # Convert numeric columns
        metrics['Revenue_CAGR'] = pd.to_numeric(metrics['Revenue_CAGR'], errors='coerce')
        metrics['Avg_EBITDA_Margin'] = pd.to_numeric(metrics['Avg_EBITDA_Margin'], errors='coerce')
        metrics['Cost_to_Revenue'] = pd.to_numeric(metrics['Cost_to_Revenue'], errors='coerce')
        
        # Check for NaN after conversion
        if metrics[['Revenue_CAGR', 'Avg_EBITDA_Margin', 'Cost_to_Revenue']].isnull().any().any():
            st.warning("Beberapa data numerik tidak valid dan diubah menjadi NaN. Periksa data Anda.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Rata-rata Revenue CAGR", value=f"{metrics['Revenue_CAGR'].mean():.2f}%")
        with col2:
            st.metric(label="Rata-rata EBITDA Margin", value=f"{metrics['Avg_EBITDA_Margin'].mean():.2f}%")
        with col3:
            st.metric(label="Rata-rata Efisiensi Biaya", value=f"{metrics['Cost_to_Revenue'].mean():.2f}%")
    except Exception as e:
        st.error(f"Error saat mengkonversi data numerik: {str(e)}")
    
    # Revenue Trends
    st.subheader("Tren Pendapatan per Skenario")
    try:
        revenue_data = combined_data[combined_data['Category'] == 'Pendapatan']
        if revenue_data.empty:
            st.error("Error: Tidak ada data pendapatan yang ditemukan.")
        else:
            years = [str(year) for year in range(2024, 2032)]
            if not all(year in revenue_data.columns for year in years):
                st.error("Error: Beberapa kolom tahun tidak ada di data pendapatan.")
            else:
                fig = px.line(revenue_data, x='Scenario', y=years, title='Tren Pendapatan (2024-2031)')
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi tren pendapatan: {str(e)}")
    
    # Data Download
    st.subheader("Unduh Data")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="Unduh Financial Metrics", data=financial_metrics.to_csv(index=False), file_name="financial_metrics.csv", mime="text/csv")
    with col2:
        st.download_button(label="Unduh Summary Data", data=final_summary.to_csv(index=False), file_name="final_summary.csv", mime="text/csv")
    
    # Data Exploration
    st.subheader("Eksplorasi Data")
    dataset_name = st.selectbox("Pilih dataset untuk dieksplorasi", ["Combined Data", "Growth Data", "Metrics", "Final Summary", "Financial Metrics"])
    datasets = {"Combined Data": combined_data, "Growth Data": growth_data, "Metrics": metrics, "Final Summary": final_summary, "Financial Metrics": financial_metrics}
    st.dataframe(datasets[dataset_name])

# Financial Analysis Page
elif page == "Financial Analysis":
    st.title("Analisis Kinerja Keuangan")
    
    st.subheader("Metrik Keuangan Utama per Skenario")
    try:
        metrics_fig = px.bar(financial_metrics, x='Scenario', y=['Revenue_CAGR', 'Avg_EBITDA_Margin', 'Avg_Net_Margin'], barmode='group', title='Perbandingan Metrik Keuangan')
        st.plotly_chart(metrics_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi metrik keuangan: {str(e)}")
    
    st.subheader("Analisis Pertumbuhan")
    try:
        growth_fig = px.line(final_summary, x='Scenario', y=['Revenue_CAGR', 'EBITDA_CAGR'], title='Metrik Pertumbuhan per Skenario')
        st.plotly_chart(growth_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi analisis pertumbuhan: {str(e)}")
    
    # Custom Visualization
    st.subheader("Visualisasi Kustom")
    try:
        numeric_cols = financial_metrics.select_dtypes(include=[np.number]).columns
        if numeric_cols.empty:
            st.error("Error: Tidak ada kolom numerik yang ditemukan di financial_metrics.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("Pilih metrik sumbu X", numeric_cols)
            with col2:
                y_axis = st.selectbox("Pilih metrik sumbu Y", numeric_cols)
            custom_fig = px.scatter(financial_metrics, x=x_axis, y=y_axis, color='Scenario', 
                                  title=f'{y_axis} vs {x_axis} per Skenario', trendline="ols")
            st.plotly_chart(custom_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi kustom: {str(e)}")

# Risk Analysis Page
elif page == "Risk Analysis":
    st.title("Analisis Risiko")
    
    st.subheader("Metrik Risiko per Skenario")
    try:
        risk_data = pd.DataFrame({
            'Scenario': metrics['Scenario'], 
            'Revenue_Volatility': metrics['Revenue_Volatility'], 
            'Margin_Volatility': metrics['Margin_Volatility']
        })
        risk_fig = px.bar(risk_data, x='Scenario', y=['Revenue_Volatility', 'Margin_Volatility'], 
                         barmode='group', title='Metrik Volatilitas per Skenario')
        st.plotly_chart(risk_fig, use_container_width=True)
    except KeyError as e:
        st.error(f"Error: Kolom {str(e)} tidak ditemukan di data metrics.")
    except Exception as e:
        st.error(f"Error saat membuat visualisasi risiko: {str(e)}")
    
    # Risk Decomposition
    st.subheader("Analisis Dekomposisi Risiko")
    try:
        risk_components = pd.DataFrame({
            'Scenario': ['Optimistic', 'Moderate', 'Pessimistic'], 
            'Market_Risk': [0.15, 0.12, 0.10], 
            'Credit_Risk': [0.08, 0.07, 0.06], 
            'Operational_Risk': [0.05, 0.04, 0.03]
        })
        decomp_fig = px.bar(risk_components.melt(id_vars=['Scenario'], var_name='Risk_Type', value_name='Risk_Level'), 
                           x='Scenario', y='Risk_Level', color='Risk_Type', title='Dekomposisi Risiko per Skenario')
        st.plotly_chart(decomp_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi dekomposisi risiko: {str(e)}")

# Portfolio Optimization Page
elif page == "Portfolio Optimization":
    st.title("Optimasi Portofolio")
    
    st.subheader("Alokasi Portofolio per Metode")
    try:
        portfolio_data = pd.DataFrame({
            'Method': ['HJB', 'Markowitz', 'Black-Litterman', 'RL'], 
            'Optimistic': [1.000, 0.333, 0.407, 0.055], 
            'Moderate': [0.000, 0.333, 0.407, 0.775], 
            'Pessimistic': [0.000, 0.333, 0.296, 0.170]
        })
        allocation_fig = px.bar(portfolio_data.melt(id_vars=['Method'], var_name='Scenario', value_name='Weight'), 
                              x='Method', y='Weight', color='Scenario', title='Alokasi Portofolio per Metode')
        st.plotly_chart(allocation_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi alokasi portofolio: {str(e)}")
    
    st.subheader("Metrik Kinerja per Metode")
    try:
        performance_data = pd.DataFrame({
            'Method': ['HJB', 'Markowitz', 'Black-Litterman', 'RL'], 
            'Expected_Return': [0.1854, 0.1400, 0.0786, 0.1348], 
            'Sharpe_Ratio': [1.017e15, 1.985e15, 3.679e14, 1.746e15]
        })
        metrics_fig = px.scatter(performance_data, x='Expected_Return', y='Sharpe_Ratio', color='Method', size=[20]*4, title='Analisis Risiko-Hasil')
        st.plotly_chart(metrics_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi metrik kinerja: {str(e)}")

# Forecasting Page
elif page == "Forecasting":
    st.title("Peramalan Keuangan")
    
    st.subheader("Peramalan Pendapatan per Skenario")
    try:
        years = [str(year) for year in range(2024, 2032)]
        forecast_data = forecast_combined[forecast_combined['Category'] == 'Pendapatan']
        if forecast_data.empty:
            st.error("Error: Tidak ada data peramalan pendapatan yang ditemukan.")
        else:
            if not all(year in forecast_data.columns for year in years):
                st.error("Error: Beberapa kolom tahun tidak ada di data peramalan.")
            else:
                forecast_fig = px.line(forecast_data, x='Scenario', y=years, title='Peramalan Pendapatan (2024-2031)')
                st.plotly_chart(forecast_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi peramalan pendapatan: {str(e)}")
    
    st.subheader("Analisis Tingkat Pertumbuhan")
    try:
        growth_cols = [col for col in growth_data.columns if 'Growth' in col]
        if not growth_cols:
            st.error("Error: Tidak ada kolom pertumbuhan yang ditemukan di growth_data.")
        else:
            growth_fig = px.box(growth_data.melt(id_vars=['Scenario'], value_vars=growth_cols), x='Scenario', y='value', title='Distribusi Tingkat Pertumbuhan per Skenario')
            st.plotly_chart(growth_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error saat membuat visualisasi analisis pertumbuhan: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Xerpihan Financial Analysis Dashboard | Dibuat dengan Streamlit")
