import os
import json
import re
from datetime import datetime
from pathlib import Path

class TranscriptPreprocessor:
    def __init__(self, input_directory):
        self.input_directory = Path(input_directory)
        self.talks = []
        
    def extract_metadata(self, text):
        """Extract metadata from the transcript header."""
        lines = text.split('\n')[:4]  # First 4 lines typically contain metadata
        metadata = {
            "title": "",
            "speaker": "",
            "platform": "",
            "url": "",
            "duration": ""
        }
        
        for line in lines:
            if line.startswith('# '):
                line = line[2:]  # Remove '# ' prefix
                if 'youtube transcript' in line.lower():
                    metadata["platform"] = "YouTube"
                    continue
                elif 'http' in line:
                    metadata["url"] = line.strip()
                elif '-' in line:
                    # Assuming format: "Title - Speaker"
                    parts = [p.strip() for p in line.split('-')]
                    if len(parts) >= 2:
                        metadata["title"] = parts[0]
                        metadata["speaker"] = parts[1]
                    else:
                        metadata["title"] = parts[0]
        
        return metadata

    def parse_segments(self, text):
        """Parse timestamp and text segments."""
        segments = []
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*(.*?)(?=\d{2}:\d{2}:\d{2}\.\d{3}|\Z)'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            timestamp, content = match.groups()
            segments.append({
                "timestamp": timestamp,
                "text": content.strip()
            })
            
        return segments

    def clean_text(self, text):
        """Clean the transcript text."""
        # Remove timestamps
        text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', text)
        
        # Basic cleaning
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        
        return text.strip()

    def process_file(self, file_path):
        """Process a single transcript file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        metadata = self.extract_metadata(content)
        segments = self.parse_segments(content)
        
        # Get raw text without timestamps
        raw_text = ' '.join(segment["text"] for segment in segments)
        
        # Calculate basic stats
        stats = {
            "word_count": len(raw_text.split()),
            "duration_seconds": len(segments)  # Approximate, assuming 1 segment per second
        }
        
        return {
            "metadata": metadata,
            "content": {
                "raw_text": raw_text,
                "cleaned_text": self.clean_text(raw_text),
                "segments": segments
            },
            "stats": stats
        }

    def process_all_files(self):
        """Process all transcript files in the directory."""
        for file_path in self.input_directory.glob('*.txt'):
            try:
                processed_talk = self.process_file(file_path)
                self.talks.append(processed_talk)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    def calculate_total_duration(json_data):
        total_seconds = 0
        
        # Loop through each talk
        for talk in json_data['talks']:
            # Get segments for the talk
            segments = talk['content'].get('segments', [])
            
            if segments:
                # Get the timestamp of the last segment
                last_timestamp = segments[-1]['timestamp']
                
                # Convert timestamp (HH:MM:SS.mmm) to seconds
                try:
                    parts = last_timestamp.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    
                    total_seconds += (hours * 3600) + (minutes * 60) + seconds
                except (IndexError, ValueError):
                    print(f"Warning: Could not parse timestamp {last_timestamp}")
                    continue
        
        # Convert total seconds to hours, minutes, seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        return {
            'total_seconds': total_seconds,
            'formatted_time': f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }
    
        
    def save_json(self, output_file):
        """Save processed talks to JSON file."""
        output = {
            "talks": self.talks,
            "metadata": {
                "conference_name": "Tech SEO Conference",
                "total_talks": len(self.talks),
                "processing_date": datetime.now().isoformat()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

# Usage example
if __name__ == "__main__":
    with open('tech-seo-connect-summary/all_talks.json', 'r') as f:
        data = json.load(f)
        
    duration = TranscriptPreprocessor.calculate_total_duration(data)
    print(f"Total conference duration: {duration['formatted_time']}")
    print(f"Total hours: {duration['hours']}")
    print(f"Total minutes: {duration['minutes']}")
    print(f"Total seconds: {duration['seconds']}")