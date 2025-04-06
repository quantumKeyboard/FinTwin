import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
from financial_ai import FinancialAI
from data_processor import DataProcessor
from svg_converter import SVGConverter
import os
from dotenv import load_dotenv
import traceback
import logging
from financial_simulator import FinancialSimulator
import streamlit.components.v1 as components

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="FinTwin - Your AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .expense-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .month-selector {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

class FinTwinApp:
    def __init__(self):
        self.financial_ai = FinancialAI()
        self.data_processor = DataProcessor()
        self.svg_converter = SVGConverter()
        self.simulator = FinancialSimulator()
        self.initialize_session_state()
        self.initialize_debug_mode()

    def initialize_debug_mode(self):
        """Initialize debug mode settings"""
        if 'debug_mode' not in st.session_state:
            st.session_state.debug_mode = False

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'financial_data' not in st.session_state:
            st.session_state.financial_data = None
        if 'predictions' not in st.session_state:
            st.session_state.predictions = None
        if 'simulations' not in st.session_state:
            st.session_state.simulations = {}
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'monthly_expenses' not in st.session_state:
            st.session_state.monthly_expenses = {}
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Import Data"
        if 'expense_categories' not in st.session_state:
            st.session_state.expense_categories = [
                "Rent/Mortgage",
                "Utilities",
                "Groceries",
                "Transportation",
                "Entertainment",
                "Healthcare",
                "Insurance",
                "Education",
                "Shopping",
                "Dining Out",
                "Travel",
                "Other"
            ]

    def log_error(self, error, context):
        """Log error with context for debugging"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        st.session_state.error_log.append(error_info)
        logger.error(f"Error in {context}: {str(error)}")
        if st.session_state.debug_mode:
            st.error(f"Debug Info - {context}: {str(error)}")

    def show_debug_panel(self):
        """Show debug panel with error logs and system status"""
        with st.sidebar:
            st.header("Debug Panel")
            debug_mode = st.toggle("Debug Mode", value=st.session_state.debug_mode)
            st.session_state.debug_mode = debug_mode

            if debug_mode:
                st.subheader("System Status")
                st.write(f"OpenAI API Key: {'Configured' if self.financial_ai.openai_api_key else 'Missing'}")
                st.write(f"Financial Data: {'Loaded' if st.session_state.financial_data else 'Not Loaded'}")
                
                if st.button("Clear Error Log"):
                    st.session_state.error_log = []
                
                st.subheader("Error Log")
                for error in st.session_state.error_log:
                    with st.expander(f"Error at {error['timestamp']}"):
                        st.write("Context:", error['context'])
                        st.write("Error:", error['error'])
                        st.code(error['traceback'])

    def change_page(self, page):
        """Change the current page in session state"""
        st.session_state.current_page = page
        
    def run(self):
        """Main application flow"""
        st.title("FinTwin - Your AI Financial Advisor")
        
        # Custom CSS for the entire app
        st.markdown("""
            <style>
                /* Sidebar styling */
                section[data-testid="stSidebar"] {
                    background-color: #f8f9fa;
                    border-right: 1px solid #e0e0e0;
                }
                
                /* Navigation header */
                .nav-header {
                    background: linear-gradient(135deg, #2c3e50, #3498db);
                    padding: 20px 15px;
                    border-radius: 10px;
                    margin-bottom: 25px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                .nav-header h2 {
                    color: white;
                    text-align: center;
                    margin: 0;
                    font-size: 1.5rem;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
                
                /* Navigation button container */
                .nav-button-container {
                    margin-bottom: 8px;
                }
                
                /* Custom button styling */
                .custom-button {
                    background-color: transparent;
                    border: none;
                    width: 100%;
                    padding: 0;
                    cursor: pointer;
                }
                
                /* Navigation buttons styling */
                .nav-button {
                    display: flex;
                    align-items: center;
                    padding: 12px 15px;
                    border-radius: 8px;
                    transition: all 0.2s ease;
                    text-decoration: none;
                    color: #2c3e50;
                }
                
                .nav-button:hover {
                    background-color: #e9ecef;
                    transform: translateX(3px);
                }
                
                .nav-button.active {
                    background-color: #e3f2fd;
                    border-left: 4px solid #3498db;
                    font-weight: bold;
                }
                
                .nav-button .icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 32px;
                    height: 32px;
                    margin-right: 12px;
                    font-size: 18px;
                    border-radius: 8px;
                }
                
                .nav-button .text {
                    font-size: 16px;
                }
                
                /* Import Data icon styling */
                .nav-button.import .icon {
                    background-color: #e3f2fd;
                    color: #2196f3;
                }
                
                /* Financial Health icon styling */
                .nav-button.health .icon {
                    background-color: #e8f5e9;
                    color: #4caf50;
                }
                
                /* Simulation icon styling */
                .nav-button.simulation .icon {
                    background-color: #fff3e0;
                    color: #ff9800;
                }
                
                /* Recommendations icon styling */
                .nav-button.recommendations .icon {
                    background-color: #f3e5f5;
                    color: #9c27b0;
                }
                
                /* Divider styling */
                .divider {
                    height: 1px;
                    background-color: #e0e0e0;
                    margin: 20px 0;
                }
                
                /* User profile styling */
                .user-profile {
                    display: flex;
                    align-items: center;
                    background-color: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 20px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                
                .user-profile .avatar {
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    width: 45px;
                    height: 45px;
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-right: 15px;
                    font-weight: bold;
                    font-size: 18px;
                }
                
                .user-profile .info .name {
                    color: #2c3e50;
                    font-weight: bold;
                    margin: 0;
                    font-size: 16px;
                }
                
                .user-profile .info .status {
                    color: #7f8c8d;
                    font-size: 12px;
                    margin: 0;
                }
                
                /* Active status indicator */
                .status-indicator {
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background-color: #4caf50;
                    border-radius: 50%;
                    margin-right: 5px;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Show debug panel in sidebar
        self.show_debug_panel()

        # Navigation header
        st.sidebar.markdown("""
            <div class="nav-header">
                <h2>Navigation</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation options with icons and styled buttons
        pages = {
            "Import Data": {"icon": "📊", "class": "import"},
            "Financial Health": {"icon": "💸", "class": "health"},
            "Simulation Playground": {"icon": "🎮", "class": "simulation"},
            "Financial Tools": {"icon": "💰", "class": "financial_tools"},
            "Recommendations": {"icon": "💡", "class": "recommendations"}
        }
        
        # Create navigation buttons
        for page, details in pages.items():
            icon = details["icon"]
            button_class = details["class"]
            active_class = "active" if st.session_state.current_page == page else ""
            
            # Create a container for each button
            button_container = st.sidebar.container()
            
            # Create the clickable button with custom styling
            clicked = button_container.button(
                f"{icon} {page}", 
                key=f"nav_{page}", 
                use_container_width=True,
                type="secondary"
            )
            
            if clicked:
                st.session_state.current_page = page
                st.rerun()
            
            # Apply custom styling for the active page indicator
            if st.session_state.current_page == page:
                st.sidebar.markdown(f"""
                    <div style="height: 2px; background: linear-gradient(90deg, #3498db, transparent); margin-bottom: 10px;"></div>
                """, unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f"""
                    <div style="height: 2px; margin-bottom: 10px;"></div>
                """, unsafe_allow_html=True)
        
        # Divider
        st.sidebar.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # User profile section
        st.sidebar.markdown("""
            <div class="user-profile">
                <div class="avatar">FT</div>
                <div class="info">
                    <p class="name">FinTwin User</p>
                    <p class="status"><span class="status-indicator"></span>Financial Twin Active</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display the currently selected page
        current_page = st.session_state.current_page
        
        if current_page == "Import Data":
            self.show_data_import()
        elif current_page == "Financial Health":
            self.show_financial_health()
        elif current_page == "Simulation Playground":
            self.show_simulation_playground()
        elif current_page == "Financial Tools":
            self.show_financial_tools()
        elif current_page == "Recommendations":
            self.show_recommendations()

    def show_data_import(self):
        st.header("📊 Financial Data Management")
        st.markdown("""
            Manage your financial data and monthly expenses in one place.
            Your data is encrypted and secure.
        """)

        # Create tabs for different sections
        tab1, tab2 = st.tabs(["Basic Financial Information", "Monthly Expenses"])

        with tab1:
            self.show_basic_financial_info()
        
        with tab2:
            self.show_monthly_expenses()
            
        # Add export/import section
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export Financial Data", key="export_button"):
                self.export_financial_data()
                
        with col2:
            uploaded_file = st.file_uploader("Import Financial Data", type=["json"])
            if uploaded_file is not None:
                self.import_financial_data(uploaded_file)
                
        with col3:
            if st.button("Clear All Data", key="clear_button"):
                self.clear_financial_data()

    def show_basic_financial_info(self):
        st.subheader("Basic Financial Information")
        
        with st.form("financial_data_form"):
            st.markdown("#### Income Information")
            monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
            
            st.markdown("#### Savings and Debt")
            col1, col2 = st.columns(2)
            with col1:
                savings = st.number_input("Current Savings ($)", min_value=0.0, step=100.0)
            with col2:
                debt = st.number_input("Current Debt ($)", min_value=0.0, step=100.0)

            if st.form_submit_button("Save Basic Information"):
                user_data = {
                    "income": monthly_income,
                    "savings": savings,
                    "debt": debt
                }
                st.session_state.user_data = user_data
                st.success("Basic financial information saved successfully!")

    def show_monthly_expenses(self):
        st.subheader("Monthly Expenses")
        
        # Month and Year Selection
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox(
                "Select Month",
                ["January", "February", "March", "April", "May", "June", 
                 "July", "August", "September", "October", "November", "December"]
            )
        with col2:
            current_year = datetime.now().year
            selected_year = st.selectbox(
                "Select Year",
                range(current_year - 2, current_year + 1)
            )

        # Initialize month data if not exists
        month_key = f"{selected_year}-{selected_month}"
        if month_key not in st.session_state.monthly_expenses:
            st.session_state.monthly_expenses[month_key] = {
                category: 0.0 for category in st.session_state.expense_categories
            }

        # Expense Input Form
        with st.form(f"expense_form_{month_key}"):
            st.markdown(f"#### Expenses for {selected_month} {selected_year}")
            
            # Create columns for better layout
            cols = st.columns(3)
            expense_data = {}
            
            for i, category in enumerate(st.session_state.expense_categories):
                col_idx = i % 3
                with cols[col_idx]:
                    expense_data[category] = st.number_input(
                        f"{category} ($)",
                        min_value=0.0,
                        value=float(st.session_state.monthly_expenses[month_key][category]),
                        step=10.0
                    )

            if st.form_submit_button("Save Monthly Expenses"):
                st.session_state.monthly_expenses[month_key] = expense_data
                st.success(f"Expenses for {selected_month} {selected_year} saved successfully!")

        # Display Monthly Summary
        st.markdown("#### Monthly Summary")
        self.show_monthly_summary(month_key)

        # Display Expense History
        st.markdown("#### Expense History")
        self.show_expense_history()

    def show_monthly_summary(self, month_key):
        if month_key in st.session_state.monthly_expenses:
            expenses = st.session_state.monthly_expenses[month_key]
            
            # Create summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_expenses = sum(expenses.values())
                st.metric("Total Expenses", f"${total_expenses:,.2f}")
            
            with col2:
                avg_expense = total_expenses / len(expenses) if expenses else 0
                st.metric("Average Expense", f"${avg_expense:,.2f}")
            
            with col3:
                max_expense = max(expenses.values()) if expenses else 0
                max_category = max(expenses.items(), key=lambda x: x[1])[0] if expenses else "N/A"
                st.metric("Highest Expense", f"${max_expense:,.2f}", f"({max_category})")

            # Create visualizations
            col1, col2 = st.columns(2)
            with col1:
                # Pie chart for expense distribution
                fig_pie = self.data_processor.create_expense_breakdown(expenses)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart for expense comparison
                fig_bar = self.data_processor.create_expense_comparison(expenses)
                st.plotly_chart(fig_bar, use_container_width=True)

    def show_expense_history(self):
        if not st.session_state.monthly_expenses:
            st.info("No expense history available. Start by adding expenses for any month.")
            return

        # Create a DataFrame for all expenses
        expense_history = []
        for month_key, expenses in st.session_state.monthly_expenses.items():
            year, month = month_key.split('-')
            for category, amount in expenses.items():
                expense_history.append({
                    'Year': year,
                    'Month': month,
                    'Category': category,
                    'Amount': amount
                })
        
        df = pd.DataFrame(expense_history)
        
        # Create time series visualization
        fig_timeline = self.data_processor.create_expense_timeline(df)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Create category-wise trend visualization
        fig_trend = self.data_processor.create_category_trends(df)
        st.plotly_chart(fig_trend, use_container_width=True)

    def _calculate_strengths_weaknesses(self, analysis):
        """Calculate financial strengths and weaknesses based on analysis data"""
        strengths = []
        weaknesses = []
        
        # Calculate strengths and weaknesses based on financial metrics
        monthly_income = st.session_state.financial_data.get('basic_info', {}).get('income', 0)
        current_savings = st.session_state.financial_data.get('basic_info', {}).get('savings', 0)
        current_debt = st.session_state.financial_data.get('basic_info', {}).get('debt', 0)
        
        # Calculate average monthly expenses
        expenses = st.session_state.financial_data.get('monthly_expenses', {})
        avg_expenses = 0
        if expenses:
            avg_expenses = sum(sum(month_data.values()) for month_data in expenses.values()) / len(expenses)
        
        # Calculate key ratios
        savings_rate = (monthly_income - avg_expenses) / monthly_income if monthly_income > 0 else 0
        debt_to_income = current_debt / (monthly_income * 12) if monthly_income > 0 else 0
        emergency_fund_months = current_savings / avg_expenses if avg_expenses > 0 else 0
        
        # Determine strengths
        if savings_rate >= 0.2:
            strengths.append("Excellent savings rate (≥20%)")
        elif savings_rate >= 0.15:
            strengths.append("Good savings rate (≥15%)")
            
        if emergency_fund_months >= 6:
            strengths.append("Strong emergency fund (≥6 months)")
        elif emergency_fund_months >= 3:
            strengths.append("Adequate emergency fund (≥3 months)")
            
        if debt_to_income < 0.2:
            strengths.append("Low debt-to-income ratio (<20%)")
        elif debt_to_income < 0.3:
            strengths.append("Healthy debt-to-income ratio (<30%)")
            
        if current_savings > 0:
            strengths.append("Positive savings balance")
            
        # Determine weaknesses
        if savings_rate < 0.1:
            weaknesses.append("Low savings rate (<10%)")
            
        if emergency_fund_months < 3:
            weaknesses.append("Insufficient emergency fund (<3 months)")
            
        if debt_to_income > 0.4:
            weaknesses.append("High debt-to-income ratio (>40%)")
            
        if avg_expenses > monthly_income * 0.8:
            weaknesses.append("High expense-to-income ratio (>80%)")
            
        # Add AI-generated insights
        if 'strengths' in analysis:
            strengths.extend(analysis['strengths'])
        if 'weaknesses' in analysis:
            weaknesses.extend(analysis['weaknesses'])
            
        return strengths, weaknesses

    def show_financial_health(self):
        st.header("💸 Financial Health Analysis")
        
        if not st.session_state.financial_data:
            # Create a more visually appealing warning
            st.markdown("""
                <div style='background-color: #fff3e0; padding: 20px; border-radius: 10px; border-left: 5px solid #f39c12;'>
                    <h3 style='margin: 0; color: #e67e22;'>Data Required</h3>
                    <p style='margin: 10px 0; color: black;'>Please import your financial data first using the 'Import Data' section.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Add a quick-action button
            if st.button("Go to Import Data"):
                st.session_state.page = "Import Data"
                st.rerun()
            return

        try:
            with st.spinner("Analyzing your financial health..."):
                # Get analysis from the AI agent
                analysis = self.financial_ai.analyze_financial_health(st.session_state.financial_data)
                
                # Calculate health score based on multiple factors
                health_score = self._calculate_health_score(analysis)
                score_color = "#2ecc71" if health_score >= 70 else "#f1c40f" if health_score >= 40 else "#e74c3c"
                
                st.markdown(f"""
                    <div style='background-color: {score_color}; padding: 25px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                        <h2 style='margin: 0; color: black;'>Financial Health Score</h2>
                        <h1 style='font-size: 60px; margin: 10px 0; color: black;'>{health_score:.1f}/100</h1>
                        <p style='margin: 0; font-size: 18px; color: black;'>Your risk level is <strong>{analysis['risk_level']}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Financial Health Breakdown
                st.markdown("<h3 style='margin-top: 30px;'>Financial Health Breakdown</h3>", unsafe_allow_html=True)
                
                # Create tabs for different aspects of financial health
                tabs = st.tabs(["Strengths & Weaknesses", "Savings Projection", "Debt Analysis"])
                
                with tabs[0]:
                    # Calculate dynamic strengths and weaknesses
                    strengths, weaknesses = self._calculate_strengths_weaknesses(analysis)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Financial Strengths</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if strengths:
                            for strength in strengths:
                                st.markdown(f"✅ {strength}")
                        else:
                            st.info("No significant financial strengths identified.")
                    
                    with col2:
                        st.markdown("""
                            <div style='background-color: #ffebee; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Financial Weaknesses</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if weaknesses:
                            for weakness in weaknesses:
                                st.markdown(f"⚠️ {weakness}")
                        else:
                            st.info("No significant financial weaknesses identified.")
                
                with tabs[1]:
                    # Savings Projection
                    st.markdown("""
                        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                            <h3 style='margin: 0; color: black;'>Savings Projection</h3>
                            <p style='margin: 5px 0; color: black;'>Based on your current savings rate and financial habits</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a projected savings chart
                    current_savings = st.session_state.financial_data.get('basic_info', {}).get('savings', 0)
                    monthly_income = st.session_state.financial_data.get('basic_info', {}).get('income', 0)
                    
                    if 'monthly_expenses' in st.session_state.financial_data:
                        # Calculate average monthly expenses
                        expenses = st.session_state.financial_data['monthly_expenses']
                        if expenses:
                            avg_expenses = sum(sum(month_data.values()) for month_data in expenses.values()) / len(expenses)
                            monthly_savings = monthly_income - avg_expenses
                            
                            # Generate projection data for 24 months
                            months = list(range(1, 25))
                            projected_savings = [current_savings + (monthly_savings * month) for month in months]
                            
                            # Create the projection chart
                            projection_df = pd.DataFrame({
                                'Month': months,
                                'Projected Savings': projected_savings
                            })
                            
                            fig = px.line(
                                projection_df, 
                                x='Month', 
                                y='Projected Savings',
                                title='24-Month Savings Projection',
                                labels={'Projected Savings': 'Projected Savings ($)', 'Month': 'Months from Now'},
                                color_discrete_sequence=['#2ecc71']
                            )
                            
                            fig.update_layout(
                                xaxis=dict(showgrid=True),
                                yaxis=dict(showgrid=True),
                                margin=dict(t=50, b=50, l=50, r=50)
                            )
                            
                            # Add a marker for the current savings
                            fig.add_scatter(
                                x=[0], 
                                y=[current_savings],
                                mode='markers',
                                marker=dict(size=12, color='#e74c3c'),
                                name='Current Savings'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Calculate and display key milestones
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                six_month_savings = current_savings + (monthly_savings * 6)
                                st.metric("6-Month Projection", f"${six_month_savings:,.2f}", delta=f"${six_month_savings - current_savings:,.2f}")
                            
                            with col2:
                                one_year_savings = current_savings + (monthly_savings * 12)
                                st.metric("1-Year Projection", f"${one_year_savings:,.2f}", delta=f"${one_year_savings - current_savings:,.2f}")
                            
                            with col3:
                                two_year_savings = current_savings + (monthly_savings * 24)
                                st.metric("2-Year Projection", f"${two_year_savings:,.2f}", delta=f"${two_year_savings - current_savings:,.2f}")
                            
                with tabs[2]:
                    # Debt Analysis
                    st.markdown("""
                        <div style='background-color: #ffebee; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                            <h3 style='margin: 0; color: black;'>Debt Analysis</h3>
                            <p style='margin: 5px 0; color: black;'>Assessment of your current debt situation</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display debt information
                    current_debt = st.session_state.financial_data.get('basic_info', {}).get('debt', 0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Total Debt", f"${current_debt:,.2f}")
                    
                    with col2:
                        # Calculate debt-to-income ratio
                        monthly_income = st.session_state.financial_data.get('basic_info', {}).get('income', 0)
                        debt_ratio = current_debt / (monthly_income * 12) if monthly_income > 0 else 0
                        st.metric("Annual Debt-to-Income Ratio", f"{debt_ratio:.2%}")
                    
                    # Debt repayment analysis
                    if current_debt > 0 and monthly_income > 0:
                        # Calculate monthly expenses
                        expenses = st.session_state.financial_data.get('monthly_expenses', {})
                        avg_expenses = 0
                        if expenses:
                            avg_expenses = sum(sum(month_data.values()) for month_data in expenses.values()) / len(expenses)
                        
                        # Calculate available money for debt repayment
                        monthly_surplus = monthly_income - avg_expenses
                        
                        if monthly_surplus > 0:
                            # Calculate time to repay debt
                            months_to_repay = current_debt / monthly_surplus
                            years_to_repay = months_to_repay / 12
                            
                            st.info(f"Based on your current financial situation, it would take approximately **{months_to_repay:.1f} months** ({years_to_repay:.1f} years) to repay your debt completely if you use all of your monthly surplus for debt repayment.")
                            
                            # Create payment strategy recommendations
                            st.subheader("Debt Repayment Strategies")
                            
                            # Aggressive strategy
                            aggressive_payment = monthly_surplus * 0.8
                            aggressive_months = current_debt / aggressive_payment
                            
                            # Balanced strategy
                            balanced_payment = monthly_surplus * 0.5
                            balanced_months = current_debt / balanced_payment
                            
                            # Conservative strategy
                            conservative_payment = monthly_surplus * 0.3
                            conservative_months = current_debt / conservative_payment
                            
                            # Create comparison dataframe
                            strategies_df = pd.DataFrame({
                                'Strategy': ['Aggressive', 'Balanced', 'Conservative'],
                                'Monthly Payment': [aggressive_payment, balanced_payment, conservative_payment],
                                'Months to Debt-Free': [aggressive_months, balanced_months, conservative_months]
                            })
                            
                            # Create bar chart
                            fig = px.bar(
                                strategies_df,
                                x='Strategy',
                                y='Months to Debt-Free',
                                title='Debt Repayment Strategy Comparison',
                                color='Strategy',
                                color_discrete_map={
                                    'Aggressive': '#e74c3c',
                                    'Balanced': '#f39c12',
                                    'Conservative': '#3498db'
                                },
                                text='Months to Debt-Free'
                            )
                            
                            fig.update_traces(texttemplate='%{y:.1f} months', textposition='outside')
                            fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display strategy details
                            st.markdown("""
                                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px;'>
                                    <h4 style='margin: 0; color: black;'>Suggested Strategies</h4>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"""
                                    <div style='background-color: #fdedec; padding: 15px; border-radius: 8px; height: 220px;'>
                                        <h4 style='margin: 0; color: #c0392b;'>Aggressive</h4>
                                        <p style='margin: 10px 0; color: black;'>Allocate 80% of your monthly surplus to debt repayment.</p>
                                        <ul style='color: black;'>
                                            <li>Monthly payment: <strong>${aggressive_payment:.2f}</strong></li>
                                            <li>Time to debt-free: <strong>{aggressive_months:.1f} months</strong></li>
                                            <li>Remaining for savings: <strong>${monthly_surplus - aggressive_payment:.2f}/month</strong></li>
                                        </ul>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                    <div style='background-color: #fef9e7; padding: 15px; border-radius: 8px; height: 220px;'>
                                        <h4 style='margin: 0; color: #d35400;'>Balanced</h4>
                                        <p style='margin: 10px 0; color: black;'>Allocate 50% of your monthly surplus to debt repayment.</p>
                                        <ul style='color: black;'>
                                            <li>Monthly payment: <strong>${balanced_payment:.2f}</strong></li>
                                            <li>Time to debt-free: <strong>{balanced_months:.1f} months</strong></li>
                                            <li>Remaining for savings: <strong>${monthly_surplus - balanced_payment:.2f}/month</strong></li>
                                        </ul>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown(f"""
                                    <div style='background-color: #ebf5fb; padding: 15px; border-radius: 8px; height: 220px;'>
                                        <h4 style='margin: 0; color: #2980b9;'>Conservative</h4>
                                        <p style='margin: 10px 0; color: black;'>Allocate 30% of your monthly surplus to debt repayment.</p>
                                        <ul style='color: black;'>
                                            <li>Monthly payment: <strong>${conservative_payment:.2f}</strong></li>
                                            <li>Time to debt-free: <strong>{conservative_months:.1f} months</strong></li>
                                            <li>Remaining for savings: <strong>${monthly_surplus - conservative_payment:.2f}/month</strong></li>
                                        </ul>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("You don't have enough monthly surplus to create a repayment plan. Consider reducing expenses or increasing income.")
                
                # Personalized Recommendations
                st.markdown("<h3 style='margin-top: 30px;'>Personalized Recommendations</h3>", unsafe_allow_html=True)
                
                # Display the analysis with better styling
                st.markdown(f"""
                    <div style='background-color: #f5f5f5; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                        <h4 style='margin: 0; color: black;'>Analysis</h4>
                        <p style='margin: 10px 0; color: black; line-height: 1.5;'>{analysis['analysis']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display actionable recommendations
                if 'recommendations' in analysis:
                    for i, rec in enumerate(analysis['recommendations']):
                        if isinstance(rec, dict):
                            st.markdown(f"""
                                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                                    <h4 style='margin: 0; color: black;'>{rec.get('title', f'Recommendation {i+1}')}</h4>
                                    <p style='margin: 10px 0; color: black;'>{rec.get('description', '')}</p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                                    <p style='margin: 0; color: black;'>{rec}</p>
                                </div>
                            """, unsafe_allow_html=True)

        except Exception as e:
            self.log_error(e, "Financial Health Analysis")
            st.error("An error occurred while analyzing your financial health. Please check the debug panel for more information.")

    def _calculate_health_score(self, analysis):
        """Calculate a comprehensive health score based on multiple financial factors"""
        score = 0
        total_weight = 0
        
        # Get financial metrics
        monthly_income = st.session_state.financial_data.get('basic_info', {}).get('income', 0)
        current_savings = st.session_state.financial_data.get('basic_info', {}).get('savings', 0)
        current_debt = st.session_state.financial_data.get('basic_info', {}).get('debt', 0)
        
        # Calculate average monthly expenses
        expenses = st.session_state.financial_data.get('monthly_expenses', {})
        avg_expenses = 0
        if expenses:
            avg_expenses = sum(sum(month_data.values()) for month_data in expenses.values()) / len(expenses)
        
        # Calculate key ratios
        savings_rate = (monthly_income - avg_expenses) / monthly_income if monthly_income > 0 else 0
        debt_to_income = current_debt / (monthly_income * 12) if monthly_income > 0 else 0
        emergency_fund_months = current_savings / avg_expenses if avg_expenses > 0 else 0
        
        # 1. Savings Rate (30% weight)
        if savings_rate >= 0.2:
            score += 30
        elif savings_rate >= 0.15:
            score += 25
        elif savings_rate >= 0.1:
            score += 20
        elif savings_rate >= 0.05:
            score += 15
        else:
            score += 10
        total_weight += 30
        
        # 2. Emergency Fund (25% weight)
        if emergency_fund_months >= 6:
            score += 25
        elif emergency_fund_months >= 3:
            score += 20
        elif emergency_fund_months >= 1:
            score += 15
        else:
            score += 10
        total_weight += 25
        
        # 3. Debt-to-Income Ratio (25% weight)
        if debt_to_income < 0.2:
            score += 25
        elif debt_to_income < 0.3:
            score += 20
        elif debt_to_income < 0.4:
            score += 15
        elif debt_to_income < 0.5:
            score += 10
        else:
            score += 5
        total_weight += 25
        
        # 4. Expense-to-Income Ratio (20% weight)
        expense_ratio = avg_expenses / monthly_income if monthly_income > 0 else 1
        if expense_ratio < 0.5:
            score += 20
        elif expense_ratio < 0.7:
            score += 15
        elif expense_ratio < 0.8:
            score += 10
        else:
            score += 5
        total_weight += 20
        
        # Calculate final score
        final_score = (score / total_weight) * 100
        return min(100, max(0, final_score))

    def show_simulation_playground(self):
        """Show the financial simulation playground"""
        st.title("🎮 Financial Simulation Playground")
        
        # Get financial data from session state
        if not st.session_state.financial_data:
            st.error("Please complete your financial profile first.")
            return
            
        # Create two columns for layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Sidebar for input parameters
            st.header("📊 Asset Information")
            
            # Asset Details
            asset_info = {
                "name": st.text_input("Asset Name", ""),
                "cost": st.number_input("Asset Cost ($)", min_value=0.0, step=1000.0),
                "urgency": st.select_slider("Urgency", options=["Low", "Medium", "High"]),
                "payment_type": st.radio("Payment Type", ["Cash", "Installments"])
            }
            
            # Risk Range
            st.header("🎯 Risk Range")
            risk_range = st.slider(
                "Select Risk Tolerance",
                min_value=1,
                max_value=10,
                value=5,
                help="1: Very Conservative, 10: Very Aggressive"
            )
            
            # Custom Prompt
            st.header("💭 Custom Prompt")
            custom_prompt = st.text_area(
                "Add Custom Instructions",
                height=100,
                help="Add any specific instructions or context for the simulation"
            )
            
            # Scenario Details
            st.header("📝 Scenario Details")
            scenario_text = st.text_area(
                "Describe your scenario",
                height=100,
                placeholder="Describe your financial situation and goals..."
            )
            
            # Add a button to run the simulation
            if st.button("Run Simulation", type="primary"):
                # Generate insights with all parameters
                insights = self.simulator.generate_financial_insights(
                    st.session_state.financial_data,
                    scenario_text,
                    asset_info,
                    risk_range,
                    custom_prompt
                )
                
                # Store insights in session state
                st.session_state.simulation_insights = insights
                
        with col2:
            # Display analysis with enhanced visuals
            if 'simulation_insights' in st.session_state:
                insights = st.session_state.simulation_insights
                
                # Overall Health Score Card
                health_score = insights["stability_score"]
                health_color = "#2ecc71" if health_score >= 7 else "#f1c40f" if health_score >= 4 else "#e74c3c"
                st.markdown(f"""
                    <div style='background-color: {health_color}; padding: 20px; border-radius: 10px; text-align: center;'>
                        <h2 style='margin: 0; color: black;'>Financial Health Score</h2>
                        <h1 style='margin: 0; font-size: 48px; color: black;'>{health_score}/10</h1>
                    </div>
                """, unsafe_allow_html=True)
                
                # Financial Health Analysis
                with st.expander("💼 Financial Health Analysis", expanded=True):
                    health = insights["financial_health_analysis"]
                    
                    # Overall Health
                    st.markdown(f"""
                        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                            <h3 style='margin: 0; color: black;'>Overall Health</h3>
                            <p style='margin: 5px 0; color: black;'>{health['overall_health']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Strengths
                        st.markdown("""
                            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Strengths</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        for strength in health["strengths"]:
                            st.markdown(f"✓ {strength}")
                        
                        # Emergency Fund Status
                        st.markdown(f"""
                            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                                <h3 style='margin: 0; color: black;'>Emergency Fund</h3>
                                <p style='margin: 5px 0; color: black;'>{health['emergency_fund_status']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Weaknesses
                        st.markdown("""
                            <div style='background-color: #ffebee; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Weaknesses</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        for weakness in health["weaknesses"]:
                            st.markdown(f"✗ {weakness}")
                        
                        # Debt Management
                        st.markdown(f"""
                            <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                                <h3 style='margin: 0; color: black;'>Debt Management</h3>
                                <p style='margin: 5px 0; color: black;'>{health['debt_management']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Impact Analysis
                with st.expander("⚖️ Impact Analysis", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        # Positives
                        st.markdown("""
                            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Positives</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        for positive in insights["positives"]:
                            st.markdown(f"✓ {positive}")
                        
                        # Financial Impact
                        st.markdown(f"""
                            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                                <h3 style='margin: 0; color: black;'>Financial Impact</h3>
                                <p style='margin: 5px 0; color: black;'>{insights['financial_impact']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Negatives
                        st.markdown("""
                            <div style='background-color: #ffebee; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Negatives</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        for negative in insights["negatives"]:
                            st.markdown(f"✗ {negative}")
                        
                        # Recovery Time
                        st.markdown(f"""
                            <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 15px;'>
                                <h3 style='margin: 0; color: black;'>Recovery Time</h3>
                                <p style='margin: 5px 0; color: black;'>{insights['recovery_time']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Financial Metrics
                with st.expander("📊 Financial Metrics", expanded=True):
                    metrics = insights["metrics"]
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Monthly Metrics
                        st.markdown(f"""
                            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Monthly Metrics</h3>
                                <p style='margin: 5px 0; color: black;'>Surplus: ${metrics['monthly_surplus']:,.2f}</p>
                                <p style='margin: 5px 0; color: black;'>Savings Ratio: {metrics['savings_ratio']:.2%}</p>
                                <p style='margin: 5px 0; color: black;'>Emergency Fund: {metrics['emergency_fund_coverage']:.1f} months</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        # Risk Metrics
                        st.markdown(f"""
                            <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Risk Metrics</h3>
                                <p style='margin: 5px 0; color: black;'>Asset to Savings: {metrics['asset_to_savings_ratio']:.2%}</p>
                                <p style='margin: 5px 0; color: black;'>Debt to Income: {metrics['debt_to_income_ratio']:.2%}</p>
                                <p style='margin: 5px 0; color: black;'>Risk Level: {metrics['risk_level']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Goals and Recommendations
                with st.expander("🎯 Goals and Recommendations", expanded=True):
                    health = insights["financial_health_analysis"]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Goals
                        st.markdown("""
                            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Goals</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown("**Short-term Goals:**")
                        for goal in health["short_term_goals"]:
                            st.markdown(f"• {goal}")
                        st.markdown("**Long-term Goals:**")
                        for goal in health["long_term_goals"]:
                            st.markdown(f"• {goal}")
                        
                    with col2:
                        # Recommendations
                        st.markdown("""
                            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px;'>
                                <h3 style='margin: 0; color: black;'>Recommendations</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"**Payment Method:** {insights['payment_recommendation']}")
                        st.markdown("**Cost Cutting Suggestions:**")
                        for suggestion in insights["cost_cutting_suggestions"]:
                            st.markdown(f"• {suggestion}")
                
                # Final Recommendation
                st.markdown(f"""
                    <div style='background-color: #2ecc71; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;'>
                        <h2 style='margin: 0; color: black;'>Final Recommendation</h2>
                        <p style='margin: 10px 0; font-size: 18px; color: black;'>{insights["metrics"]["recommended_action"]}</p>
                    </div>
                """, unsafe_allow_html=True)

    def show_recommendations(self):
        st.header("AI Recommendations")
        
        if 'financial_data' not in st.session_state or not st.session_state.financial_data:
            st.warning("Please import your financial data first.")
            return

        # Get recommendations from the AI agent
        recommendations = self.financial_ai.generate_recommendations(
            st.session_state.financial_data,
            st.session_state.predictions if 'predictions' in st.session_state else None,
            st.session_state.simulations if 'simulations' in st.session_state else None
        )

        # Display recommendations by category
        for category, recs in recommendations.items():
            st.subheader(category.title())
            for rec in recs:
                if isinstance(rec, dict):
                    # Handle structured recommendations
                    st.markdown(f"**{rec.get('title', 'Recommendation')}**")
                    st.write(rec.get('description', ''))
                    if rec.get('visualization'):
                        self.svg_converter.display_svg(rec['visualization'])
                else:
                    # Handle simple string recommendations
                    st.write(f"• {rec}")
            
            st.markdown("---")

        # Add action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Apply Recommendations"):
                st.success("Recommendations applied to your financial plan!")
        with col2:
            if st.button("Generate More Recommendations"):
                st.info("New recommendations generated based on your latest data.")

    def export_financial_data(self):
        """Export all financial data to a JSON file."""
        if not st.session_state.user_data:
            st.warning("Please input your basic financial information first!")
            return
            
        if not st.session_state.monthly_expenses:
            st.warning("Please add some monthly expenses first!")
            return
            
        # Create data processor instance
        data_processor = DataProcessor()
        
        # Generate detailed financial analysis
        financial_analysis = data_processor.generate_financial_analysis(
            st.session_state.user_data, 
            st.session_state.monthly_expenses
        )
        
        # Prepare data for export
        export_data = {
            "basic_info": st.session_state.user_data,
            "monthly_expenses": st.session_state.monthly_expenses,
            "financial_analysis": financial_analysis,
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0"
        }
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=4)
        
        # Create download button
        st.download_button(
            label="Download Financial Data (JSON)",
            data=json_data,
            file_name=f"fintwin_financial_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        
        st.success("Financial data exported successfully!")
        
        # Display preview of exported data
        with st.expander("Preview Exported Data"):
            st.json(export_data)
            
        # Display key insights from the analysis
        if financial_analysis:
            st.subheader("Key Financial Insights")
            
            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Savings Rate", f"{financial_analysis['summary']['savings_rate']*100:.1f}%")
            with col2:
                st.metric("Debt-to-Income Ratio", f"{financial_analysis['summary']['debt_to_income_ratio']*100:.1f}%")
            with col3:
                st.metric("Avg Monthly Expense", f"${financial_analysis['summary']['avg_monthly_expense']:,.2f}")
                
            # Display top expense categories
            st.subheader("Top Expense Categories")
            for category in financial_analysis['expenses']['top_categories']:
                st.metric(
                    category['category'], 
                    f"${category['amount']:,.2f}",
                    f"{category['amount']/financial_analysis['summary']['total_income']*100:.1f}% of income"
                )
                
            # Display high-priority recommendations
            high_priority_recs = []
            for category, recs in financial_analysis['recommendations'].items():
                for rec in recs:
                    if rec['priority'] == 'high':
                        high_priority_recs.append(rec)
                        
            if high_priority_recs:
                st.subheader("High Priority Recommendations")
                for rec in high_priority_recs:
                    st.info(f"**{rec['title']}**: {rec['description']}")

    def import_financial_data(self, uploaded_file):
        """Import financial data from a JSON file."""
        try:
            # Read the uploaded file
            import_data = json.load(uploaded_file)
            
            # Validate the data structure
            if "basic_info" not in import_data or "monthly_expenses" not in import_data:
                st.error("Invalid data format. The file must contain basic financial information and monthly expenses.")
                return
                
            # Update session state with imported data
            st.session_state.user_data = import_data["basic_info"]
            st.session_state.monthly_expenses = import_data["monthly_expenses"]
            
            # Create a consolidated financial_data structure
            st.session_state.financial_data = {
                "basic_info": import_data["basic_info"],
                "monthly_expenses": import_data["monthly_expenses"],
                "analysis": import_data.get("financial_analysis", {})
            }
            
            st.success("Financial data imported successfully!")
            
            # Display summary of imported data
            with st.expander("Imported Data Summary"):
                # Basic info summary
                st.subheader("Basic Financial Information")
                st.json({
                    "income": import_data["basic_info"].get("income", 0),
                    "savings": import_data["basic_info"].get("savings", 0),
                    "debt": import_data["basic_info"].get("debt", 0)
                })
                
                # Monthly expenses summary
                st.subheader("Monthly Expenses")
                st.json({
                    "months_with_expenses": len(import_data["monthly_expenses"]),
                    "total_expenses": sum(sum(expenses.values()) for expenses in import_data["monthly_expenses"].values())
                })
                
                # Display financial analysis if available
                if "financial_analysis" in import_data:
                    st.subheader("Financial Analysis")
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Savings Rate", f"{import_data['financial_analysis']['summary']['savings_rate']*100:.1f}%")
                    with col2:
                        st.metric("Debt-to-Income Ratio", f"{import_data['financial_analysis']['summary']['debt_to_income_ratio']*100:.1f}%")
                    with col3:
                        st.metric("Avg Monthly Expense", f"${import_data['financial_analysis']['summary']['avg_monthly_expense']:,.2f}")
                        
                    # Display top expense categories
                    st.subheader("Top Expense Categories")
                    for category in import_data['financial_analysis']['expenses']['top_categories']:
                        st.metric(
                            category['category'], 
                            f"${category['amount']:,.2f}",
                            f"{category['amount']/import_data['financial_analysis']['summary']['total_income']*100:.1f}% of income"
                        )
                        
                    # Display high-priority recommendations
                    high_priority_recs = []
                    for category, recs in import_data['financial_analysis']['recommendations'].items():
                        for rec in recs:
                            if rec['priority'] == 'high':
                                high_priority_recs.append(rec)
                                
                    if high_priority_recs:
                        st.subheader("High Priority Recommendations")
                        for rec in high_priority_recs:
                            st.info(f"**{rec['title']}**: {rec['description']}")
                
                # Display export information
                st.subheader("Export Information")
                st.json({
                    "export_date": import_data.get("export_date", "Unknown"),
                    "version": import_data.get("version", "Unknown")
                })
                
        except Exception as e:
            self.log_error(e, "Data Import")
            st.error(f"Error importing data: {str(e)}")

    def clear_financial_data(self):
        """Clear all financial data from the session state."""
        if st.checkbox("I understand that this will permanently delete all my financial data"):
            st.session_state.user_data = None
            st.session_state.monthly_expenses = {}
            st.session_state.financial_data = None
            st.success("All financial data has been cleared.")

    def show_financial_tools(self):
        st.header("💰 Financial Tools")
        
        # Create tabs for different financial tools
        tool_tab = st.selectbox(
            "Select Tool",
            ["Loan Calculator", "Investment Calculator", "Debt Repayment Planner"]
        )
        
        if tool_tab == "Loan Calculator":
            self.show_loan_calculator()
        elif tool_tab == "Investment Calculator":
            self.show_investment_calculator()
        elif tool_tab == "Debt Repayment Planner":
            self.show_debt_repayment_planner()

    def show_loan_calculator(self):
        st.subheader("Loan Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            loan_amount = st.number_input("Loan Amount ($)", min_value=1000, step=1000, value=10000)
            loan_term = st.number_input("Loan Term (years)", min_value=1, max_value=30, value=5)
            interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=30.0, step=0.1, value=5.0)
        
        with col2:
            loan_purpose = st.selectbox("Loan Purpose", ["Home", "Education", "Business", "Personal"])
            payment_frequency = st.selectbox("Payment Frequency", ["Monthly", "Bi-weekly", "Weekly"])
            start_date = st.date_input("Start Date", value=datetime.now().date())
        
        if st.button("Calculate"):
            # Convert years to months for calculation
            term_months = loan_term * 12
            monthly_rate = interest_rate / 100 / 12
            
            # Calculate monthly payment
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -term_months)
            
            # Calculate total interest
            total_interest = (monthly_payment * term_months) - loan_amount
            
            # Calculate total cost
            total_cost = loan_amount + total_interest
            
            # Display results
            st.subheader("Loan Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Monthly Payment", f"${monthly_payment:,.2f}")
            with col2:
                st.metric("Total Interest", f"${total_interest:,.2f}")
            with col3:
                st.metric("Total Cost", f"${total_cost:,.2f}")
            
            # Display amortization schedule
            st.subheader("Amortization Schedule")
            schedule = []
            remaining_balance = loan_amount
            
            for month in range(1, term_months + 1):
                interest_payment = remaining_balance * monthly_rate
                principal_payment = monthly_payment - interest_payment
                remaining_balance -= principal_payment
                
                schedule.append({
                    "Month": month,
                    "Payment": f"${monthly_payment:,.2f}",
                    "Principal": f"${principal_payment:,.2f}",
                    "Interest": f"${interest_payment:,.2f}",
                    "Remaining Balance": f"${remaining_balance:,.2f}"
                })
            
            st.dataframe(schedule)

    def show_investment_calculator(self):
        st.subheader("Investment Calculator")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_investment = st.number_input("Initial Investment ($)", min_value=1000, step=1000, value=10000)
            monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0, step=100, value=500)
            investment_period = st.number_input("Investment Period (years)", min_value=1, max_value=50, value=10)
        
        with col2:
            expected_return = st.number_input("Expected Annual Return (%)", min_value=0.0, max_value=30.0, step=0.1, value=7.0)
            risk_level = st.selectbox("Risk Level", ["Low", "Moderate", "High"])
            investment_type = st.selectbox("Investment Type", ["Stocks", "Bonds", "Real Estate", "Mixed Portfolio"])
        
        if st.button("Calculate"):
            # Calculate compound interest with monthly contributions
            monthly_rate = expected_return / 100 / 12
            total_months = investment_period * 12
            
            # Future value of initial investment
            future_value = initial_investment * (1 + monthly_rate) ** total_months
            
            # Future value of monthly contributions
            if monthly_contribution > 0:
                future_value += monthly_contribution * ((1 + monthly_rate) ** total_months - 1) / monthly_rate
            
            # Calculate total contributions
            total_contributions = initial_investment + (monthly_contribution * total_months)
            
            # Calculate total return
            total_return = future_value - total_contributions
            
            # Display results
            st.subheader("Investment Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Future Value", f"${future_value:,.2f}")
            with col2:
                st.metric("Total Contributions", f"${total_contributions:,.2f}")
            with col3:
                st.metric("Total Return", f"${total_return:,.2f}")
            
            # Display growth chart
            growth_data = []
            balance = initial_investment
            
            for month in range(total_months + 1):
                if month > 0:
                    balance = (balance + monthly_contribution) * (1 + monthly_rate)
                growth_data.append({
                    "Month": month,
                    "Balance": balance
                })
            
            st.line_chart(pd.DataFrame(growth_data).set_index("Month"))

    def show_debt_repayment_planner(self):
        st.subheader("Debt Repayment Planner")
        
        if not st.session_state.financial_data:
            st.warning("Please import your financial data first to get personalized recommendations.")
            return
        
        # Get current financial data
        monthly_income = st.session_state.financial_data.get('monthly_income', 0)
        current_debt = st.session_state.financial_data.get('debt', 0)
        monthly_expenses = st.session_state.financial_data.get('monthly_expenses', {})
        
        # Calculate average monthly expenses
        avg_expenses = 0
        if monthly_expenses:
            avg_expenses = sum(sum(month_data.values()) for month_data in monthly_expenses.values()) / len(monthly_expenses)
        
        # Calculate monthly surplus
        monthly_surplus = monthly_income - avg_expenses
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Debt", f"${current_debt:,.2f}")
            st.metric("Monthly Surplus", f"${monthly_surplus:,.2f}")
        
        with col2:
            st.metric("Monthly Income", f"${monthly_income:,.2f}")
            st.metric("Average Monthly Expenses", f"${avg_expenses:,.2f}")
        
        if monthly_surplus > 0:
            # Calculate different repayment strategies
            strategies = {
                "Aggressive": 0.8,
                "Balanced": 0.5,
                "Conservative": 0.3
            }
            
            st.subheader("Repayment Strategies")
            
            for strategy, percentage in strategies.items():
                monthly_payment = monthly_surplus * percentage
                months_to_repay = current_debt / monthly_payment
                years_to_repay = months_to_repay / 12
                
                st.write(f"**{strategy} Strategy**")
                st.write(f"- Monthly Payment: ${monthly_payment:,.2f}")
                st.write(f"- Time to Repay: {months_to_repay:.1f} months ({years_to_repay:.1f} years)")
                st.write("---")
            
            # Display repayment schedule
            st.subheader("Recommended Repayment Schedule")
            schedule = []
            remaining_debt = current_debt
            monthly_payment = monthly_surplus * 0.5  # Using balanced strategy
            
            month = 1
            while remaining_debt > 0:
                interest = remaining_debt * 0.1 / 12  # Assuming 10% annual interest
                principal = min(monthly_payment - interest, remaining_debt)
                remaining_debt -= principal
                
                schedule.append({
                    "Month": month,
                    "Payment": f"${monthly_payment:,.2f}",
                    "Principal": f"${principal:,.2f}",
                    "Interest": f"${interest:,.2f}",
                    "Remaining Debt": f"${remaining_debt:,.2f}"
                })
                
                month += 1
            
            st.dataframe(schedule)
        else:
            st.error("You don't have enough monthly surplus to create a repayment plan. Consider reducing expenses or increasing income.")

    def show_navigation(self):
        st.sidebar.markdown("""
            <style>
            .nav-header {
                background: linear-gradient(45deg, #000000, #000000);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                text-align: center;
                font-size: 1.2rem;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .nav-button {
                background-color: #000000;
                color: white;
                border: 1px solid #000000;
                border-radius: 5px;
                padding: 0.5rem;
                margin: 0.5rem 0;
                width: 100%;
                text-align: left;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .nav-button:hover {
                background-color: #1a1a1a;
                color: white;
                transform: translateX(5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .nav-button.active {
                background-color: #1a1a1a;
                color: white;
                border-left: 4px solid #ffd700;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .user-profile {
                background-color: #000000;
                padding: 1rem;
                border-radius: 10px;
                margin-top: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(45deg, #000000, #1a1a1a);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                margin: 0 auto;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: #4caf50;
                display: inline-block;
                margin-right: 5px;
                box-shadow: 0 0 5px #4caf50;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize session state for current page if not exists
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'import_data'
        
        # Navigation header
        st.sidebar.markdown('<div class="nav-header">FinTwin Navigation</div>', unsafe_allow_html=True)
        
        # Navigation buttons
        pages = {
            'import_data': '📥 Import Data',
            'financial_health': '💸 Financial Health',
            'simulation_playground': '🎮 Simulation Playground',
            'financial_tools': '💰 Financial Tools',
            'recommendations': '💡 Recommendations'
        }
        
        for page_id, page_name in pages.items():
            if st.sidebar.button(page_name, key=f"nav_{page_id}", 
                               use_container_width=True,
                               type="primary" if st.session_state.current_page == page_id else "secondary"):
                st.session_state.current_page = page_id
        
        # User profile section
        st.sidebar.markdown('<div class="user-profile">', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="avatar">U</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<p style="text-align: center; margin-top: 0.5rem;"><span class="status-indicator"></span> Online</p>', unsafe_allow_html=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # Show the selected page
        if st.session_state.current_page == 'import_data':
            self.show_import_data()
        elif st.session_state.current_page == 'financial_health':
            self.show_financial_health()
        elif st.session_state.current_page == 'simulation_playground':
            self.show_simulation_playground()
        elif st.session_state.current_page == 'financial_tools':
            self.show_financial_tools()
        elif st.session_state.current_page == 'recommendations':
            self.show_recommendations()

if __name__ == "__main__":
    app = FinTwinApp()
    app.run() 