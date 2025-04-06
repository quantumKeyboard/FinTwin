import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self):
        self.colors = {
            'income': '#2ecc71',
            'expenses': '#e74c3c',
            'savings': '#3498db',
            'debt': '#f1c40f',
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#e74c3c',
            'neutral': '#95a5a6'
        }
        self.category_colors = px.colors.qualitative.Set3

    def create_projection_chart(self, predictions):
        """Create a chart showing financial projections."""
        # Prepare data
        df = pd.DataFrame(predictions['projections'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Create figure
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['savings'],
            name='Savings',
            line=dict(color=self.colors['savings'], width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['income'],
            name='Income',
            line=dict(color=self.colors['income'], width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['expenses'],
            name='Expenses',
            line=dict(color=self.colors['expenses'], width=2)
        ))
        
        # Update layout
        fig.update_layout(
            title='Financial Projections',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_simulation_chart(self, simulation):
        """Create a chart comparing simulation results."""
        # Create sample data for visualization
        dates = pd.date_range(start=datetime.now(), periods=12, freq='M')
        base_data = pd.DataFrame({
            'date': dates,
            'value': np.linspace(0, simulation['net_worth_impact'], 12),
            'type': 'Simulation'
        })
        
        # Create figure
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(
            x=base_data['date'],
            y=base_data['value'],
            name='Net Worth Impact',
            line=dict(color=self.colors['savings'], width=2)
        ))
        
        # Add cash flow trace
        cash_flow = pd.DataFrame({
            'date': dates,
            'value': np.full(12, simulation['monthly_cash_flow']),
            'type': 'Cash Flow'
        })
        
        fig.add_trace(go.Scatter(
            x=cash_flow['date'],
            y=cash_flow['value'],
            name='Monthly Cash Flow',
            line=dict(color=self.colors['income'], width=2, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Simulation Results',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_expense_breakdown(self, expenses):
        """Create an enhanced pie chart showing expense breakdown."""
        # Prepare data
        df = pd.DataFrame({
            'category': list(expenses.keys()),
            'amount': list(expenses.values())
        })
        
        # Sort by amount for better visualization
        df = df.sort_values('amount', ascending=False)
        
        # Create figure
        fig = px.pie(
            df,
            values='amount',
            names='category',
            title='Expense Distribution',
            color_discrete_sequence=self.category_colors,
            hole=0.4  # Create a donut chart
        )
        
        # Update layout
        fig.update_layout(
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            annotations=[
                dict(
                    text=f"${sum(expenses.values()):,.2f}",
                    x=0.5,
                    y=0.5,
                    font_size=20,
                    showarrow=False
                )
            ]
        )
        
        return fig

    def create_expense_comparison(self, expenses):
        """Create a bar chart comparing expenses."""
        # Prepare data
        df = pd.DataFrame({
            'category': list(expenses.keys()),
            'amount': list(expenses.values())
        })
        
        # Sort by amount
        df = df.sort_values('amount', ascending=True)
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['amount'],
            y=df['category'],
            orientation='h',
            marker_color=self.colors['primary'],
            text=df['amount'].apply(lambda x: f'${x:,.2f}'),
            textposition='auto',
        ))
        
        # Update layout
        fig.update_layout(
            title='Expense Comparison',
            xaxis_title='Amount ($)',
            yaxis_title='Category',
            template='plotly_white',
            showlegend=False,
            height=400
        )
        
        return fig

    def create_expense_timeline(self, df):
        """Create a time series visualization of expenses using stacked columns."""
        # Convert Month to datetime for proper sorting
        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')
        
        # Create figure
        fig = go.Figure()
        
        # Add stacked bar for each category
        for category in df['Category'].unique():
            category_data = df[df['Category'] == category].groupby('Date')['Amount'].sum().reset_index()
            fig.add_trace(go.Bar(
                x=category_data['Date'],
                y=category_data['Amount'],
                name=category,
                marker_color=self.category_colors[list(df['Category'].unique()).index(category) % len(self.category_colors)]
            ))
        
        # Update layout
        fig.update_layout(
            title='Expense History (Stacked Columns)',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            template='plotly_white',
            hovermode='x unified',
            showlegend=True,
            barmode='stack',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_category_trends(self, df):
        """Create a visualization showing category-wise trends using comparison charts."""
        # Convert Month to datetime for proper sorting
        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')
        
        # Create figure
        fig = go.Figure()
        
        # Add bar for each category
        for category in df['Category'].unique():
            category_data = df[df['Category'] == category].groupby('Date')['Amount'].sum().reset_index()
            fig.add_trace(go.Bar(
                x=category_data['Date'],
                y=category_data['Amount'],
                name=category,
                marker_color=self.category_colors[list(df['Category'].unique()).index(category) % len(self.category_colors)]
            ))
        
        # Update layout
        fig.update_layout(
            title='Category-wise Expense Trends (Comparison)',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            template='plotly_white',
            hovermode='x unified',
            showlegend=True,
            barmode='group',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_monthly_comparison(self, df):
        """Create a visualization comparing expenses across months."""
        # Prepare data
        monthly_data = df.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
        monthly_data['Date'] = pd.to_datetime(monthly_data['Year'] + '-' + monthly_data['Month'] + '-01')
        
        # Create figure
        fig = go.Figure()
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=monthly_data['Date'],
            y=monthly_data['Amount'],
            marker_color=self.colors['primary'],
            text=monthly_data['Amount'].apply(lambda x: f'${x:,.2f}'),
            textposition='auto',
        ))
        
        # Add line for trend
        fig.add_trace(go.Scatter(
            x=monthly_data['Date'],
            y=monthly_data['Amount'].rolling(window=3, min_periods=1).mean(),
            name='3-Month Average',
            line=dict(color=self.colors['accent'], width=2, dash='dash'),
            mode='lines'
        ))
        
        # Update layout
        fig.update_layout(
            title='Monthly Expense Comparison',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_risk_analysis_chart(self, risk_level, risk_change):
        """Create a gauge chart for risk analysis."""
        # Define risk levels and colors
        risk_levels = ["Low", "Medium", "High"]
        risk_colors = ["#2ecc71", "#f1c40f", "#e74c3c"]
        
        # Create figure
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_levels.index(risk_level),
            title={'text': "Risk Level"},
            gauge={
                'axis': {'range': [0, 2], 'ticktext': risk_levels},
                'bar': {'color': risk_colors[risk_levels.index(risk_level)]},
                'steps': [
                    {'range': [0, 0.5], 'color': risk_colors[0]},
                    {'range': [0.5, 1.5], 'color': risk_colors[1]},
                    {'range': [1.5, 2], 'color': risk_colors[2]}
                ]
            }
        ))
        
        # Update layout
        fig.update_layout(
            template='plotly_white',
            height=300
        )
        
        return fig

    def create_health_score_chart(self, health_score):
        """Create a gauge chart for health score."""
        # Create figure
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={'text': "Financial Health Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': self._get_health_score_color(health_score)},
                'steps': [
                    {'range': [0, 33], 'color': "#e74c3c"},
                    {'range': [33, 66], 'color': "#f1c40f"},
                    {'range': [66, 100], 'color': "#2ecc71"}
                ]
            }
        ))
        
        # Update layout
        fig.update_layout(
            template='plotly_white',
            height=300
        )
        
        return fig

    def _get_health_score_color(self, score):
        """Get color based on health score."""
        if score < 33:
            return "#e74c3c"
        elif score < 66:
            return "#f1c40f"
        else:
            return "#2ecc71"

    def create_comparison_chart(self, original_data, modified_data):
        """Create a bar chart comparing original and modified scenarios."""
        # Prepare data
        categories = ['Income', 'Expenses', 'Savings', 'Debt']
        original_values = [
            original_data['income'],
            sum(original_data['expenses'].values()),
            original_data['savings'],
            original_data['debt']
        ]
        modified_values = [
            modified_data['income'],
            sum(modified_data['expenses'].values()),
            modified_data['savings'],
            modified_data['debt']
        ]
        
        # Create figure
        fig = go.Figure()
        
        # Add original data
        fig.add_trace(go.Bar(
            name='Original',
            x=categories,
            y=original_values,
            marker_color='#3498db'
        ))
        
        # Add modified data
        fig.add_trace(go.Bar(
            name='Modified',
            x=categories,
            y=modified_values,
            marker_color='#2ecc71'
        ))
        
        # Update layout
        fig.update_layout(
            title='Scenario Comparison',
            xaxis_title='Category',
            yaxis_title='Amount ($)',
            barmode='group',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def generate_financial_analysis(self, user_data, monthly_expenses):
        """Generate detailed financial analysis for export."""
        if not user_data or not monthly_expenses:
            return {}
            
        # Calculate basic metrics
        total_income = user_data.get("income", 0)
        total_savings = user_data.get("savings", 0)
        total_debt = user_data.get("debt", 0)
        
        # Calculate expense metrics
        total_expenses_by_month = {}
        category_totals = {}
        all_categories = set()
        
        for month_key, expenses in monthly_expenses.items():
            month_total = sum(expenses.values())
            total_expenses_by_month[month_key] = month_total
            
            for category, amount in expenses.items():
                all_categories.add(category)
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
                
        # Calculate averages and trends
        avg_monthly_expense = sum(total_expenses_by_month.values()) / len(total_expenses_by_month) if total_expenses_by_month else 0
        
        # Calculate savings rate
        savings_rate = (total_income - avg_monthly_expense) / total_income if total_income > 0 else 0
        
        # Calculate debt-to-income ratio
        debt_to_income = total_debt / total_income if total_income > 0 else 0
        
        # Identify top expense categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        top_categories = [{"category": cat, "amount": amt} for cat, amt in sorted_categories[:5]]
        
        # Calculate monthly trends
        monthly_trends = []
        sorted_months = sorted(total_expenses_by_month.items())
        
        for i in range(1, len(sorted_months)):
            prev_month, prev_amount = sorted_months[i-1]
            curr_month, curr_amount = sorted_months[i]
            change = curr_amount - prev_amount
            change_percent = (change / prev_amount * 100) if prev_amount > 0 else 0
            
            monthly_trends.append({
                "from_month": prev_month,
                "to_month": curr_month,
                "change": change,
                "change_percent": change_percent
            })
            
        # Generate analysis
        analysis = {
            "summary": {
                "total_income": total_income,
                "total_savings": total_savings,
                "total_debt": total_debt,
                "avg_monthly_expense": avg_monthly_expense,
                "savings_rate": savings_rate,
                "debt_to_income_ratio": debt_to_income
            },
            "expenses": {
                "total_by_month": total_expenses_by_month,
                "category_totals": category_totals,
                "top_categories": top_categories
            },
            "trends": {
                "monthly_trends": monthly_trends
            },
            "recommendations": self._generate_recommendations(
                total_income, total_savings, total_debt, 
                avg_monthly_expense, savings_rate, debt_to_income,
                category_totals
            )
        }
        
        return analysis
        
    def _generate_recommendations(self, income, savings, debt, avg_expense, savings_rate, debt_to_income, category_totals):
        """Generate personalized recommendations based on financial data."""
        recommendations = {
            "savings": [],
            "debt": [],
            "expenses": [],
            "income": []
        }
        
        # Savings recommendations
        if savings_rate < 0.2:
            recommendations["savings"].append({
                "title": "Increase Savings Rate",
                "description": "Your savings rate is below the recommended 20%. Consider reducing expenses or increasing income.",
                "priority": "high"
            })
            
        if savings < income * 3:
            recommendations["savings"].append({
                "title": "Build Emergency Fund",
                "description": "Aim to save at least 3 months of income as an emergency fund.",
                "priority": "medium"
            })
            
        # Debt recommendations
        if debt_to_income > 0.4:
            recommendations["debt"].append({
                "title": "Reduce Debt",
                "description": "Your debt-to-income ratio is high. Focus on paying down high-interest debt first.",
                "priority": "high"
            })
            
        # Expense recommendations
        if avg_expense > income * 0.8:
            recommendations["expenses"].append({
                "title": "Reduce Expenses",
                "description": "Your expenses are consuming more than 80% of your income. Look for areas to cut back.",
                "priority": "high"
            })
            
        # Identify highest expense categories
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        if sorted_categories:
            top_category = sorted_categories[0][0]
            recommendations["expenses"].append({
                "title": f"Review {top_category} Expenses",
                "description": f"Your highest expense category is {top_category}. Consider if there are ways to reduce this expense.",
                "priority": "medium"
            })
            
        # Income recommendations
        if income < avg_expense * 1.5:
            recommendations["income"].append({
                "title": "Increase Income",
                "description": "Consider ways to increase your income to improve your financial situation.",
                "priority": "medium"
            })
            
        return recommendations 