# FinTwin - AI Financial Advisor

FinTwin is an AI-powered financial advisor application that helps users track expenses, analyze financial health, and get personalized recommendations.

## Features

- **Financial Data Management**: Track income, expenses, savings, and debt
- **Financial Health Analysis**: Get AI-powered insights into your financial situation
- **Simulation Playground**: Experiment with different financial scenarios
- **Personalized Recommendations**: Receive tailored financial advice

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/quantumKeyboard/805DevKraft.git
   cd 805DevKraft
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the application:
```
python -m streamlit run app.py
```

Access the application in your browser at http://localhost:8501

## Project Structure

- `app.py`: Main application file
- `financial_ai.py`: AI models and analysis
- `data_processor.py`: Data processing utilities
- `pages/`: Additional application pages

## Technologies Used

- Python
- Streamlit
- OpenAI API
- Pandas
- NumPy
- Scikit-learn
- Prophet
- Plotly

## License

MIT 