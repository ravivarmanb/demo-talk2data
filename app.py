import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from database import Database, Base

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    st.warning("Please set the GEMINI_API_KEY in your .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize database
db = Database('sqlite:///health_insurance.db')
engine = create_engine('sqlite:///health_insurance.db')
Session = sessionmaker(bind=engine)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Database schema information for the prompt
SCHEMA_INFO = """
The database has the following tables:

1. addresses: Contains address information (address_id, street_address, city, state, zip_code, country)
2. customers: Contains customer information (customer_id, first_name, last_name, date_of_birth, email, phone, ssn, address_id)
3. agents: Contains agent information (agent_id, first_name, last_name, email, phone, hire_date, address_id)
4. policy_types: Contains policy type information (type_id, name, description, base_premium, coverage_limit)
5. policies: Contains policy information (policy_id, policy_number, customer_id, agent_id, type_id, start_date, end_date, premium, status)
6. claims: Contains claim information (claim_id, claim_number, policy_id, customer_id, claim_date, description, amount_claimed, amount_paid, status)
7. prospects: Contains prospect information (prospect_id, first_name, last_name, email, phone, source, status, notes, created_date)

Relationships:
- customers.address_id -> addresses.address_id
- agents.address_id -> addresses.address_id
- policies.customer_id -> customers.customer_id
- policies.agent_id -> agents.agent_id
- policies.type_id -> policy_types.type_id
- claims.policy_id -> policies.policy_id
- claims.customer_id -> customers.customer_id
"""

def generate_sql(natural_language_query):
    """Generate SQL query from natural language using Gemini 2.5 Flash"""
    try:
        # Using Gemini 2.5 Flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""You are a SQL expert. Given the following database schema:
        
        {SCHEMA_INFO}
        
        Write a SQL query to: {natural_language_query}
        
        Return ONLY the SQL query, nothing else. Do not include any explanations or markdown formatting.
        """
        
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Clean up the response to extract just the SQL
        if '```sql' in sql_query:
            sql_query = sql_query.split('```sql')[1].split('```')[0].strip()
        elif '```' in sql_query:
            sql_query = sql_query.split('```')[1].strip()
            if sql_query.startswith('sql\n'):
                sql_query = sql_query[4:].strip()
        
        return sql_query
    except Exception as e:
        st.error(f"Error generating SQL: {str(e)}")
        return None

def execute_query(query):
    """Execute SQL query and return results as a DataFrame"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None

def display_sql_examples():
    """Display example queries"""
    st.sidebar.markdown("### Example Queries")
    examples = [
        "Show me all active policies with their customer names",
        "List all claims with amounts over $1000",
        "Find the top 5 customers by total premium paid",
        "Show the number of policies by type",
        "List all claims with customer and policy details"
    ]
    
    for idx, example in enumerate(examples):
        if st.sidebar.button(example, key=f"example_{idx}"):
            st.session_state.natural_language = example
            st.rerun()

def main():
    st.set_page_config(
        page_title="Health Insurance Analytics",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Health Insurance Analytics")
    st.markdown("Ask questions about your health insurance data in natural language")
    
    # Initialize database if needed
    if not os.path.exists('health_insurance.db'):
        with st.spinner("Initializing database with sample data..."):
            db.init_db()
            db.create_sample_data(50)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Sidebar with database info and examples
    with st.sidebar:
        st.header("Database Info")
        st.markdown("""
        This app connects to a SQLite database with the following tables:
        - Customers
        - Policies
        - Claims
        - Agents
        - Addresses
        - Policy Types
        - Prospects
        """)
        
        if st.button("Reset Database"):
            with st.spinner("Resetting database..."):
                db.drop_tables()
                db.init_db()
                db.create_sample_data(50)
                st.success("Database reset with sample data")
        
        display_sql_examples()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your health insurance data"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            st.markdown("Generating SQL query...")
            sql_query = generate_sql(prompt)
            
            if sql_query:
                st.markdown("**Generated SQL:**")
                st.code(sql_query, language="sql")
                
                st.markdown("**Results:**")
                df = execute_query(sql_query)
                
                if df is not None:
                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                        
                        # Show some basic stats if the result is numeric
                        if len(df.select_dtypes(include=['number']).columns) > 0:
                            st.markdown("**Quick Statistics:**")
                            st.json(df.describe().to_dict())
                    else:
                        st.info("No results found.")
                
                # Add to message history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"SQL Query:\n```sql\n{sql_query}\n```\n\nResults: {len(df) if df is not None else 0} rows returned"
                })
            else:
                st.error("Could not generate a valid SQL query. Please try rephrasing your question.")

if __name__ == "__main__":
    main()
