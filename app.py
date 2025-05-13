from dotenv import load_dotenv
import os
import mysql.connector
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq


load_dotenv()
groq_api_key= os.getenv("GROQ_API_KEY")

# 1. Setup LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")  # or "gemma2-9b-it"


# 2. Define Prompt Template
prompt = PromptTemplate(
    input_variables=["question", "table_info"],
    template="""
You are a helpful assistant that converts natural language questions into SQL queries.
Given the table schema and a user's question, generate a syntactically correct SQL query and please don't add sql word in the query and always add ; end of the query.
Only output the raw SQL query without any explanation or formatting.

### Table Schema:
{table_info}

### Question:
{question}

### SQL Query:
"""
)

table_info ="""
TABLE: STUDENT1
-name VARCHAR(25)
-class VARCHAR(25)
-section VARCHAR(25)
-marks (INT)
    """

# 3. Chain
chain = prompt | llm | StrOutputParser()

# 4. MySQL Query Function
def run_sql_query(sql):
    conn = mysql.connector.connect(
        host="localhost",
        user="Your User Name",
        password="Your Password",
        database="Database Name"
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

# 5. Streamlit UI
st.title("ENGLISH TO SQL QUERY:brain:")

question = st.text_input("Ask a question about the STUDENT1 table:")
if st.button("Submit"):
    try:
        sql_query = chain.invoke({"table_info":table_info,"question": question})
        st.code(sql_query, language="sql")
        results = run_sql_query(sql_query)
        st.subheader("Results:")
        for row in results:
            st.write(row)
    except Exception as e:
        st.error(f"Error: {e}")