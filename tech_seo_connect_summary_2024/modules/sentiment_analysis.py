from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.tokenize import sent_tokenize
import numpy as np
import json
import os

class ConferenceSentimentAnalyzer:
    def __init__(self, json_data):
        self.data = json_data
        
    def analyze_talk_sentiment(self, text):
        """Analyze sentiment for a single talk"""
        # Break into sentences for more granular analysis
        sentences = sent_tokenize(text)
        
        sentiments = []
        for sentence in sentences:
            blob = TextBlob(sentence)
            sentiments.append({
                'polarity': blob.sentiment.polarity,  # -1 to 1
                'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
                'text': sentence
            })
            
        return sentiments
    
    def analyze_all_talks(self):
        """Analyze sentiment across all talks"""
        results = []
        
        for talk in self.data['talks']:
            text = talk['content']['cleaned_text']
            sentiments = self.analyze_talk_sentiment(text)
            
            # Calculate aggregate metrics
            avg_polarity = np.mean([s['polarity'] for s in sentiments])
            avg_subjectivity = np.mean([s['subjectivity'] for s in sentiments])
            
            # Find most positive and negative sentences
            sorted_sentiments = sorted(sentiments, key=lambda x: x['polarity'])
            most_negative = sorted_sentiments[0]
            most_positive = sorted_sentiments[-1]
            
            results.append({
                'title': talk['metadata']['title'],
                'speaker': talk['metadata']['speaker'],
                'avg_polarity': avg_polarity,
                'avg_subjectivity': avg_subjectivity,
                'most_negative_sentence': most_negative,
                'most_positive_sentence': most_positive,
                'sentiment_distribution': sentiments
            })
            
        return results
    
    def visualize_results(self, results):
        """Create visualizations of sentiment analysis"""
        df = pd.DataFrame([{
            'Title': r['title'],
            'Speaker': r['speaker'],
            'Polarity': r['avg_polarity'],
            'Subjectivity': r['avg_subjectivity']
        } for r in results])
        
        plt.style.use('default')
        sns.set_theme()
        
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Overall sentiment distribution
        ax1 = plt.subplot(2, 2, 1)
        sns.histplot(data=df, x='Polarity', bins=20)
        plt.title('Distribution of Talk Sentiments')
        plt.xlabel('Sentiment Polarity (-1 = Negative, 1 = Positive)')
        
        # 2. Sentiment vs Subjectivity scatter
        ax2 = plt.subplot(2, 2, 2)
        sns.scatterplot(data=df, x='Polarity', y='Subjectivity')
        plt.title('Sentiment vs Subjectivity')
        
        # 3. Top 10 Most Positive/Negative Talks
        ax3 = plt.subplot(2, 1, 2)
        top_sentiments = pd.concat([
            df.nsmallest(5, 'Polarity'),
            df.nlargest(5, 'Polarity')
        ])
        sns.barplot(
            data=top_sentiments, 
            y='Title', 
            x='Polarity',
            hue='Title',  # Add hue parameter
            legend=False  # Hide legend
        )
        plt.title('Most Positive and Negative Talks')
        
        plt.tight_layout()
        plt.savefig('sentiment_analysis.png')
        plt.close()
        
    def print_insights(self, results):
        """Print key insights from the sentiment analysis"""
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'Title': r['title'],
            'Speaker': r['speaker'],
            'Polarity': r['avg_polarity'],
            'Subjectivity': r['avg_subjectivity']
        } for r in results])
        
        print("\n=== Sentiment Analysis Insights ===\n")
        
        print("Overall Conference Mood:")
        print(f"Average Sentiment: {df['Polarity'].mean():.3f}")
        print(f"Sentiment Standard Deviation: {df['Polarity'].std():.3f}")
        
        print("\nMost Positive Talks:")
        for _, row in df.nlargest(3, 'Polarity').iterrows():
            print(f"- {row['Title']} (by {row['Speaker']}): {row['Polarity']:.3f}")
        
        print("\nMost Negative Talks:")
        for _, row in df.nsmallest(3, 'Polarity').iterrows():
            print(f"- {row['Title']} (by {row['Speaker']}): {row['Polarity']:.3f}")
        
        print("\nMost Objective Talks:")
        for _, row in df.nsmallest(3, 'Subjectivity').iterrows():
            print(f"- {row['Title']} (by {row['Speaker']}): {row['Subjectivity']:.3f}")
        
        print("\nMost Subjective Talks:")
        for _, row in df.nlargest(3, 'Subjectivity').iterrows():
            print(f"- {row['Title']} (by {row['Speaker']}): {row['Subjectivity']:.3f}")

    def create_table_image(self, df, title, output_filename):
        """Create an image of a formatted table"""
        # Set style for tables
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, len(df) * 0.5 + 1))
        
        # Hide axes
        ax.axis('tight')
        ax.axis('off')
        
        # Format the data for display
        display_data = df.copy()
        if 'Polarity' in df.columns:
            display_data['Score'] = display_data['Polarity'].map('{:.3f}'.format)
        elif 'Subjectivity' in df.columns:
            display_data['Score'] = display_data['Subjectivity'].map('{:.3f}'.format)
        
        # Prepare table data
        table_data = display_data[['Title', 'Speaker', 'Score']].values
        
        # Create table
        table = ax.table(
            cellText=table_data,
            colLabels=['Title', 'Speaker', 'Score'],
            cellLoc='left',
            loc='center',
            colWidths=[0.5, 0.25, 0.25]
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Add title
        plt.title(title, pad=20)
        
        # Save figure
        plt.savefig(f'tables/{output_filename}.png', 
                    bbox_inches='tight', 
                    dpi=300,
                    facecolor='white',
                    edgecolor='none')
        plt.close()

    def save_to_markdown(self, results, output_path='sentiment_analysis.md'):
        """Save sentiment analysis results to a markdown file"""
        # Create tables directory if it doesn't exist
        os.makedirs('tables', exist_ok=True)
        
        # Create DataFrame for analysis
        df = pd.DataFrame([{
            'Title': r['title'],
            'Speaker': r['speaker'],
            'Polarity': r['avg_polarity'],
            'Subjectivity': r['avg_subjectivity']
        } for r in results])
        
        # Create table images
        # Most Positive Talks
        positive_df = df.nlargest(5, 'Polarity')
        self.create_table_image(
            positive_df, 
            'Most Positive Talks',
            'positive_talks'
        )
        
        # Most Negative Talks
        negative_df = df.nsmallest(5, 'Polarity')
        self.create_table_image(
            negative_df, 
            'Most Negative Talks',
            'negative_talks'
        )
        
        # Most Objective Talks
        objective_df = df.nsmallest(5, 'Subjectivity')
        self.create_table_image(
            objective_df, 
            'Most Objective Talks',
            'objective_talks'
        )
        
        # Most Subjective Talks
        subjective_df = df.nlargest(5, 'Subjectivity')
        self.create_table_image(
            subjective_df, 
            'Most Subjective Talks',
            'subjective_talks'
        )
        
        with open(output_path, 'w') as f:
            # Write header
            f.write('# Conference Talk Sentiment Analysis\n\n')
            
            # Overall stats
            f.write('## Overall Conference Sentiment\n\n')
            f.write(f"• Average Sentiment: {df['Polarity'].mean():.3f}\n")
            f.write(f"• Sentiment Standard Deviation: {df['Polarity'].std():.3f}\n")
            f.write(f"• Average Subjectivity: {df['Subjectivity'].mean():.3f}\n\n")
            
            # Add table images
            f.write('## Most Positive Talks\n\n')
            f.write('![Most Positive Talks](tables/positive_talks.png)\n\n')
            
            f.write('## Most Negative Talks\n\n')
            f.write('![Most Negative Talks](tables/negative_talks.png)\n\n')
            
            f.write('## Objectivity Analysis\n\n')
            f.write('### Most Objective Talks\n\n')
            f.write('![Most Objective Talks](tables/objective_talks.png)\n\n')
            
            f.write('### Most Subjective Talks\n\n')
            f.write('![Most Subjective Talks](tables/subjective_talks.png)\n\n')
            
            # Add the sentiment analysis visualization
            f.write('## Overall Sentiment Analysis\n\n')
            f.write('![Sentiment Analysis Visualizations](sentiment_analysis.png)\n')

if __name__ == "__main__":
    with open('tech-seo-connect-summary/all_talks.json', 'r') as f:
        data = json.load(f)
        
    analyzer = ConferenceSentimentAnalyzer(data)
    results = analyzer.analyze_all_talks()
    analyzer.visualize_results(results)
    analyzer.save_to_markdown(results)