import google.generativeai as genai

class GeminiAi:
    _chat = None
    _input = {
        "email": "saimon@gmail.com",
        "password": "12345",
        "username": "saimon"
    }
    @classmethod
    def get_chat(self):
        if GeminiAi._chat is None:
            genai.configure(api_key="AIzaSyD1FDtnO_YU9psuk5Ybn44FLb2_CJhSseU")
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            GeminiAi._chat = model.start_chat(
                history=[
                    {"role": "user", "parts": "I have some input field in my app. The following field have some text like enter email or enter password. Your work is to find what should i enter email or password or something else. That means i will give you a text you have to find what type of input field is needed. Give me the only field name in all small case letter. If the field name have multiple word use underscore between them."},
                ]
            )
        return GeminiAi._chat
    @classmethod
    def getInputDict(self):
        return GeminiAi._input