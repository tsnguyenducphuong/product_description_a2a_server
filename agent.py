import random
from datetime import date, datetime, timedelta

from google.adk.agents import LlmAgent, SequentialAgent,LoopAgent

LLMAGENT_MODEL = "gemini-2.5-flash-preview-04-17"

 
# DIRECTLY PUT THE SUBAGENTS HERE -------------------------------------------------------------
initial_product_descriptor_agent = LlmAgent(
    name="initial_product_descriptor_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model=LLMAGENT_MODEL,
    description="Generate product description from product image",
    instruction="""
    You are a helpful assistant that generate product description that is suitable for ecommerce from product image provided by user.
    The description will be put to context as product description.
    
    IMPORTANT: Your response MUST be a valid JSON that matching this structure:
         {
             "product_description": the generate product description,
             "status": success if successfully describe the image provided by the user, failed otherwise, 
             "feedback": ""
         }

    Then your task is complete, handover to the next agent.
    """,
    output_key="product_description"
)
product_descriptor_reviewer_agent = LlmAgent(
    name="product_descriptor_reviewer_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model=LLMAGENT_MODEL,
    description="Review product description for great ecommerce product listing description",
    instruction="""
    You are a helpful assistant that review the product description in the context {product_description} and provide feedback how to improve the description for a better ecommerce product listing.
 

    IMPORTANT: Your response MUST be a valid JSON that matching this structure:
         {
             "product_description": the generate product description,
             "status": success if successfully describe the image provided by the user, failed otherwise, 
             "feedback": the feedback on how to improve the product description provided or say 'it looks good' if the description is good and no need to be improved.
         }
    Then your task is complete, handover to the next agent.
    """,
     output_key="feedback"
)

product_descriptor_refiner_agent = LlmAgent(
    name="product_descriptor_refiner_agent",
    # https://ai.google.dev/gemini-api/docs/models
    model=LLMAGENT_MODEL,
    description="Product Description refiner that refine a product description for better content.",
    instruction="""
    You are a helpful assistant that help to refine a {product_description} based on {feedback}.
    The put the refined description to {product_description}.
    If the feedback contains it looks good then the product description is fine and it's the final product description no need to further refine.

    IMPORTANT: Your response MUST be a valid JSON that matching this structure:
         {
             "product_description": the newly refined product description,
             "status": final if the feedback said it looks good, success if successfully describe the image provided by the user, failed otherwise, 
             "feedback": the current feedback on how to improve the product description or say it looks good and it is the final product description if the feedback said it looks good
         }

    Then your task is complete, handover to the next agent.
    """,
)

# Create the Product Description Review and Refine Loop Agent
product_descriptor_loop_agent = LoopAgent(
    name="product_descriptor_loop_agent",
    max_iterations=2, #limit to 2 iterations to avoid infinite loops
    sub_agents=[product_descriptor_reviewer_agent,product_descriptor_refiner_agent],
    description="Loop through the generated product description to review and refine with review agent and refine agent until specified requirements for the product description are matched"
) 


product_descriptor_agent = SequentialAgent(
    name="product_descriptor_agent",
    sub_agents=[
                initial_product_descriptor_agent, #Step 1: Generate the first draft version of product description from product image
                product_descriptor_loop_agent #Step 2: Loop through the generated product description to review and refine with review agent and refine agent until specified requirements for the product description are matched
                ],
    description="Generates product description from product image, review and refine content with several subagents", 
)

def create_adk_agent() -> SequentialAgent:
    return product_descriptor_agent


