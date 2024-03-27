from modules.google_drive_manager import GoogleSheetsManager
from modules.open_ai_manager import GPT


gs = GoogleSheetsManager('AI for Google Sheets')
gpt = GPT()


# Test
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

  gpt.set_instructions(system_prompt)

  # You can give the AI as much information in your sheet as you want, but you may need to adjust the code if so. 
  # This is designed to work with one name column and one description column in your sheet.

  categories_df = gs.create_dataframe_from_google_sheet('categorizer')  
  

  for keyword in keywords_dataframe['Keyword']:
    entities_list = get_entities_from_keyword(keyword)
    content = write_content(keyword, entities_list)
    print(content)
    output_dictionary['Keyword'].append(keyword)
    output_dictionary['Content'].append(content)
    print(output_dictionary)

  final_df = pd.DataFrame(output_dictionary, columns=['Keyword', 'Content'])
  print(final_df['Content'])

  gdrive.write_dataframe_to_sheets('Output', final_df)

if __name__ == '__main__':
  main()