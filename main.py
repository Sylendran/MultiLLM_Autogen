import os
from dotenv import load_dotenv
import autogen
from autogen import GroupChat, GroupChatManager, ConversableAgent
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download
from PyPDF2 import PdfReader
from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor
import tempfile
from utils.web_scrapper_utils import scrape_website


# Load environment variables
load_dotenv()

#loading LLM configs
config_list = [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]

#loading huggingface configs and dataset
repo_id = os.getenv("HUGGINGFACE_REPO")
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
#dataset = load_dataset(repo_id, use_auth_token=huggingface_api_key)

api = HfApi()

# List files in the repository
files = api.list_repo_files(repo_id=repo_id, repo_type='dataset', token=huggingface_api_key)

# Extract text from PDFs in the repository
resume_content = ''

# Your current website URL
current_website_url = 'https://sites.google.com/view/sylendranarunagiri/about'  # Replace with your actual URL
# Scrape the entire website
webpage_content = scrape_website(current_website_url)

temp_dir = tempfile.TemporaryDirectory()

# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files and PRD.
)


for file in files:
    if file.lower().endswith('.pdf'):
        print(f"Processing file: {file}")
        local_file_path = hf_hub_download(
            repo_id=repo_id,
            filename=file,
            repo_type='dataset',
            token=huggingface_api_key
        )
        # Extract text from the PDF
        try:
            reader = PdfReader(local_file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
            resume_content += text + '\n'
        except Exception as e:
            print(f"Error reading {local_file_path}: {e}")


llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

productmanager = autogen.ConversableAgent(
        name="ProductManager",
        llm_config=llm_config,
        system_message=
    "You are a **Senior Product Manager** overseeing the development of a personal portfolio website for a Product Manager seeking employment in the US market. "
    "Your goal is to ensure the team builds a **sophisticated, industry-level website** that effectively showcases the individual's skills, experience, projects, and products managed. "
    "The website should include **modern design elements, images, interactive features, and a seamless user experience**. "
    "It should also include **links to the individual's LinkedIn, GitHub, contact information (email and phone)**, and any other relevant platforms. "
    "Provide clear guidance, set high expectations, and ensure the team collaborates effectively to deliver a top-notch website.",
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
        system_message= "You are a Senior Front-End Web Developer responsible for implementing the website using modern web technologies. "
        "Your task is to write clean, efficient, and maintainable code to create a responsive, interactive, and visually appealing website. "
        "Incorporate advanced features such as animations, interactive elements, and dynamic content where appropriate. "
        "Ensure the website includes images, formatting, color schemes, and click interactions. "
        "Include links to LinkedIn, GitHub, email, and phone contact information. "
        #"**For generating images, you can use the OpenAI API to create images based on the project's requirements.** "
        #"Write code to generate images using the OpenAI API and save them as JPG files in the 'images' folder within the working directory. "
        "Follow best practices in web development, including cross-browser compatibility, accessibility standards, and SEO optimization. ",
        #"Remember to handle API keys securely by using environment variables. Make use of the code executor agent to run commands to save your files to local folders.",
        description= "Generate code files and assets required for the webpage, including HTML, CSS, and images."
        "Use the OpenAI API to generate images based on project requirements and save them to the 'images' folder.",
)

code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the local command line code executor.
    human_input_mode="ALWAYS",  # Always take human input for this agent for safety.
    description= "Executes code like querying openai to generate image and then store it in temporary file location."
)

designer = autogen.AssistantAgent(
        name="Designer",
        llm_config=llm_config,
        system_message="You are a **UI/UX Designer** specializing in creating modern, user-friendly interfaces for web applications. "
    "Your responsibility is to design an **aesthetically pleasing and intuitive user interface** for the personal portfolio website. "
    "Develop a **cohesive visual theme** with appropriate **color schemes, typography, and imagery** that reflects the professionalism and personal brand of the Product Manager. "
    "Design **interactive elements, navigation menus, and layout structures** that enhance user engagement. "
    "Ensure that the design includes sections for **skills, experience, projects, products managed, and contact information**, with links to **LinkedIn, GitHub, email, and phone**."
    "You will also required images using DALL-E or Openai APIs and take coder's help to save it locally.",
        description="Come up with innovative user design for clearly showcasing skills, experience, projects, etc for the personal webpage.",
)

researcher = autogen.AssistantAgent(
        name="Researcher",
        llm_config=llm_config,
        system_message="You are a **Research Analyst** with expertise in **personal branding and digital presence** for professionals seeking employment. "
   "Your task is to **research current trends and best practices** in building personal portfolio websites for Product Managers targeting the US job market. "
    "Identify features, design elements, and content strategies that make such websites **stand out to recruiters and hiring managers**. "
    "Provide insights on effective use of **images, interactivity**, and integration with professional platforms like **LinkedIn and GitHub**. "
    "Gather examples of **exemplary portfolio websites** and summarize key takeaways that can be applied to this project.",
        description="Research on what makes a successful personal webpage for a product manager to be successful in the job search.",
)


group_chat = GroupChat(
    agents=[productmanager, user_proxy, coder, designer,researcher], #code_executor_agent
    messages=[],
    max_round=14,
    send_introductions=True,
)

group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)


# Combine with any existing content (e.g., resume_content)
combined_content = resume_content + '\n\n' + webpage_content

chat_result = productmanager.initiate_chat(
    group_chat_manager,
    message="Team, our goal is to build a sophisticated, industry-level personal portfolio website for a Product Manager seeking opportunities in the US market. "
    "We have the content from the current website, including all its sections and sub-pages. "
    "Your task is to analyze the existing content thoroughly and use it, along with the person's resume, to build an enhanced website that meets the following requirements:\n"
    "- Modern design with appropriate color schemes, typography, and high-quality images.\n"
    "- Responsive layout compatible with various devices and browsers.\n"
    "- Interactive elements such as animations, hover effects, and smooth navigation.\n"
    "- Sections highlighting skills, experience, projects, products managed, and personal achievements.\n"
    "- Integration of links to LinkedIn, GitHub, and other relevant professional platforms.\n"
    "- Contact information including email and phone, with clickable links.\n"
    "- Optimization for search engines (SEO) and adherence to accessibility standards.\n"
    #"- Include relevant images generated using the OpenAI API, saving them to the 'images' folder within the temporary directory.\n"
    #"- For example, for a project about 'building an AI chatbot,' generate an image of a futuristic cyborg AI bot. similarly images have to be created for all projects and products.\n\n"
    "Please use the comprehensive content provided below to extract the necessary information:\n\n The final output is a html file, css file and images to host on cloud and a 3 pager PRD document."
    f"{combined_content}\n\n"
    "Let's collaborate effectively to deliver a top-notch website that stands out to recruiters and hiring managers. The output should include all necessary code files (HTML, CSS, JavaScript) and any assets like images, ready to be deployed on the cloud.",
    summary_method="reflection_with_llm",
)

print(chat_result.summary)

print(os.listdir(temp_dir.name))