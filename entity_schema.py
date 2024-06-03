from modules.entity_helper import NLP

ea = NLP()

def get_entities():
  
  url = input("Provide the URL you would like to analyze: ")

  entities = ea.get_entities(url)

  print(f"\u001b[34mEntities for {url}: \n\n")
  
  for entity, value in entities.items():
    print(f"\u001b[32m{entity}: \u001b[37m\n{value}\n")


  return entities

ent = get_entities()

def write_schema(entities):

  item_template = {
      "@type":"Thing",
      "name": str,
      "sameAs": str
    }

  final_schema = { 
    "about": []
    }


  for entity, values in entities.items():
    new_item = item_template.copy()
    new_item['name'] = entity
    new_item['sameAs'] = values['wikipedia_link']
    final_schema["about"].append(new_item)
  
  print("\u001b[32mComplete!\n")
  print(f"\u001b[35m{final_schema}")

write_schema(ent)