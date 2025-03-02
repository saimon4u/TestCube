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
            credential_content = ""
            with open(media / "credential.txt", "r") as f:
                credential_content += f.read()
            _system_prompt = f'You are an android input test case generator tool called Testcube. Your work is to find best input for a input field.I have some existing credential input. Here is the credentials i have. Credentials: \n{credential_content}. Now after every input field found i will give you a prompt. The prompt will look like "Enter your email" / "Enter Password" / "Username" etc. Your work is to find for this prompt what existing credential i should use. My credentials are in key value format. You have to give me the key name only with proper case maintained. If you found something that you previously encountered than replay the previous reponse. Like if you found an example@gmail.com but previously you responded email for "Enter your email" than respond email again or match with existing credential that for which field it is best suited.\nExample:\nCredentials:\nemail: saimon@gmail.com\npass: 12345678\nprompt: Enter your email\nresponse: email\nprompt: Enter Password\nresponse: pass'
            GeminiAi._chat = model.start_chat(
                history=[
                    {"role": "user", "parts": _system_prompt},
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