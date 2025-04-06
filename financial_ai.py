import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from openai import OpenAI
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

class FinancialAI:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        self._initialize_models()
        self._initialize_context()

    def _initialize_context(self):
        """Initialize the context prompt for the AI"""
        self.context_prompt = """You are an advanced Financial Intelligence Assistant designed to help users understand, manage, and optimize their personal finances. You analyze financial data with precision and communicate insights clearly, acting as both a financial analyst and advisor.

CAPABILITIES:
- Process and analyze personal financial data provided in JSON format
- Generate personalized financial profiles and assessments 
- Create accurate forecasts and predictions based on spending patterns
- Provide actionable financial recommendations and precautions
- Simulate financial scenarios and their potential impacts
- Calculate recovery timelines for financial decisions
- Generate SVG code for data visualizations

RESPONSIBILITIES:
1. Financial Profile Analysis
   - Analyze monthly income, expenses, savings, and debt data
   - Identify spending patterns, trends, and potential issues
   - Calculate key financial metrics (savings rate, debt-to-income ratio, etc.)
   - Present findings in an organized, understandable format

2. Prediction and Forecasting
   - Project future financial states based on current patterns
   - Identify potential financial risks or opportunities
   - Forecast savings growth or debt reduction timelines
   - Predict impact of recurring expenses on long-term goals

3. Recommendation Generation
   - Suggest specific actions to improve financial health
   - Identify areas for potential expense reduction
   - Recommend optimal savings or debt payment strategies
   - Propose budget adjustments based on spending patterns

4. Financial Scenario Simulation
   - Assess affordability of proposed purchases or investments
   - Calculate impact on monthly cash flow and savings
   - Determine recovery periods for financial decisions
   - Provide multiple scenario outcomes with varying approaches
   - Suggest expenditure adjustments to maintain financial stability

5. Data Visualization
   - Generate clean, readable SVG code for financial visualizations
   - Create appropriate chart types based on the data
   - Include clear labels, legends, and color coding
   - Design visualizations that highlight key insights
   - Scale visualizations appropriately for web display
   - Format SVG code to be directly usable

INTERACTION GUIDELINES:
- Maintain confidentiality and treat financial data with respect
- Provide explanations behind recommendations and calculations
- Present information in both detailed and summarized formats
- Balance technical accuracy with accessible explanations
- Avoid judgmental language regarding spending decisions
- Focus on actionable insights rather than generic advice
- Base all recommendations on the specific financial data provided
- Consider both short-term needs and long-term financial health
- Always provide visual representations of key data points and forecasts"""

    def _initialize_models(self):
        self.health_model = RandomForestRegressor()
        self.risk_model = RandomForestRegressor()
        self.scaler = StandardScaler()

    def analyze_financial_health(self, user_data):
        """Analyze financial health using OpenAI API"""
        try:
            # Prepare the data for analysis
            analysis_data = {
                "user_data": user_data,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "financial_health"
            }

            # Create the messages for the API call
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": f"Please analyze the following financial data and provide a comprehensive health assessment. Include SVG visualizations for key metrics. Data: {json.dumps(analysis_data)}"}
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Parse the response
            try:
                response_data = json.loads(response.choices[0].message.content)
                return {
                    'health_score': response_data.get('health_score', 0),
                    'risk_level': response_data.get('risk_level', 'Unknown'),
                    'savings_projection': response_data.get('savings_projection', 0),
                    'analysis': response_data.get('analysis', ''),
                    'visualization': response_data.get('visualization', '')
                }
            except json.JSONDecodeError:
                return self._fallback_analysis(user_data)

        except Exception as e:
            print(f"Error in OpenAI analysis: {e}")
            return self._fallback_analysis(user_data)

    def simulate_scenario(self, user_data, scenario_type, parameters):
        """Run simulations using OpenAI API"""
        try:
            # Prepare simulation data
            simulation_data = {
                "user_data": user_data,
                "scenario_type": scenario_type,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }

            # Create the messages for the API call
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": f"Please simulate the following financial scenario and provide detailed analysis with SVG visualizations. Scenario: {json.dumps(simulation_data)}"}
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Parse the response
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return self._fallback_simulation(scenario_type, parameters)

        except Exception as e:
            print(f"Error in OpenAI simulation: {e}")
            return self._fallback_simulation(scenario_type, parameters)

    def generate_recommendations(self, user_data, predictions=None, simulations=None):
        """Generate recommendations using OpenAI API"""
        try:
            # Prepare recommendation data
            recommendation_data = {
                "user_data": user_data,
                "predictions": predictions,
                "simulations": simulations,
                "timestamp": datetime.now().isoformat()
            }

            # Create the messages for the API call
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": f"Please generate personalized financial recommendations based on the following data. Include SVG visualizations for key recommendations. Data: {json.dumps(recommendation_data)}"}
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Parse the response
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return self._fallback_recommendations()

        except Exception as e:
            print(f"Error in OpenAI recommendations: {e}")
            return self._fallback_recommendations()

    def _fallback_analysis(self, user_data):
        """Fallback analysis when OpenAI API fails"""
        features = self._prepare_features(user_data)
        health_score = self._predict_health_score(features)
        risk_level = self._predict_risk_level(features)
        savings_projection = self._project_savings(user_data)
        
        return {
            'health_score': health_score,
            'risk_level': risk_level,
            'savings_projection': savings_projection,
            'analysis': self._generate_ai_analysis(user_data, health_score, risk_level, savings_projection),
            'visualization': None
        }

    def _fallback_simulation(self, scenario_type, parameters):
        """Fallback simulation when OpenAI API fails"""
        if scenario_type == "expense_reduction":
            return self.simulate_expense_reduction_fallback(parameters)
        elif scenario_type == "income_increase":
            return self.simulate_income_increase_fallback(parameters)
        elif scenario_type == "loan":
            return self.simulate_loan_fallback(parameters)
        elif scenario_type == "investment":
            return self.simulate_investment_fallback(parameters)
        return None

    def _fallback_recommendations(self):
        """Fallback recommendations when OpenAI API fails"""
        return {
            'savings': ['Increase your emergency fund', 'Consider a high-yield savings account'],
            'investments': ['Diversify your portfolio', 'Consider index funds'],
            'debt': ['Pay off high-interest debt first', 'Consider debt consolidation']
        }

    def _prepare_features(self, user_data):
        features = []
        if user_data:
            features.extend([
                user_data.get('income', 0),
                user_data.get('savings', 0),
                user_data.get('debt', 0)
            ])
        return np.array(features).reshape(1, -1)

    def _predict_health_score(self, features):
        # Placeholder for actual prediction logic
        return 75.0

    def _predict_risk_level(self, features):
        # Placeholder for actual prediction logic
        return "Moderate"

    def _project_savings(self, user_data):
        # Placeholder for actual projection logic
        return 10000.0

    def _generate_ai_analysis(self, user_data, health_score, risk_level, savings_projection):
        # Placeholder for actual AI analysis
        return "Your financial health is in good shape. Consider increasing your savings rate."

    def simulate_expense_reduction_fallback(self, parameters):
        """Fallback method for expense reduction simulation"""
        expense_type = parameters.get('expense_type', 'Unknown')
        reduction_percentage = parameters.get('reduction_percentage', 0)
        
        return {
            'scenario': 'expense_reduction',
            'type': expense_type,
            'reduction': reduction_percentage,
            'impact': 'positive',
            'analysis': f'Reducing {expense_type} by {reduction_percentage}% would improve your financial health.',
            'metrics': {
                'Monthly Savings': f'${1000 * (reduction_percentage/100):.2f}',
                'Annual Impact': f'${12000 * (reduction_percentage/100):.2f}',
                'Risk Reduction': 'Moderate'
            }
        }

    def simulate_income_increase_fallback(self, parameters):
        """Fallback method for income increase simulation"""
        increase_percentage = parameters.get('increase_percentage', 0)
        
        return {
            'scenario': 'income_increase',
            'increase': increase_percentage,
            'impact': 'positive',
            'analysis': f'Increasing income by {increase_percentage}% would significantly improve your financial position.',
            'metrics': {
                'Monthly Increase': f'${500 * (increase_percentage/100):.2f}',
                'Annual Impact': f'${6000 * (increase_percentage/100):.2f}',
                'Savings Potential': 'High'
            }
        }

    def simulate_loan_fallback(self, parameters):
        """Fallback method for loan simulation"""
        amount = parameters.get('amount', 0)
        term = parameters.get('term', 12)
        interest_rate = parameters.get('interest_rate', 0)
        purpose = parameters.get('purpose', 'Unknown')
        
        monthly_payment = (amount * (interest_rate/100/12)) / (1 - (1 + (interest_rate/100/12))**(-term))
        
        return {
            'scenario': 'loan',
            'amount': amount,
            'term': term,
            'interest_rate': interest_rate,
            'purpose': purpose,
            'impact': 'neutral',
            'analysis': f'A {purpose} loan of ${amount} over {term} months at {interest_rate}% interest.',
            'metrics': {
                'Monthly Payment': f'${monthly_payment:.2f}',
                'Total Interest': f'${(monthly_payment * term - amount):.2f}',
                'Debt-to-Income Impact': 'Moderate'
            }
        }

    def simulate_investment_fallback(self, parameters):
        """Fallback method for investment simulation"""
        amount = parameters.get('amount', 0)
        duration = parameters.get('duration', 1)
        risk_level = parameters.get('risk_level', 'Moderate')
        strategy = parameters.get('strategy', 'Balanced')
        
        # Simple compound interest calculation
        annual_return = 0.07 if risk_level == 'Low' else 0.10 if risk_level == 'Moderate' else 0.15
        future_value = amount * (1 + annual_return) ** duration
        
        return {
            'scenario': 'investment',
            'amount': amount,
            'risk_level': risk_level,
            'duration': duration,
            'strategy': strategy,
            'impact': 'positive',
            'analysis': f'Investing ${amount} in a {risk_level} {strategy} strategy over {duration} years.',
            'metrics': {
                'Future Value': f'${future_value:.2f}',
                'Total Return': f'${(future_value - amount):.2f}',
                'Annual Return': f'{annual_return*100:.1f}%'
            }
        } 