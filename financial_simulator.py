import streamlit as st
import os
import json
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Load environment variables
load_dotenv()

class FinancialSimulator:
    def __init__(self):
        """Initialize the financial simulator with AI capabilities"""
        # Configure Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Error initializing Gemini: {str(e)}")
            self.model = None

    def generate_financial_insights(self, financial_data: Dict[str, Any], scenario_text: str, asset_info: Dict[str, Any], risk_range: int = 5, custom_prompt: str = "") -> Dict[str, Any]:
        """Generate comprehensive financial insights using Gemini"""
        if not self.model:
            return self._generate_fallback_analysis(financial_data, asset_info, risk_range, custom_prompt)
            
        # Extract and format financial data
        basic_info = financial_data.get("basic_info", {})
        monthly_expenses_data = financial_data.get("monthly_expenses", {})
        
        # Calculate average monthly expenses
        avg_monthly_expenses = 0
        if monthly_expenses_data:
            avg_monthly_expenses = sum(sum(month_data.values()) for month_data in monthly_expenses_data.values()) / len(monthly_expenses_data)
        
        # Format data for AI analysis
        formatted_data = {
            "monthly_income": basic_info.get("income", 0),
            "total_savings": basic_info.get("savings", 0),
            "total_debt": basic_info.get("debt", 0),
            "average_monthly_expenses": avg_monthly_expenses,
            "expense_history": monthly_expenses_data,
            "risk_tolerance": risk_range,
            "custom_instructions": custom_prompt
        }
        
        prompt = f"""
        You are a financial advisor. Analyze this user's financial health and provide a detailed response in JSON format.

        TASK:
        1. Analyze the user's current financial health
        2. Provide detailed insights about their financial situation
        3. Calculate key financial metrics
        4. Provide personalized recommendations
        5. Consider the user's risk tolerance level: {risk_range}/10
        6. Incorporate any custom instructions provided

        FINANCIAL DATA:
        {json.dumps(formatted_data, indent=2)}

        SCENARIO:
        {scenario_text}

        ASSET DETAILS:
        {json.dumps(asset_info, indent=2)}

        CUSTOM INSTRUCTIONS:
        {custom_prompt}

        RESPONSE FORMAT:
        {{
            "financial_health_analysis": {{
                "overall_health": "Overall financial health assessment",
                "strengths": ["List of financial strengths"],
                "weaknesses": ["List of financial weaknesses"],
                "emergency_fund_status": "Assessment of emergency fund adequacy",
                "debt_management": "Analysis of debt situation",
                "savings_rate": "Analysis of savings habits",
                "expense_analysis": "Detailed analysis of spending patterns",
                "risk_tolerance": "Assessment of financial risk tolerance",
                "improvement_areas": ["Areas that need improvement"],
                "short_term_goals": ["Immediate financial goals"],
                "long_term_goals": ["Long-term financial objectives"]
            }},
            "positives": ["List of benefits"],
            "negatives": ["List of drawbacks"],
            "financial_impact": "Detailed impact assessment",
            "payment_recommendation": "Recommended payment method",
            "recovery_time": "Time to recover savings",
            "stability_score": "Score from 1-10",
            "cost_cutting_suggestions": ["List of suggestions"],
            "metrics": {{
                "monthly_surplus": "Calculated value",
                "savings_ratio": "Calculated ratio",
                "asset_to_savings_ratio": "Calculated ratio",
                "debt_to_income_ratio": "Calculated ratio",
                "emergency_fund_coverage": "Number of months covered",
                "risk_level": "Low/Medium/High",
                "recommended_action": "Detailed recommendation"
            }}
        }}

        INSTRUCTIONS:
        1. Provide detailed, personalized financial health analysis
        2. Include specific recommendations based on the user's situation
        3. Ensure all calculations are accurate
        4. Make recommendations clear and actionable
        5. Format all monetary values with proper currency symbols
        6. Consider both short-term and long-term financial implications
        7. Provide specific, actionable steps for improvement
        8. Adjust recommendations based on the user's risk tolerance
        9. Incorporate any custom instructions provided

        Respond with only the JSON object, no additional text or explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return json.loads(response.text)
            else:
                raise Exception("Empty response from Gemini")
        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            return self._generate_fallback_analysis(financial_data, asset_info, risk_range, custom_prompt)
    
    def _generate_fallback_analysis(self, financial_data: Dict[str, Any], asset_info: Dict[str, Any], risk_range: int = 5, custom_prompt: str = "") -> Dict[str, Any]:
        """Generate basic analysis when AI is unavailable"""
        # Extract values from the nested structure
        basic_info = financial_data.get("basic_info", {})
        monthly_expenses_data = financial_data.get("monthly_expenses", {})
        
        # Calculate average monthly expenses
        avg_monthly_expenses = 0
        if monthly_expenses_data:
            avg_monthly_expenses = sum(sum(month_data.values()) for month_data in monthly_expenses_data.values()) / len(monthly_expenses_data)
        
        monthly_income = basic_info.get("income", 0)
        total_savings = basic_info.get("savings", 0)
        total_debt = basic_info.get("debt", 0)
        
        # Calculate metrics
        monthly_surplus = monthly_income - avg_monthly_expenses
        savings_ratio = total_savings / avg_monthly_expenses if avg_monthly_expenses > 0 else 0
        asset_to_savings_ratio = asset_info["cost"] / total_savings if total_savings > 0 else float('inf')
        debt_to_income_ratio = total_debt / monthly_income if monthly_income > 0 else float('inf')
        emergency_fund_coverage = total_savings / avg_monthly_expenses if avg_monthly_expenses > 0 else 0
        
        # Adjust risk level based on risk_range
        risk_level = "High" if risk_range >= 8 else "Medium" if risk_range >= 5 else "Low"
        
        # Adjust recommendations based on risk tolerance
        if risk_range >= 8:
            payment_recommendation = "Cash" if asset_to_savings_ratio < 0.7 else "Installments"
            recommended_action = "Consider saving more before purchase" if asset_to_savings_ratio > 0.7 else "Proceed with purchase if needed"
        elif risk_range >= 5:
            payment_recommendation = "Cash" if asset_to_savings_ratio < 0.5 else "Installments"
            recommended_action = "Consider saving more before purchase" if asset_to_savings_ratio > 0.5 else "Proceed with purchase if needed"
        else:
            payment_recommendation = "Cash" if asset_to_savings_ratio < 0.3 else "Installments"
            recommended_action = "Consider saving more before purchase" if asset_to_savings_ratio > 0.3 else "Proceed with purchase if needed"
        
        # Incorporate custom prompt into analysis if provided
        custom_analysis = ""
        if custom_prompt:
            custom_analysis = f"Custom considerations: {custom_prompt}"
        
        return {
            "financial_health_analysis": {
                "overall_health": "Basic financial health assessment",
                "strengths": ["Regular income stream", "Existing savings"],
                "weaknesses": ["Potential high debt-to-income ratio", "Limited emergency fund"],
                "emergency_fund_status": f"{emergency_fund_coverage:.1f} months of expenses covered",
                "debt_management": f"Debt-to-income ratio: {debt_to_income_ratio:.2f}",
                "savings_rate": f"Current savings rate: {(monthly_surplus/monthly_income*100):.1f}%" if monthly_income > 0 else "Unable to calculate",
                "expense_analysis": "Basic expense analysis based on monthly data",
                "risk_tolerance": f"{risk_level} based on user preference ({risk_range}/10)",
                "improvement_areas": ["Increase emergency fund", "Reduce debt", "Improve savings rate"],
                "short_term_goals": ["Build emergency fund", "Reduce monthly expenses"],
                "long_term_goals": ["Achieve financial stability", "Build wealth"]
            },
            "positives": ["Asset could be an investment", "May improve quality of life"],
            "negatives": ["Reduces financial buffer", "May impact emergency fund"],
            "financial_impact": f"Will use {asset_to_savings_ratio:.1%} of savings" if total_savings > 0 else "No savings available",
            "payment_recommendation": payment_recommendation,
            "recovery_time": f"{asset_info['cost'] / monthly_surplus:.1f} months" if monthly_surplus > 0 else "Unable to calculate",
            "stability_score": max(1, min(10, int(10 - (asset_to_savings_ratio * 5)))) if total_savings > 0 else 1,
            "cost_cutting_suggestions": [
                "Review subscription services",
                "Optimize daily expenses",
                "Consider delayed purchase"
            ],
            "metrics": {
                "monthly_surplus": monthly_surplus,
                "savings_ratio": savings_ratio,
                "asset_to_savings_ratio": asset_to_savings_ratio,
                "debt_to_income_ratio": debt_to_income_ratio,
                "emergency_fund_coverage": emergency_fund_coverage,
                "risk_level": risk_level,
                "recommended_action": recommended_action
            },
            "custom_analysis": custom_analysis
        } 