from flask import Flask, render_template, request, Response
from flask_cors import CORS
from flask import jsonify
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.llms import Anthropic
from tempfile import TemporaryDirectory
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import SequentialChain
from agent import plan_execute
from langchain import SerpAPIWrapper
from langchain.agents.tools import Tool

working_directory = TemporaryDirectory()

load_dotenv()

app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"message": "Hello from Flask!"}
    return jsonify(data), 200


@app.route('/api/plan', methods=['POST'])
def basic_impl():
    """Take the context and starts the sequence chain"""
    data = request.get_json()
    idea = data['idea']
    problemDefinition = data['problemDefinition']
    targetAudience = data['targetAudience']
    constraints = data['constraints']
    solutionOverview = data['solutionOverview']

    analysis_chain = analysis_bot()
    project_chain = project_planner()
    req_detailer_chain = req_detailer()
    risk_chain = risk_assess()
    overall_chain = SequentialChain(chains=[analysis_chain,req_detailer_chain, project_chain,risk_chain],input_variables=["idea","problemDefinition","targetAudience","constraints","solutionOverview"],output_variables=["requirements_USPs", "requirements_details", "project_plan","risk_assessment"],verbose=True)
    answer = overall_chain(
        {
            "idea":idea,
            "problemDefinition":problemDefinition,
            "targetAudience":targetAudience,
            "constraints":constraints,
            "solutionOverview":solutionOverview,
        }
    )

    return jsonify({'answer': answer})


# ############### CHAINS #####################

def analysis_bot():
    """Takes context and generates requirements and USPs"""
    llm = Anthropic(streaming=True,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),temperature=0.7)
    template = """You are a Software Development analysis bot. Your job is to take an idea, a problem for certain target audience and based on the
    target audience you need to analyse the given information, you should generate functional requirements and non functional requirements.
    You should also identify USPs (unique selling points) this software should have to compete in the market.

    These are requirements and USPs for given software description:
    """
    prompt_template = PromptTemplate(input_variables=["context"], template=template)
    analysis_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="requirements_USPs")
    return analysis_chain


def req_detailer():
    """Take a requirement and makes it more detailed"""
    llm = Anthropic(streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), temperature=0)
    template = """You are a senior software developer bot who can write amazing code. Now, given the requirements {requirements_USPs}, return the requirements in a json:
    requirement: To do something, priority : low or med or high, time_to_complete: in days.

    Make sure to keep the format simple to avoid errors and make sure to cover all the requirements
    """
    prompt_template = PromptTemplate(input_variables=["requirements_USPs"], template=template)
    req_prior = LLMChain(llm=llm, prompt=prompt_template, output_key="requirements_details")
    return req_prior


def project_planner():
    """Takes requirements and generates project plan"""
    llm = Anthropic(streaming=True,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),temperature=0.5)
    template = """You are a software developement planning agent.
    Given the requirements and develop a proper project plan that identifies, prioritizes, and assigns the tasks and
    resources required to build the project
    Requirements:
    {requirements_USPs}
    Project Plan in the order of priority:
    """
    prompt_template = PromptTemplate(input_variables=["requirements_USPs"], template=template)
    project_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="project_plan")

    return project_chain


def risk_assess():
    llm = Anthropic(streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), temperature=0)
    template = """You are a software development risk assessment tool that designs the system for the 
    following software idea and requirements along with the following project plan {project_plan}. I want you to write up a risk assessment tool.

    Risks Involved and mitigation:
    """
    prompt_template = PromptTemplate(input_variables=["project_plan"], template=template)
    risk_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="risk_assessment")

    return risk_chain


############# AGENTS ###############################


def market_analysis_agent_search():
    """ Takes an area to research and does so using internet"""
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name = "Search",
            func=search.run,
            description="Useful to learn about best pratice to do something or to know about current events you can use this to search"
        )
        ,
        # Tool(
        # name="human",
        # description="Useful for when you need to get input from a human",
        # func=input,  # Use the default input function
        # )
    ]

    market_agent = plan_execute(tools)

    prompt = """"""

    summarised_answer = market_agent.run(prompt)
    

# @app.route('/basic', methods=['POST'])
# def basic_impl():
#         data = request.get_json()
#         context = data['context']
#         prompt = f"""
#         You are an AI smart agent that helps users by generating  
#         Functional Requirements, Non-Functional Requirements. All of the them should be based on the following information 
#         but Don't ask the information that is already given:
#         {context}
#         Make the the answer is the form of JSON object with the following format:
#         'action': 'the action ',
#         'action_input': 'the input of the action',
#         Try to deduce as much as possible from the data but if you think you dont have information about something you cant find using the tools provided, ask for
#         human feedback. Don't ask the information that is already given
#         """

#         agent = plan_execute()

#         answer = agent.run(prompt)

#         return jsonify({'answer': answer})

# @app.route('/requirements', methods=['POST'])
# def fun_non_fun_requirements_agent():
#     data = request.get_json()
#     context = data['context']

#     prompt = f"""
#     I want you to write Functional Requirements and Non functional Requirements for the following application idea:  APP IDEA STARTS HERE 
#     {context} APP IDEA ENDS HERE
#     The requirements you write should be clear, concise, and complete.
#     You should follow industry-standard software engineering practices when writing the requirements.

#     Try to deduce as much as possible from the data 
#     but if you think you dont have information about something you cant find using the tools provided

#     Make sure to keep the format simple to avoid errors
#     """

#     # requirements_agent = plan_execute()
#     requirements_agent = plan_execute()

#     answer = requirements_agent.run(prompt)

#     return jsonify({'answer': answer})


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(port=4000)
