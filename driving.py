import openai
import json
import sounddevice as sd
import wavio as wv

freq = 44100
duration = 5


def record_audio():
    filename = "audio/order.mp3"
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)
    print("Recording Audio")
    sd.wait()
    wv.write(filename, recording, freq, sampwidth=2)
    return filename


def transcribe_audio(audio_file):
    audio_file = open(audio_file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file).text
    return transcript


def place_mcdonalds_order(order):
    """Place an order at McDonald's and return the order details"""
    order_info = {
        "order": {
            "items": order,
        }
    }
    return json.dumps(order_info)


def end_order():
    print("END ORDER")


def append_chat_message(messages, role, user_input, function_name=None):
    if function_name:
        messages.append(
            {"role": role, "content": user_input, "name": function_name}
        )
    else:
        messages.append({"role": role, "content": user_input})
    return messages


def run_conversation(messages):
    # Step 1: send the conversation and available functions to GPT
    functions = [
        {
            "name": "place_mcdonalds_order",
            "description": "Place an order at McDonald's and return the order details. Only call this when the user has finalized their order and in your final response read them the price of their order as well.",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "string",
                            "description": "The json format of the McDonald's order. It should include the items and customizations.",
                        },
                    },
                "required": ["order"],
            },
        },
        {
            "name": "end_order",
            "description": "Call this function after you confirm the customer's order. This will end the conversation.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
            "required": [],
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "place_mcdonalds_order": place_mcdonalds_order,
            "end_order": end_order,
        }
        function_name = response_message["function_call"]["name"]
        function_to_call = available_functions[function_name]
        print("FUNCTION CALLED: " + function_name)
        if function_name == "end_order":
            print("Thanks for your money")
            return messages, False  # replace messages

        function_args = json.loads(
            response_message["function_call"]["arguments"]
        )
        function_response = function_to_call(
            order=function_args.get("order"),
        )

        # Step 4: send the info on the function call and function response to GPT
        # extend conversation with assistant's reply
        messages.append(response_message)
        append_chat_message(messages, "function",
                            function_response, function_name)
        print("FUNCTION CALLED: SUCCESS")
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )
        messages.append(second_response["choices"][0]["message"])
        print(second_response["choices"][0]["message"].content)
    else:
        append_chat_message(messages, "assistant",
                            response_message.content)
        print(response_message.content)
    return messages, True


transcript = transcribe_audio("audio/order.mp3")
messages = [
    {"role": "system", "content": "You are a helpful, drive through McDonald's assistant. Your goal is to take a customer's food order from items only on the McDonald's menu. Your goal is to have a short conversation with the customer and after you take their order, you will call the function to 'place_mcdonalds_order' where you will finalize the user's purchase. You must only talk about ordering food, item menu prices and nutritional information."},
    # {"role": "user", "content": transcript}
]

continue_conversation = True
while continue_conversation:
    audio = transcribe_audio(record_audio())
    print(audio)
    append_chat_message(messages, "user", audio)
    messages, continue_conversation = run_conversation(messages)

    '''
    continue_conversation = input(
        "Continue conversation? (y/n): ").lower()
    if continue_conversation == 'n':
        continue_conversation = False
    '''
