from langflow import CustomComponent
from langchain.chat_models import AzureChatOpenAI
from langchain.llms.base import BaseLLM
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.schema import Document
from langchain.llms.base import BaseLLM
import os

class InSourceAzureChatOpenAI(CustomComponent):
    display_name: str = "Azure Chat OpenAI (InSource)"
    description: str = "InSource Managed Azure Chat OpenAI, Specific setting required"
    documentation: str = "https://insource.asia"
    field_config = {
        "code": {"show": False}
    }

    def build(self, deployment_name: str) -> BaseLLM:
        llm=AzureChatOpenAI(
            client=None,
            openai_api_base=str(os.getenv("OPENAI_API_BASE")),
            openai_api_version=str(os.getenv("OPENAI_API_VERSION")),
            deployment_name=deployment_name,
            openai_api_key=str(os.getenv("OPENAI_API_KEY")),
            openai_api_type=str(os.getenv("OPENAI_API_TYPE"))
        )
        return llm
