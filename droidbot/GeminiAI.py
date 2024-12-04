import google.generativeai as genai
import pathlib
import json

media = pathlib.Path(__file__).parents[1] / "droidbot"

class GeminiAi:
    _chat = None
    _input = None
    
    @classmethod
    def get_chat(self):
        if GeminiAi._chat is None:
            genai.configure(api_key="AIzaSyDy_VQnRxk5LqrOvEtpdZzxXdM8tIt_0xg")
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            GeminiAi._chat = model.start_chat(
                history=[
                    {"role": "user", "parts": "I have some input field in my app. The following field have some text like enter email or enter password. Your work is to find what should i enter email or password or something else. That means i will give you a text you have to find what type of input field is needed. Give me the only field name in all small case letter. If the field name have multiple word use underscore between them. Also give some similar type of field name like for user_name you can generate user_id or uid or something like that. Because we don't know what user uses for that particular field so give me those similar type of name also in csv format all in one line."},
                ]
            )

            credential_file = genai.upload_file(media / "credential.txt")
            response = model.generate_content(["Give me a json object from this file. Don't give me an extra character instead of that json object.", credential_file])
            json_data = response.text.strip().split("\n")[1]
            GeminiAi._input = json.loads(json_data)
        return GeminiAi._chat
    
    @classmethod
    def getInputDict(self):
        return GeminiAi._input