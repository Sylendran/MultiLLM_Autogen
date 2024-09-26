import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, demo

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Define the agents with their roles and initial prompts
agents = {
    "ProductManager": AssistantAgent(
        name="ProductManager",
        role="Product Manager",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Product Manager overseeing the project. Ensure the team builds an effective webpage to showcase all necessary sections that works best for a product manager job search."
    ),
    "SoftwareDeveloper": AssistantAgent(
        name="SoftwareDeveloper",
        role="Software Developer",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Software Developer responsible for coding."
    ),
    "Designer": AssistantAgent(
        name="Designer",
        role="Designer",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Designer creating the UI/UX."
    ),
    "Researcher": AssistantAgent(
        name="Researcher",
        role="Research Assistant",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Research Assistant gathering information."
    ),
    "Marketer": AssistantAgent(
        name="Marketer",
        role="Marketing Specialist",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Marketing Person promoting the product."
    ),
    "SalesRep": AssistantAgent(
        name="SalesRep",
        role="Sales Representative",
        llm_model="gpt-4o-mini",
        system_prompt="You are a Sales Representative selling the product."
    )
}

# Initialize the conversation
conversation = AgentConversation(agents=agents)

# Define the initial message from the Product Manager
initial_message = "Our goal is to collaboratively build a personal portfolio webpage for a product manager that can be hosted for free and viewed by anyone."
"the purspose of the webpage is to showcase all relevant projects, skills, experience that a potential hiring manager can see and be impressed to hire this product manager."

# Start the conversation
conversation.start_conversation(
    initiator="ProductManager",
    message=initial_message
)

# Run the conversation simulation
if __name__ == "__main__":
    conversation.run(max_turns=10)  # You can adjust the number of turns as needed


class CodeGeneratingAgent(autogen.AssistantAgent):
    def handle_response(self, response):
        super().handle_response(response)
        if "```" in response:
            code = self.extract_code(response)
            self.save_code(code)

    def extract_code(self, content):
        # Extract code between ``` ```
        start = content.find("```") + 3
        end = content.rfind("```")
        return content[start:end].strip()

    def save_code(self, code):
        filename = f"{self.name}_output.html"
        with open(filename, "w") as file:
            file.write(code)
        print(f"Code saved to {filename}")