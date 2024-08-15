import os
from crewai import Agent, Task, Crew
# Importing crewAI tools
from crewai_tools import (
    CSVSearchTool,
    PDFSearchTool
)

# Set up API keys
os.environ["OPENAI_API_KEY"] = "sk-proj-vN2jUMudg7EvF71PeVz6T3BlbkFJo1FMNYTzxWzKJcsIEdka"


csv_tool = CSVSearchTool(csv='courses_data.csv')
pdf_tool = PDFSearchTool(pdf='ADVISE.pdf')


query_identifier_agent = Agent(
    role='Query Identifier',
    goal='Identify the type of query: "casual" or "task".',
    backstory='Simple agent to classify the query type.',
    verbose=True)
identify_query_task = Task(
    description='Identify the type of {query} and return "casual" or "task".',
    expected_output='Either "casual" or "task".',
    agent=query_identifier_agent)


general_conversation_agent = Agent(
    role='General Conversation Handler',
    goal='Engage in casual conversation about course recommendations.',
    backstory='Friendly assistant specializing in course-related conversations.',
    verbose=True)
general_conversation_task = Task(
    description="Respond to the user's casual conversation query: {query}.",
    expected_output="A polite and friendly response to a casual query.",
    agent=general_conversation_agent,
)

        
recommender = Agent(
    role='Recommends courses',
    goal='Provide accurate and exact recommendations for courses based on students interests and qualifications',
    backstory="You are a student advisor. Your task is to suggest the right courses based on the query and context document provided. "
                "Please consider the prerequisites and corequisites for each course when making recommendations."
                "Pre-requisite: Classes you must take prior to the specific class."
                 "Co-requisite: Classes you can take along with the desired class if you have not taken them before"
              "For example suppose someone took  EMT1111, EMT1150, ENG1101 so far"
              "As he has not completed all classes which are needed for starting second semester classes"
              "he can not take any second semester class so first he has to take EMT1120, EMT1130  and some general education classes like ENG, MAT, PHY for which no prerequisites needed or student alreday taken prerequsite classes."
                "Have a user friendly but straight forward conversation and do not use sentences which not needed",
    tools=[pdf_tool],
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
    description='Read the pdf file and find the courses that match the student query: {query}. Strongly consider the prequisites and corequisites for each course.Pre-requisite is Classes you must take prior to the specific class.Co-requisite is Classes you can take along with the desired class if you have not taken them before' ,
    expected_output='A list or description of courses that match the student query, including the course name, prerequisites, and corequisites. Be accurate and only give answer, do not give extra things',
    agent=recommender
)

validate = Task(
    description='Write the exact correct answer for the student and validate the answer given by recommender',
    expected_output='Complete correct answer.',
    agent=validator
)


identifier_crew = Crew(
    agents=[query_identifier_agent],
    tasks=[identify_query_task])
general_answer_crew = Crew(
            agents=[general_conversation_agent],
            tasks=[general_conversation_task]
        )
task_answer_crew = Crew(
            agents=[recommender, validator],
            tasks=[recommend, validate]
        )

def task_execution(query):
    inputs = {
        "query": query
    }
    query_type =  identifier_crew.kickoff(inputs=inputs)
    query_type = str(query_type)
    # print("query type is:::::::",str(query_type))
    if query_type == 'casual':
        answer = general_answer_crew.kickoff(inputs=inputs)
        return answer
        
    elif query_type == 'task':
        answer = task_answer_crew.kickoff(inputs=inputs)
        return answer
    else:
        return "Invalid query type"
    
def get_answer(query):
    final_answer = task_execution(query)
    return final_answer