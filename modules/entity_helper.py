import textrazor
import os

class NLP:
    
    def __init__(self):
        
        # Add this as an environment variable or replace with your API key
        self.api_key = os.getenv('TEXTRAZOR_API_KEY')
        self.extractors = ["entities", "topics"]
        self.cleanup_mode = "cleanHTML"
        self.client = textrazor.TextRazor(api_key=self.api_key, extractors=self.extractors)

    def reset_client(self):
        self.client = textrazor.TextRazor(extractors=self.extractors,cleanup_mode=self.cleanup_mode) 

    def read_url(self, url):

        try:
            print(f"\u001b[33mAnalyzing URL: {url}\n")
            response = self.client.analyze_url(url)
        except Exception as e:
            print("Error reading URL: " + url)
            print(e)

        return response
    
    def read_text(self, text):
        try:
            print("Analyzing input text")
            response = self.client.analyze(text)
        except Exception as e:
            print("Error reading text: " + text)
            print(e)
        return response

    def get_entities(self, url):

        response = self.read_url(url)
        
        print('\u001b[33mAnalyzing entities: \n')
        self.client.set_cleanup_mode("cleanHTML")

        entities = list(response.entities())
        entities.sort(key=lambda x: x.relevance_score, reverse=True)

        seen = set()
        
        entity_dict = {}

        for entity in entities:
            if entity.id not in seen and entity.relevance_score > 0.7:
                entity_dict[entity.id] = {
                    "relevance_score": entity.relevance_score, 
                     "wikipedia_link": entity.wikipedia_link, 
                     "wikidata_id": entity.wikidata_id, 
                     "freebase_id": entity.freebase_id
                    }
                seen.add(entity.id)

        return entity_dict

    def get_topics(self, response):
        print('Analyzing topics: ')
        
        self.client.set_cleanup_mode("cleanHTML")

        topics = list(response.topics())
        topics.sort(key=lambda x: x.score, reverse=True)

        seen = set()
        
        topic_dict = {}

        for topic in topics:
            if topic.label not in seen:
                topic_dict[topic.label] = [topic.score, topic.wikipedia_link]
                seen.add(topic.id)

        return topic_dict
