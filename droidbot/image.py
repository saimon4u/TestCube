import PIL.Image
import google.generativeai as genai

image_path_1 = "before.png"  
image_path_2 = "after.png" 
sample_file_1 = PIL.Image.open(image_path_1)
sample_file_2 = PIL.Image.open(image_path_2)

genai.configure(api_key="AIzaSyABfZluj_e1uTMOR2fqseX99pYDD7saNec")
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

prompt = "Spot the difference of this two image. Observe those images deeply and give a proper explanation what is different."

response = model.generate_content([prompt, sample_file_1, sample_file_2])

print(response.text)
