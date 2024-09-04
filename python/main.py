import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pandasai.llm import OpenAI
import pandas as pd
import os
from pandasai import Agent
from fastapi.responses import JSONResponse, FileResponse
import uuid
import shutil
from openai import OpenAI as ResponseAI
from loguru import logger


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Directory where the uploaded files will be saved
UPLOAD_DIR = "uploads"
IMAGE_DIR = "images"
LLM = OpenAI(api_token=os.getenv("OPENAIKEY"))
CLIENT = ResponseAI(api_key = os.getenv("OPENAIKEY"))

logger.add(os.path.join("logs", "file_{time}.log"), rotation="12:00")


class QUERY(BaseModel):
    query_text: str
    filename: str

def response_gen(query, response):
    """
    Generates a professionally crafted response by combining a given query and its answer.

    This function uses an AI model to combine a provided question and answer into a well-formed, professional response.

    Args:
        query (str): The question or query string.
        response (str): The answer or response string.

    Returns:
        str: A professionally crafted response based on the provided query and response.
    """

    # Prepare the prompt for the AI model
    prompt = f"""Combine question and answer to make a good answer response. The question is '{query}' and the answer is '{response}'. Professionally craft this and respond only with the answer.

    Example Response: Your current profit is 1234"""

    logger.info("Prompt created for the AI model: %s", prompt)

    try:
        # Generate the response using the AI model
        completion = CLIENT.chat.completions.create(
            # model="gpt-4",
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"{prompt}"},
                {"role": "user", "content": f"Craft answer"}
            ],
        )
        # Extract the generated response
        crafted_response = completion.choices[0].message.content
        logger.info("Response successfully generated.")
    except Exception as e:
        logger.error("Failed to generate response: %s", str(e))
        raise

    return crafted_response


def query_generator(query, filename):
    """
    Generates a response to a query by interacting with an AI agent using a DataFrame loaded from a CSV file.
    
    This function loads a CSV file into a DataFrame, initializes an AI agent, and uses the agent to chat 
    and generate a response. Depending on the type of response, it either generates a URL for an image or 
    crafts a text response.

    Args:
        query (str): The question or query string.
        filename (str): The name of the CSV file containing data to be processed.

    Returns:
        dict: A dictionary containing the original query, the generated answer, and the image URL (if applicable).
    """
    
    # Load the DataFrame from the CSV file
    try:
        df = pd.read_csv(os.path.join("uploads", filename))  # SmartDataframe can be uncommented if needed
        logger.info("DataFrame loaded from file: %s", filename)
    except Exception as e:
        logger.error("Failed to load DataFrame from file: %s", filename)
        raise
    
    # Initialize the AI agent with the DataFrame
    agent = Agent(df, config={"verbose": True, "llm": LLM})
    logger.info("AI agent initialized.")
    
    # Generate the response by chatting with the AI agent
    try:
        response = str(agent.chat(query))
        logger.info("Response generated from AI agent.")
    except Exception as e:
        logger.error("Failed to generate response from AI agent: %s", str(e))
        raise
    
    try:
        # Check if the response is a file path for an image
        split_response = response.split(".")
        if split_response[-1] == "png":
            logger.info("Response identified as an image file.")
            
            # Copy the image file to the destination directory with a UUID-based name
            os.makedirs(IMAGE_DIR, exist_ok=True)  

            image_path = copy_file_with_uuid(str(response), IMAGE_DIR)
            base_name = os.path.basename(image_path)
            base_url = "http://127.0.0.1:3002/get-image"  # Adjust if needed
            url = f"{base_url}/{base_name}"
            
            result = {"query": query, "answer": "", "image_url": url}
            logger.info("Image URL generated: %s", url)
        else:
            logger.info("Response identified as text.")
            
            # Generate a crafted text response
            response = response_gen(query, response)
            result = {"query": query, "answer": response, "image_url": ""}
            logger.info("Text response generated.")
    except Exception as e:
        logger.error("An error occurred during response processing: %s", str(e))
        raise
    
    return result



def copy_file_with_uuid(source_file, destination_folder):
    """
    Copies a file to a specified destination folder with a unique UUID filename and the same file extension.
    
    The function generates a new UUID, appends the original file extension, and then copies the file
    to the destination folder with the newly generated name.

    Args:
        source_file (str): The path to the source file that needs to be copied.
        destination_folder (str): The path to the destination folder where the file will be copied.

    Returns:
        str: The path to the newly created file with a UUID-based name in the destination folder.
    """

    # Generate a new UUID for the filename
    unique_filename = str(uuid.uuid4())
    logger.info("Generated UUID for the filename: %s", unique_filename)
    
    # Extract the file extension from the source file
    _, file_extension = os.path.splitext(source_file)
    logger.info("Extracted file extension: %s", file_extension)
    
    # Create the full path for the destination file with the UUID and original extension
    destination_file = os.path.join(destination_folder, unique_filename + file_extension)
    logger.info("Destination file path: %s", destination_file)
    
    try:
        # Copy the source file to the destination folder with the new name
        shutil.copy(source_file, destination_file)
        logger.info("File successfully copied to: %s", destination_file)
        
    except Exception as e:
        logger.error("Failed to copy the file: %s", str(e))
        raise

    return destination_file

@app.get("/get-image/{image_name}")
def get_image(image_name: str):
    """
    Endpoint to retrieve an image file from the server.

    This endpoint receives an image file name, checks if the image exists in the designated directory, 
    and returns the image file if found. If the image does not exist, it raises a 404 error.

    Args:
        image_name (str): The name of the image file to be retrieved.

    Returns:
        FileResponse: The image file with the correct media type if found.
    
    Raises:
        HTTPException: If the image file is not found, a 404 status code is returned.
    """

    # Construct the full file path
    file_path = os.path.join(IMAGE_DIR, image_name)
    logger.info("Constructed file path: %s", file_path)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        logger.warning("Image not found: %s", image_name)
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Return the image file with the appropriate media type
    logger.info("Returning image file: %s", image_name)
    return FileResponse(path=file_path, media_type="image/jpeg")



@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload an Excel or CSV file and convert it to a CSV format.

    This endpoint handles file uploads, ensuring the file is an Excel or CSV file. 
    If the file is an Excel file, it converts the file to CSV format. The CSV file 
    is then saved with a unique UUID-based name in the designated upload directory.

    Args:
        file (UploadFile): The uploaded file object.

    Returns:
        dict: A dictionary containing the new filename of the saved CSV file.
    
    Raises:
        HTTPException: If the uploaded file is not an Excel or CSV file, a 400 status code is returned.
    """

    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info("Upload directory verified or created: %s", UPLOAD_DIR)
    
    # Get the file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    logger.info("Uploaded file extension: %s", file_extension)

    # Validate the file extension
    if file_extension not in [".xls", ".xlsx", ".csv"]:
        logger.warning("Invalid file type uploaded: %s", file_extension)
        raise HTTPException(status_code=400, detail="Only Excel and CSV files are allowed.")
    
    # Generate a unique filename for the CSV
    csv_filename = f"{uuid.uuid4()}.csv"
    csv_filepath = os.path.join(UPLOAD_DIR, csv_filename)
    logger.info("CSV file will be saved as: %s", csv_filepath)
    
    try:
        # Process the file based on its extension
        if file_extension in [".xls", ".xlsx"]:
            logger.info("Processing Excel file.")
            df = pd.read_excel(file.file)
            df.to_csv(csv_filepath, index=False)
            logger.info("Excel file converted to CSV and saved.")
        elif file_extension == ".csv":
            logger.info("Processing CSV file.")
            with open(csv_filepath, "wb") as f:
                f.write(await file.read())
            logger.info("CSV file saved.")
    except Exception as e:
        logger.error("Failed to process and save the file: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while processing the file.")
    
    return {"filename": csv_filename}

@app.post("/query")
async def generate_query_route(query: QUERY):
    """
    Endpoint to generate a response for a given query based on data in a specified CSV file.

    This endpoint accepts a query and a filename, generates a response using the `query_generator` function,
    and returns the response as a JSON object.

    Args:
        query (QUERY): An object containing the query text and the filename of the CSV file.

    Returns:
        JSONResponse: A JSON response containing the generated response from the query.
    
    Raises:
        HTTPException: If an error occurs during query generation.
    """
    
    try:
        logger.info("Received query: %s", query.query_text)
        logger.info("Using file: %s", query.filename)

        # Generate the response using the query_generator function
        response = query_generator(query.query_text, query.filename)
        logger.info("Response generated successfully.")
    except Exception as e:
        logger.error("Failed to generate response: %s", str(e))
        raise HTTPException(status_code=500, detail="An error occurred while generating the query response.")
    
    return JSONResponse(content=response)
