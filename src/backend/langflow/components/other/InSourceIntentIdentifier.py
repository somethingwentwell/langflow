from langflow import CustomComponent

from langchain.llms.base import BaseLLM
from langchain import PromptTemplate
from langchain.chains.base import Chain
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)

class InSourceIntentIdentifier(CustomComponent):
    display_name: str = "Intent Identifier (InSource)"
    description: str = "Identify the intent of a message"
    documentation: str = "https://insource.asia"
    field_config = {
        "code": {"show": False}
    }

    def build(self, llm: BaseLLM, types: str) -> Chain:
        prompt_text = f"""You are a world class algorithm for extracting information in structured formats.
You can only choose the best values from the following list: {types}
Use the given format to extract information from the following input: {{input}}
Tip: Make sure to answer in the correct format and allowed value
        """
        prompt_template = PromptTemplate.from_template(prompt_text)
        json_schema = {
            "title": "Classify Intent",
            "description": "Identifying information about a message",
            "type": "object",
            "properties": {
                "intent": {"title": "Intent", "description": f"The intent of the message. Only the values from the following list are allowed: {types}", "type": "string"}
            },
            "required": ["intent"],
        }
        chain = create_structured_output_chain(json_schema, llm, prompt_template, verbose=True)
        return chain
