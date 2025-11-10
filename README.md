# Health Insurance Analytics with Streamlit and Gemini

This is a Streamlit application that allows you to interact with a health insurance database using natural language. The application uses Google's Gemini AI to convert natural language queries into SQL and display the results.

## Features

- Natural language to SQL conversion using Gemini
- Interactive data exploration
- Sample health insurance database with synthetic data
- Example queries to get you started
- Responsive web interface

## Prerequisites

- Python 3.8+
- Google Gemini API key

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Gemini API key:
   ```
   cp .env.example .env
   ```
   Then edit `.env` and replace `your_gemini_api_key_here` with your actual Gemini API key.

## Running the Application

1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to `http://localhost:8501`

## Database Schema

The application uses a SQLite database with the following tables:

- **addresses**: Contains address information
- **customers**: Contains customer information
- **agents**: Contains insurance agent information
- **policy_types**: Different types of insurance policies
- **policies**: Insurance policies linked to customers and agents
- **claims**: Insurance claims made by customers
- **prospects**: Potential customers

## Example Queries

Try these example queries to get started:

- Show me all active policies with their customer names
- List all claims with amounts over $1000
- Find the top 5 customers by total premium paid
- Show the number of policies by type
- List all claims with customer and policy details

## Resetting the Database

You can reset the database with fresh sample data by clicking the "Reset Database" button in the sidebar.

## License

This project is licensed under the MIT License.
