from modules.google_drive_manager import GoogleSheetsManager
from modules.open_ai_manager import GPT

# Test sheet: https://docs.google.com/spreadsheets/d/1HSDEh4eSRrPDlWaqzn98wIBJxySiDUjUFVqO1o9vUMo/edit#gid=0

gs = GoogleSheetsManager('AI for Google Sheets')
gpt = GPT()

def main():

  # In this system prompt, you want to give the AI a list of categories it can choose from. Here's an example below:
  # You will want to change this. 
  system_prompt = """ 

  You are an employee at Nike helping to categorize different kinds of shoes based on their name and a brief description.

  The categories you can choose from are:

  - Running shoes
  - Hiking shoes
  - Climbing shoes
  - Skate shoes
  - Trainers
  - Dress shoes
  - Sandals
  - Boots
  - Basketball shoes

  Given a name and brief description, you will place the shoe into the correct category based on what is most relevant to that shoe. 

  Example inputs/outputs:

  Input: Jordan 1 Mid: Inspired by the original AJ1, this mid-top edition maintains the iconic look you love while choice colors and crisp leather give it a distinct identity.
  Output: Basketball shoes

  Input: Air Max 90: Nothing as fly, nothing as comfortable, nothing as proven. The Nike Air Max 90 stays true to its OG running roots with the iconic Waffle sole, stitched overlays and classic TPU details. Classic colors celebrate your fresh look while Max Air cushioning adds comfort to the journey.
  Output: Running shoes

  Input: Nike Dunk Low: Created for the hardwood but taken to the streets, the Nike Dunk Low Retro returns with crisp overlays and original team colors. This basketball icon channels '80s vibes with premium leather in the upper that looks good and breaks in even better. Modern footwear technology helps bring the comfort into the 21st century.
  Output: Basketball shoes
  """

  # Setup our AI assistant with our system prompt and the model we want
  gpt.set_instructions(system_prompt)
  gpt.set_model('gpt-3.5-turbo')

  # This will use our module to create a dataframe and set it to this variablee.
  info_df = gs.create_dataframe(worksheet_name='categorizer')  
  info_df["Category"] = None


  # This counter will be used to periodically write the DF back to our sheet
  i=0
  
  for index, row in info_df.iterrows():

    # You can give the AI as much information in your sheet as you want, but you may need to adjust the code if so. 
    # This is designed to work with one name column and one description column in your sheet. 
    # If you want to categorize with more info, adjust your category prompt to include it here and add it into your system prompt examples. 
    try:
      category = gpt.get_response(f"{row['Name']}: {row['Description']}\n\n Respond with only the category and no other text.")
      info_df.at[index, "Category"] = category
      print(f"\u001b[32mSuccess!  \u001b[37m{row['Name']} placed into: {category}")
    except Exception as e:
      print(f"\u001b[31mFailed to categorize  \u001b[37m{row['Name']}...")
      
    # Writes to our sheet every 10 iterations in case we run into an issue.
    i +=1
    if i == 10:
      gs.write_dataframe_to_sheets(dataframe=info_df,worksheet_name='Output',)

  gs.write_dataframe_to_sheets(dataframe=info_df,worksheet_name='Output',)

if __name__ == '__main__':
  main()


