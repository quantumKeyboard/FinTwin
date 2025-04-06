# FinTwin - AI Financial Advisor

FinTwin is an advanced AI-powered financial advisor application that helps users track expenses, analyze financial health, and get personalized recommendations. Built with cutting-edge AI technology and robust financial analytics, it serves as your personal financial companion.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

## Features

### 🏦 Financial Data Management
- Track income, expenses, savings, and debt
- Categorize and monitor monthly expenses
- Import/export financial data
- Historical data analysis

### 📊 Financial Health Analysis
- AI-powered financial health scoring
- Risk level assessment
- Savings projections
- Trend analysis and visualizations

### 🎮 Simulation Playground
- Investment scenario testing
- Expense reduction impact analysis
- Asset purchase evaluation
- Financial goal planning

### 💡 Personalized Recommendations
- AI-generated financial advice
- Category-specific optimization suggestions
- Risk-aware recommendations
- Goal-oriented guidance

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/quantumKeyboard/805DevKraft.git
   cd 805DevKraft
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Required Package Versions
```plaintext
streamlit==1.32.0
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.6.1
prophet==1.1.5
plotly==5.18.0
python-dotenv==1.0.0
openai==1.7.0
langchain==0.1.4
pydantic==2.6.1
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.2
```

## Configuration

1. **Environment Setup**
   Create a `.env` file in the project root:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **OpenAI API Key**
   - Sign up at [OpenAI](https://openai.com)
   - Generate an API key
   - Add it to your `.env` file

## Usage

1. **Start the Application**
   ```bash
   python -m streamlit run app.py
   ```

2. **Access the Interface**
   - Open your browser
   - Navigate to `http://localhost:8501`

### Basic Workflow

1. **Initial Setup**
   - Enter your basic financial information
   - Set up expense categories
   - Import existing financial data (optional)

2. **Regular Usage**
   - Update monthly expenses
   - Track income and savings
   - Monitor financial health
   - Run financial simulations
   - Review AI recommendations

## Project Structure

```plaintext
805DevKraft/
├── app.py                 # Main Streamlit application
├── financial_ai.py        # AI integration and analysis
├── data_processor.py      # Data processing and visualization
├── svg_converter.py       # SVG handling utilities
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables
└── .gitignore            # Git ignore rules
```

## Technologies

### Core Technologies
- **Python**: Primary programming language
- **Streamlit**: Web application framework
- **OpenAI API**: AI-powered analysis
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations
- **Scikit-learn**: Machine learning models
- **Prophet**: Time series forecasting
- **Plotly**: Interactive visualizations

### Additional Libraries
- **python-dotenv**: Environment management
- **langchain**: AI chain operations
- **pydantic**: Data validation
- **python-jose**: JWT handling
- **passlib & bcrypt**: Security features

## Development

### Setting Up Development Environment

1. **Install Development Tools**
   ```bash
   pip install black pylint pytest
   ```

2. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Add docstrings for functions and classes

### Running Tests
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## Support

For support:
1. Check the documentation
2. Create an issue in the repository
3. Contact the development team

---
