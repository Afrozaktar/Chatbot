import os
import streamlit as st
from crewai import Agent, Task, Crew
#Importing crewAI tools
from crewai_tools import (
    CSVSearchTool,
    PDFSearchTool,
    WebsiteSearchTool
)

# Set up API keys
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

csv_tool = CSVSearchTool(csv='merged.csv')
pdf_tool = PDFSearchTool(pdf='ADVISE2.pdf')
web_tool = WebsiteSearchTool(url="https://www.citytech.cuny.edu/catalog/program.aspx?id=47")

def initialize_crew(query):
    recommender = Agent(
        role='Recommends courses',
        goal='Provide accurate and exact recommendations for courses based on students interests and qualifications',
        backstory="You are a experienced student advisor. Your task is to suggest the right courses based on the query and contexts provided. "
                    ,
        tools=[pdf_tool, web_tool],
        max_iterations=50,  # Increase the iteration limit as needed
        max_execution_time=300,
        allow_delegation=False,
        verbose=True,

    )

    validator = Agent(
        role='Validates answer given by recommender',
        goal='review the answer and validate if the answer is correct or not. Use the CSV file for validating, Pre-requisite: Classes you must take prior to the specific class.Co-requisite: Classes you can take along with the desired class if you have not taken them before',
        backstory='A skilled reviewer who checks the answer makes completely sure that the student is getting correct answer by looking at columns like semester, prequisites, corequisites etc',
        tools=[csv_tool],
        verbose=True

    ) 

    # Define tasks
    recommend = Task(
        description="Read the pdf file and find the courses that match the student query: {query}"
                    "Consider the prerequisites and corequisites for each course when making recommendations."
                    "Pre-requisite: Classes you must take prior to the specific class."
                    "Co-requisite: Classes you can take along with the desired class if you have not taken them before"
                    "For example suppose someone took  EMT1111, EMT1150, ENG1101 so far"
                    "As he has not completed all classes which are needed for starting second semester classes"
                    "he can not take any second semester class so first he has to take EMT1120, EMT1130  and some general education classes like ENG, MAT, PHY for which no prerequisites needed or student alreday taken prerequsite classes."
                    "Have a user friendly but straight forward conversation and do not use sentences which not needed" ,
        expected_output='A list or description of courses that match the student query, including the course name, prerequisites, and corequisites. Be accurate and only give answer, do not give extra things',
        agent=recommender
    )

    validate = Task(
        description='Write the exact correct answer for the student and validate the answer given by recommender',
        expected_output='Complete correct answer.',
        agent=validator
    )


    task_answer_crew = Crew(
                agents=[recommender, validator],
                tasks=[recommend]
            )


    inputs = {
            "query": query
        }

    result = task_answer_crew.kickoff(inputs)

    return result


    
# def get_answer(query):
#     final_answer = initialize_crew(query)
#     return final_answer