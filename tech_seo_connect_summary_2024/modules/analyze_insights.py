from openai import OpenAI
import json
import time
from typing import List, Dict
import pandas as pd

class TalkInsightsAnalyzer:
    def __init__(self, json_path: str):
        self.client = OpenAI()
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def analyze_single_talk(self, talk: Dict) -> Dict:
        """Analyze a single talk for key takeaways."""
        
        prompt = f"""
        Analyze this SEO conference talk and provide:
        1. 3-5 key takeaways (actionable insights)
        2. Main theme/topic
        3. Future predictions or trends mentioned
        
        Title: {talk['metadata']['title']}
        Speaker: {talk['metadata']['speaker']}
        
        Transcript excerpt:
        {talk['content']['cleaned_text'][:4000]}  # First 4000 chars to stay within token limits
        
        Format the response as JSON with these keys:
        - takeaways (list)
        - main_theme (string)
        - future_trends (list)
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert SEO analyst helping extract insights from conference talks."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error analyzing talk '{talk['metadata']['title']}': {str(e)}")
            return None

    def analyze_all_talks(self) -> Dict:
        """Analyze all talks and compile insights."""
        all_insights = []
        
        for talk in self.data['talks']:
            insights = self.analyze_single_talk(talk)
            if insights:
                insights['title'] = talk['metadata']['title']
                insights['speaker'] = talk['metadata']['speaker']
                all_insights.append(insights)
            time.sleep(1)  # Rate limiting
            
        return all_insights

    def generate_overall_summary(self, all_insights: List[Dict]) -> Dict:
        """Generate overall conference themes and trends."""
        
        # Compile all insights into a condensed format
        summary_text = "\n".join([
            f"Talk: {insight['title']}\n"
            f"Theme: {insight['main_theme']}\n"
            f"Trends: {', '.join(insight['future_trends'])}\n"
            for insight in all_insights
        ])

        prompt = f"""
        Based on these insights from multiple SEO conference talks, provide:
        1. Top 5 overarching themes from the conference
        2. Top 5 predicted SEO trends for 2025
        3. Most significant changes/shifts in SEO discussed
        4. Common challenges mentioned
        
        Conference Insights:
        {summary_text}
        
        Format the response as JSON with these keys:
        - themes (list)
        - future_trends (list)
        - significant_changes (list)
        - common_challenges (list)
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert SEO analyst synthesizing conference insights."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating overall summary: {str(e)}")
            return None

    def save_insights(self, output_path: str = 'conference_insights.json'):
        """Analyze all talks and save insights to JSON."""
        
        # Analyze individual talks
        all_insights = self.analyze_all_talks()
        
        # Generate overall summary
        overall_summary = self.generate_overall_summary(all_insights)
        
        # Combine insights
        final_output = {
            'talk_insights': all_insights,
            'overall_summary': overall_summary
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2)
        
        return final_output

    def create_markdown_summary(self, insights: Dict, output_path: str = 'conference_summary.md'):
        """Create a formatted markdown summary of the insights."""
        
        markdown = f"""# SEO Conference Summary

## Overall Themes and Trends

### Key Conference Themes
{self._list_to_md(insights['overall_summary']['themes'])}

### Predicted SEO Trends for 2025
{self._list_to_md(insights['overall_summary']['future_trends'])}

### Significant Changes in SEO
{self._list_to_md(insights['overall_summary']['significant_changes'])}

### Common Challenges
{self._list_to_md(insights['overall_summary']['common_challenges'])}

## Individual Talk Summaries

"""
        # Add individual talk summaries
        for talk in insights['talk_insights']:
            markdown += f"""### {talk['title']}
*Speaker: {talk['speaker']}*

**Main Theme:** {talk['main_theme']}

**Key Takeaways:**
{self._list_to_md(talk['takeaways'])}

**Future Trends:**
{self._list_to_md(talk['future_trends'])}

---

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    def _list_to_md(self, items: List) -> str:
        """Convert a list to markdown bullet points."""
        return '\n'.join([f'- {item}' for item in items])

# Usage example
if __name__ == "__main__":
    analyzer = TalkInsightsAnalyzer('tech-seo-connect-summary/all_talks.json')
    insights = analyzer.save_insights()
    analyzer.create_markdown_summary(insights)
