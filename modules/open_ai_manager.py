from openai import OpenAI, OpenAIError
import time

class GPT:
    def __init__(self, assistant_id='id'):
        self.client = OpenAI(
        max_retries = 3
        )
        self.model = 'gpt-3.5-turbo'
        self.thread=self.client.beta.threads.create()
        self.assistant_id = assistant_id
        self.instructions = 'You are a helpful assistant'

    def set_model (self, model):
        self.model = model

    def get_model(self):
        return self.model
    
    def set_instructions(self, instructions):
        self.instructions = instructions
    
    def set_assistant_id(self, assistant_id):
        self.assistant_id = assistant_id
        
    def create_new_thread(self):
        self.thread = self.client.beta.threads.create()

    def create_assistant(self, name="Test_Assistant",instructions="You are a helpful assistant"):
            print("Creating assistant")
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=self.get_model
            )

            self.set_assistant_id(assistant.id)

    def get_response_from_assistant(self, message_content: str):
        try:
            print("Sending message...")
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message_content,
                
            )        
        
            print("Getting response...")
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                instructions=self.instructions
            )

            while run.status != 'completed':
                print(f"Run Status: {run.status}")
                keep_running = self.client.beta.threads.runs.retrieve(
                        thread_id=self.thread.id,
                        run_id = run.id
                )
                time.sleep(5)
                if keep_running.status == "completed":
                    print(f"Run Status: {run.status}")
                    break

            messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
            
            assistant_messages = [message for message in messages.data if message.role == 'assistant']
            
            # Check if we have at least one assistant message
            if assistant_messages:
                # Assuming the last message is the latest response from the assistant
                latest_response = assistant_messages[0]
                
                # Assuming there's a single MessageContentText object in the 'content' list
                # and extracting the 'value' from the first one
                response_text = latest_response.content[0].text.value
                
                return response_text
            else:
                return None

        except OpenAIError as e:
            print(f"An error occurred: {str(e)}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return None

    
    def get_response(self, prompt):

        print("Getting response...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                            {"role": "system", "content": self.instructions},
                            {"role": "user", "content": prompt}
                        ]
                )
            print("Response:")
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        

        except Exception as e:
            print("Error: " + str(e))

    def get_response_with_image(self, prompt, image_url):

        print("Getting response...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": [
                    {
                        "type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                                        },
                                    },
                                ],
                            },
                        ]
                    )
            print("Response:")
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        

        except Exception as e:
            print("Error: " + str(e))
