import google.generativeai as genai
import pathlib
import json
import os

media = pathlib.Path(__file__).parents[1] / "droidbot/files"

import os
import json

def parse_and_save_json(json_str, folder_path="files"):
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Strip and clean input
        json_str = json_str.strip()
        json_lines = json_str.split('\n')
        json_str = '\n'.join(json_lines[1:-1])  # Remove enclosing brackets

        # Parse JSON
        data = json.loads(f"[{json_str}]")  
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None

    # Write each object to a separate .txt file
    for i, obj in enumerate(data[0]):
        file_name = os.path.join(folder_path, f"file{i+1}.txt")
        with open(file_name, "w", encoding="utf-8") as f:
            # Write the key-value pairs in plain text
            for key, value in obj.items():
                f.write(f"{key}: {value}\n")

class GeminiAi:
    _chat = None
    _input = None
    genai.configure(api_key="AIzaSyDy_VQnRxk5LqrOvEtpdZzxXdM8tIt_0xg")
    __model = genai.GenerativeModel("gemini-1.5-flash-latest")
    @classmethod
    def get_chat(cls):
        if cls._chat is None:
            # genai.configure(api_key="AIzaSyDy_VQnRxk5LqrOvEtpdZzxXdM8tIt_0xg")
            current_filename = ""
            with open(media / "current.txt", "r") as f:
                current_filename = f.read()
            credential_content = ""
            with open(media / current_filename, "r") as f:
                credential_content += f.read()
            _system_prompt = f'You are an android input test case generator tool called Testcube. Your work is to find best input for a input field.I have some existing credential input. Here is the credentials i have. Credentials: \n{credential_content}. Now after every input field found i will give you a prompt. The prompt will look like "Enter your email" / "Enter Password" / "Username" etc. Your work is to find for this prompt what existing credential i should use. My credentials are in key value format. You have to give me the key name only with proper case maintained. If you found something that that is not your prompt type like if you encounter a prompt example@gmail.com then you have to be smart and send response as email because this value belong to an email.Also if you found **** then it must be a password so respond pass. So finally just dont look for the key name if you found something that matches any value in the existing credential then also repond the corresponding key name.\nExample:\nCredentials:\nemail: saimon@gmail.com\npass: 12345678\nprompt: Enter your email\nresponse: email\nprompt: Enter Password\nresponse: pass\nprompt: Bhuiyan\nresponse: l_name'
            cls._chat = cls.__model.start_chat(
                history=[
                    {"role": "user", "parts": _system_prompt},
                ]
            )
        return cls._chat
    
    @classmethod
    def generate_random_input(cls):
        current_filename = ""
        with open(media / "current.txt", "r") as f:
            current_filename = f.read()
        credential_content = ""
        with open(media / current_filename, "r") as f:
            credential_content += f.read()
        _system_prompt = f'You are an android input test case generator tool called Testcube. Your work is to simulate mock data to test an android app. I have some existing credentials input for testing. Here is the credentials i have. Credentials:\n{credential_content}. Now you need to create exactly 10 copy of this credentials in json format and return me an array of json. For each variation consider empty string, variatiion in gmail format, variation in password length, variation in upper case lower case etc. Also create variation in all of the field.'
        chat = cls.__model.start_chat(
            history = [
                {"role": "user", "parts": _system_prompt}
            ]
        )
        response = chat.send_message("Generate now")
        parse_and_save_json(response.text)
    @classmethod
    def getInputDict(cls):
        if cls._input is None:
            current_filename = ""
            with open(media / "current.txt", "r") as f:
                current_filename = f.read()
                
            credential_file = genai.upload_file(media / current_filename)
            response = cls.__model.generate_content(["Give me a json object from this file. Don't give me an extra character instead of that json object. Serve every value as string.", credential_file])
            json_data = response.text.strip().split("\n")
            json_data.remove(json_data[0])
            json_data.remove(json_data[len(json_data) - 1])
            json_data = "\n".join(json_data)
            print(json_data)
            cls._input = json.loads(json_data)
        return cls._input