import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

from core.models import Category


def get_categories():
    # Retrieve all categories from the database
    return [category.name for category in Category.objects.all()]


def process_with_llm(user_message):
    categories = get_categories()  # Fetch the category list
    categories_list = ', '.join(categories)  # Create a string list for prompt

    # Define your template with the list of categories included
    prompt_template = f"""
    You are a sophisticated language model designed to convert unstructured user input into structured JSON data. 
    Your task is to transform a user’s free text message into a JSON object suitable for creating a task in a Django model. 
    This JSON object must contain the fields: title, description, and category.

    The list of categories is stored in a database table, and currently includes the following entries: 
    {categories_list}. Use this list to categorize the task appropriately.

    Instructions:
    1. Extract the **title** from the first sentence of the user’s message.
    2. Extract the **description** from the second sentence of the user’s message.
    3. **Identify the category** using the provided list of categories while keeping in mind that these categories are database entries.

    Finally, format the extracted information into a JSON object with the fields: title, description, and category.

    User Message: "{user_message}"

    Expected JSON Format:
    {{
      "title": "<extracted_title>",
      "description": "<extracted_description>",
      "category": "<identified_category>"
    }}
    Output the JSON object directly.
    """

    # Initialize the OpenAI provider in Langchain
    llm = OpenAI(model="gpt-3.5-turbo")  # Use the appropriate OpenAI model

    # Create a prompt template
    prompt = PromptTemplate(template=prompt_template, input_variables=["user_message"])

    # Create a chain with the model and the crafted prompt
    chain = LLMChain(llm=llm, prompt=prompt)

    # Execute the chain with the given user_message
    result = chain.run(user_message=user_message)

    # Try to parse the result as JSON
    try:
        processed_data = json.loads(result.strip())
        return processed_data
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        print(f"Response was: {result}")
        return None


