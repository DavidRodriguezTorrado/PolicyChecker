import openai

def query_custom_gpt(message, model="gpt-4o", temperature=0.0, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, stop=None):
    """
    Queries the OpenAI API to get a text response from the custom GPT model.

    Parameters:
    - message (str): The message to send to the model.
    - model (str): The model to use (default is "gpt-4o").
    - temperature (float): Controls the randomness of the response (0.0 for deterministic output).
    - top_p (float): Controls the diversity of the output (1.0 considers all possible tokens).
    - frequency_penalty (float): Penalizes new tokens based on their frequency (0.0 means no penalty).
    - presence_penalty (float): Penalizes new tokens based on whether they appear in the text so far (0.0 means no penalty).
    - stop (str or list): A stop sequence to end the response generation.

    Returns:
    - str: The plain text response from the model.
    """
    try:
        # Make a request to the OpenAI API for chat completion
        response = openai.ChatCompletion.create(
            model=model,  # The model to use for the chat completion
            messages=[
                {"role": "user", "content": message}  # The user message to send to the model
            ],
            temperature=temperature,  # Controls randomness of the model's output
            top_p=top_p,  # Controls diversity via nucleus sampling
            frequency_penalty=frequency_penalty,  # Penalize repeated tokens
            presence_penalty=presence_penalty,  # Penalize tokens based on their presence
            stop=stop  # Optional stop sequence
        )
        # Extract and return the plain text response
        return response['choices'][0]['message']['content']
    except Exception as e:
        # Handle any exceptions that occur during the API call
        return f"An error occurred: {str(e)}"
