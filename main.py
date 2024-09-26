import os
from dotenv import load_dotenv
import autogen
from autogen import GroupChat, GroupChatManager

# Load environment variables
load_dotenv()
config_list = [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

productmanager = autogen.ConversableAgent(
        name="ProductManager",
        llm_config=llm_config,
        system_message="You are a Product Manager overseeing the project. Ensure the team builds an effective webpage to showcase all necessary sections that works best for a product manager job search."
        "",
        description="Oversees the direction and success of the project of building a personal webpage.",
)

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
    description="Seek input from human.",
)

coder = autogen.AssistantAgent(
        name="SoftwareDeveloper",
        llm_config=llm_config,
        system_message="You are a Software Developer responsible for coding.",
        description="Generate code files that are required for webpage. It could be html, css, flask anything that is required for the webpage project.",
)

designer = autogen.AssistantAgent(
        name="Designer",
        llm_config=llm_config,
        system_message="You are a Designer creating the UI/UX.",
        description="Come up with innovative user design for clearly showcasing skills, experience, projects, etc for the personal webpage.",
)

researcher = autogen.AssistantAgent(
        name="Researcher",
        llm_config=llm_config,
        system_message="You are a Research Assistant gathering information.",
        description="Research on what makes a successful personal webpage for a product manager to be successful in the job search.",
)

group_chat = GroupChat(
    agents=[productmanager, user_proxy, coder, designer, researcher],
    messages=[],
    max_round=10,
    send_introductions=True,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)

chat_result = productmanager.initiate_chat(
    group_chat_manager,
    message="We need to build a personal portfolio or webpage that can be used by a product manager looking for a PM job in the US."
    "The webpage should showcase relevant skills, experience, projects and products managed by the respective person. Assume the person already has adequate product manager experience."
    "Fill in with relevant work to showcase a successful profile. The output should be a html and css from the coder which can be deployed on cloud for hosting.",
    summary_method="reflection_with_llm",
)

print(chat_result.summary)