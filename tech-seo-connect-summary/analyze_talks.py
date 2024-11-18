from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import json
import numpy as np

class TalkAnalyzer:
    def __init__(self, talks_json_path):
        # Load JSON data
        with open(talks_json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.talks = self.data['talks']
        
        # Define custom stop words for transcribed speech
        transcript_stop_words = [
            'um', 'uh', 'like', 'yeah', 'actually', 'basically', 'literally',
            'you know', 'i mean', 'sort of', 'kind of', 'okay', 'right',
            'so', 'just', 'theres', 'youre', 'gonna', 'wanna', 'stuff',
            'super', 'really', 'very', 'quite', 'bit', 'things'
        ]
        
        # Combine with English stop words
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        all_stop_words = list(ENGLISH_STOP_WORDS.union(transcript_stop_words))
        
        # Initialize models
        self.vectorizer = CountVectorizer(
            max_df=0.95,
            min_df=2,
            stop_words=all_stop_words,
            token_pattern=r'\b\w+\b',
        )
        
        self.lda_model = LatentDirichletAllocation(
            n_components=5,
            random_state=42,
            learning_method='batch'
        )

        self.bigram_vectorizer = CountVectorizer(
            ngram_range=(2, 2),
            max_df=0.95,
            min_df=2,
            stop_words=all_stop_words,
            token_pattern=r'\b\w+\b'
        )
        
        self.trigram_vectorizer = CountVectorizer(
            ngram_range=(3, 3),
            max_df=0.95,
            min_df=2,
            stop_words=all_stop_words,
            token_pattern=r'\b\w+\b'
        )

        
    def extract_topics(self, n_words=10):
        """Extract topics from all talks."""
        # Get cleaned texts from all talks
        documents = [talk['content']['cleaned_text'] for talk in self.talks]
        
        # Create document-term matrix
        dtm = self.vectorizer.fit_transform(documents)
        
        # Fit LDA model
        self.lda_model.fit(dtm)
        
        # Get feature names (words)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract top words for each topic
        topics = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words_idx = topic.argsort()[:-n_words-1:-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topics.append({
                'topic_id': topic_idx,
                'words': top_words,
                'weights': topic[top_words_idx].tolist()
            })
            
        return topics
    
    def analyze_ngrams(self, min_count=3):
        """Analyze frequent bigrams and trigrams across all talks."""
        documents = [talk['content']['cleaned_text'] for talk in self.talks]
        
        # Analyze bigrams
        bigram_matrix = self.bigram_vectorizer.fit_transform(documents)
        bigram_features = self.bigram_vectorizer.get_feature_names_out()
        bigram_sums = bigram_matrix.sum(axis=0).A1
        
        # Analyze trigrams
        trigram_matrix = self.trigram_vectorizer.fit_transform(documents)
        trigram_features = self.trigram_vectorizer.get_feature_names_out()
        trigram_sums = trigram_matrix.sum(axis=0).A1
        
        # Create sorted lists of n-grams with their frequencies
        bigrams = [
            {'phrase': phrase, 'count': int(count)}
            for phrase, count in zip(bigram_features, bigram_sums)
            if count >= min_count
        ]
        
        trigrams = [
            {'phrase': phrase, 'count': int(count)}
            for phrase, count in zip(trigram_features, trigram_sums)
            if count >= min_count
        ]
        
        # Sort by frequency
        bigrams.sort(key=lambda x: x['count'], reverse=True)
        trigrams.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'bigrams': bigrams[:50],  # Top 50 bigrams
            'trigrams': trigrams[:30]  # Top 30 trigrams
        }

    def analyze_talk_ngrams(self, talk_index):
        """Analyze n-grams for a specific talk."""
        text = [self.talks[talk_index]['content']['cleaned_text']]
        
        # Get n-grams for this specific talk
        bigram_matrix = self.bigram_vectorizer.transform(text)
        trigram_matrix = self.trigram_vectorizer.transform(text)
        
        # Get feature names
        bigram_features = self.bigram_vectorizer.get_feature_names_out()
        trigram_features = self.trigram_vectorizer.get_feature_names_out()
        
        # Get non-zero elements
        bigram_counts = bigram_matrix.toarray()[0]
        trigram_counts = trigram_matrix.toarray()[0]
        
        # Create sorted lists of n-grams with their frequencies
        talk_bigrams = [
            {'phrase': phrase, 'count': int(count)}
            for phrase, count in zip(bigram_features, bigram_counts)
            if count > 0
        ]
        
        talk_trigrams = [
            {'phrase': phrase, 'count': int(count)}
            for phrase, count in zip(trigram_features, trigram_counts)
            if count > 0
        ]
        
        # Sort by frequency
        talk_bigrams.sort(key=lambda x: x['count'], reverse=True)
        talk_trigrams.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'talk_title': self.talks[talk_index]['metadata']['title'],
            'bigrams': talk_bigrams[:20],  # Top 20 bigrams
            'trigrams': talk_trigrams[:15]  # Top 15 trigrams
        }
    
    def analyze_talk_topics(self, talk_index):
        """Analyze topics for a specific talk."""
        text = self.talks[talk_index]['content']['cleaned_text']
        
        # Transform single document
        dtm = self.vectorizer.transform([text])
        
        # Get topic distribution
        topic_distribution = self.lda_model.transform(dtm)[0]
        
        # Get dominant topic
        dominant_topic = np.argmax(topic_distribution)
        
        return {
            'talk_title': self.talks[talk_index]['metadata']['title'],
            'topic_distribution': topic_distribution.tolist(),
            'dominant_topic': int(dominant_topic),
            'dominant_topic_score': float(topic_distribution[dominant_topic])
        }
    
    def analyze_all_talks(self):
        """Run topic analysis on all talks."""
        # Extract overall topics
        topics = self.extract_topics()
        
        # Analyze each talk
        talk_analyses = []
        for i in range(len(self.talks)):
            analysis = self.analyze_talk_topics(i)
            talk_analyses.append(analysis)
        
        return {
            'overall_topics': topics,
            'talk_analyses': talk_analyses
        }
    
    def analyze_all_talks_ngrams(self):
        """Run all analyses on talks."""
        results = self.analyze_all_talks()  # Get existing topic analysis
        
        # Add n-gram analysis
        results['ngram_analysis'] = {
            'overall': self.analyze_ngrams(),
            'per_talk': [
                self.analyze_talk_ngrams(i) 
                for i in range(len(self.talks))
            ]
        }
        
        return results
    
    
if __name__ == "__main__":
    # Example usage
    analyzer = TalkAnalyzer('tech-seo-connect-summary/all_talks.json')
    results = analyzer.analyze_all_talks_ngrams()

    # Print overall topics
    for topic in results['overall_topics']:
        print(f"\nTopic {topic['topic_id']}:")
        for word, weight in zip(topic['words'], topic['weights']):
            print(f"  - {word}: {weight:.4f}")

    # Print individual talk analyses
    for analysis in results['talk_analyses']:
        print(f"\nTalk: {analysis['talk_title']}")
        print(f"Dominant Topic: {analysis['dominant_topic']}")
        print(f"Topic Score: {analysis['dominant_topic_score']:.4f}")
        # Print overall n-gram analysis
    print("\nTop Bigrams across all talks:")
    for bigram in results['ngram_analysis']['overall']['bigrams'][:10]:
        print(f"  - {bigram['phrase']}: {bigram['count']}")

    print("\nTop Trigrams across all talks:")
    for trigram in results['ngram_analysis']['overall']['trigrams'][:10]:
        print(f"  - {trigram['phrase']}: {trigram['count']}")

    # Print per-talk analysis
    for talk_analysis in results['ngram_analysis']['per_talk']:  # First 2 talks
        print(f"\nTalk: {talk_analysis['talk_title']}")
        print("Top Bigrams:")
        for bigram in talk_analysis['bigrams'][:5]:
            print(f"  - {bigram['phrase']}: {bigram['count']}")