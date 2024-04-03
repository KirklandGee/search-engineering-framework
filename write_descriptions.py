from modules.google_drive_manager import GoogleSheetsManager
from modules.open_ai_manager import GPT

# Test sheet: https://docs.google.com/spreadsheets/d/1HSDEh4eSRrPDlWaqzn98wIBJxySiDUjUFVqO1o9vUMo/edit#gid=0

gs = GoogleSheetsManager('AI for Google Sheets')
gpt = GPT()

def main():

  # In this system prompt, you want to give the AI a list of categories it can choose from. Here's an example below:
  # You will want to change this. 
  system_prompt = """ 
      You are an employee at Nike helping to write product descriptions for various shoes on offer.
      Given a name and a few other pieces of info about the product, you will write a 1-2 sentence descrpition describing the product.

      Please follow the following brand guidelines:
      - Nike tone of voice: bold, ambitious, aspirational_
      - We believe if you have a body, you are an athlete
      - We dare to design the future of sport

      Example inputs/outputs:  

      Input: Jordan 1 Mid, Leather, synthetic leather and textile upper for a supportive feel. Foam midsole and Nike Air cushioning provide lightweight comfort. Rubber outsole with pivot circle gives you durable traction. Shown: White/Black/Green Glow Style: DQ8426-103

      Output: Inspired by the original AJ1, this mid-top edition maintains the iconic look you love while choice colors and crisp leather give it a distinct identity.

      Input: Air Max 90:Originally designed for performance running, the Max Air unit in the heel adds unbelievable cushioning. Padded, low-top collar looks sleek and feels great Rubber Waffle outsole adds a heritage look, traction and durability. Stitched overlays and TPU accents on the heel and eyestays add durability, comfort and the iconic '90s look you love. Shown: White/White/White Style: DH8010-100

      Output: Nothing as fly, nothing as comfortable, nothing as proven. The Nike Air Max 90 stays true to its OG running roots with the iconic Waffle sole, stitched overlays and classic TPU details. Classic colors celebrate your fresh look while Max Air cushioning adds comfort to the journey.

      Input: Nike Dunk Low: Premium leather in the upper has the perfect sheen and breaks in beautifully. The modern foam midsole offers lightweight, responsive cushioning. A padded, low-cut collar adds a sleek look that feels comfortable. Bold color blocking throws it back to the original colorway inspiration: school team colors. The rubber outsole with classic hoops pivot circle adds durability, traction and heritage style.

      Output: Created for the hardwood but taken to the streets, the Nike Dunk Low Retro returns with crisp overlays and original team colors. This basketball icon channels '80s vibes with premium leather in the upper that looks good and breaks in even better. Modern footwear technology helps bring the comfort into the 21st century.  
    """

  # Setup our AI assistant with our system prompt and the model we want
  gpt.set_instructions(system_prompt)
  
  # I'd recommend using GPT-4 for this use case, but that depends on your specific needs.
  gpt.set_model('gpt-3.5-turbo')

  # This will use our module to create a dataframe and set it to this variablee.
  info_df = gs.create_dataframe(worksheet_name='writer')
  info_df["Category"] = None

  # This counter will be used to periodically write the DF back to our sheet
  i=0
  
  for index, row in info_df.iterrows():

    # You can give the AI as much information in your sheet as you want, but you may need to adjust the code if so. 
    # This is designed to work with one name column and one description column in your sheet. 
    # If you want to categorize with more info, adjust your category prompt to include it here and add it into your system prompt examples. 
    try:
      description = gpt.get_response(f"{row['Name']}\n\n Respond with only the description and no other text.")
      info_df.at[index, "Description"] = description
      print(f"\u001b[32mSuccess!  \u001b[37m{row['Name']} description written!")
    except Exception:
      print(f"\u001b[31mFailed to write description for \u001b[37m{row['Name']}...")
      info_df.at[index, "Description"] = "Failed to write..."
      
    # Writes to our sheet every 10 iterations in case we run into an issue.
    i +=1
    if i == 10:
      gs.write_dataframe_to_sheets(dataframe=info_df,worksheet_name='writer',)

  gs.write_dataframe_to_sheets(dataframe=info_df,worksheet_name='writer',)

if __name__ == '__main__':
  main()


