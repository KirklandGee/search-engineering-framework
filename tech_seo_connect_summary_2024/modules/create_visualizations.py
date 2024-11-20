from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
from collections import Counter
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.util import ngrams
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import community  # python-louvain package



nltk.download('punkt_tab')

class ConferenceVisualizer:
    def __init__(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
            
        # Expanded and more specific categories
        self.color_categories = {
            # AI and ML related terms
            'ai': ['ai', 'model', 'language', 'machine', 'learning', 'gpt', 'bert', 'neural', 
                   'recommendation', 'algorithm', 'automation', 'chatgpt', 'intelligence'
                   'context windows', 'models'],
            
            # Search related terms
            'search': ['search', 'query', 'google', 'result', 'engine', 'serp', 'ranking', 
                      'crawl', 'index', 'keyword', 'intent', 'relevance', 'bing'],
            
            # Content related terms
            'content': ['content', 'page', 'site', 'video', 'image', 'blog', 'article', 
                       'text', 'media', 'document', 'copy', 'write', 'title', 'description'],
            
            # Technical SEO terms
            'technical': ['code', 'javascript', 'api', 'lcp', 'tools', 'url', 'html', 'css', 
                         'schema', 'markup', 'performance', 'speed', 'core', 'vitals', 'mobile',
                         'responsive', 'canonical', 'redirect', 'server', 'cloud', 'core web','performance'],
            
            # Analytics and data terms
            'data': ['data', 'analysis', 'analytics', 'metric', 'measure', 'track', 'report',
                    'insight', 'conversion', 'traffic', 'engagement', 'performance', 'roi'
                    'bulk export', ],
            
            # E-commerce terms
            'tools': ['rank tracker', 'ahrefs', 'semrush', 'moz', 'seo', 'seo tools',
                      'google analytics', 'google search console', 'google tag manager', 'google ads', 'google my business',
                        'open source', 'space serp']
        }
        
        # Updated color scheme with more vibrant, distinct colors
        self.colors = {
            'ai': '#FF4B4B',          # Bright red
            'search': '#4A90E2',      # Bright blue
            'content': '#50E3C2',     # Turquoise
            'technical': '#F7B731',   # Golden yellow
            'data': '#A569BD',        # Purple
            'tools': '#26C281'    # Green
        }

        self.custom_stop_words = {
            # Common English words
            'the', 'to', 'and', 'you', 'that', 'a', 'of', 'is', 'i', 'so',
            'it', 'this', 'like', 'we', 'in', 'for', 'its', 'can', 'have',
            'are', 'with', 'but', 'do', 'if', 'on', 'not', 'your', 'what',
            'be', 'as', 'at', 'they', 'there', 'from', 'or', 'an', 'will',
            'my', 'one', 'all', 'would', 'their', 'was', 'were', 'them',
            
            # Presentation filler words
            'um', 'uh', 'like', 'yeah', 'actually', 'basically', 'literally',
            'going', 'think', 'know', 'mean', 'really', 'way', 'thing',
            'things', 'lot', 'kind', 'want', 'need', 'look', 'see', 'right',
            'going', 'get', 'got', 'well', 'just', 'thats', 'im', 'dont',
            'okay', 'sure', 'maybe', 'probably', 'obviously', 'essentially',
            
            # Common verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'can', 'could', 'shall', 'should', 'may', 'might', 'must',
            'go', 'goes', 'going', 'went', 'gone',
            
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'mine', 'yours', 'his', 'hers', 'ours', 'theirs',
            
            # Other common words in presentations
            'thank', 'thanks', 'please', 'yes', 'no', 'ok', 'lets',
            'wanna', 'gonna', 'gotta', 'kinda', 'sorta',
            
            # Common transitional/temporal words
            'then', 'when', 'now', 'here', 'there', 'where', 'why',
            'how', 'what', 'which', 'because', 'also', 'too', 'very',
            'some', 'any', 'even', 'still', 'back', 'over', 'again',
            'already', 'always', 'never', 'ever', 'first', 'second',
            'next', 'last', 'much', 'many', 'most', 'other', 'another',
            'same', 'different', 'such', 'only', 'every', 'each',
            
            # Common action words
            'make', 'making', 'made', 'take', 'taking', 'taken',
            'give', 'giving', 'given', 'work', 'working', 'worked',
            'use', 'using', 'used', 'try', 'trying', 'tried',
            'start', 'starting', 'started', 'end', 'ending', 'ended',
            'help', 'helping', 'helped', 'change', 'changing', 'changed',
            
            # Common descriptive words
            'good', 'great', 'big', 'small', 'little', 'more', 'less',
            'better', 'best', 'worse', 'worst', 'new', 'old', 'different',
            'up','by'
            
            # Technical common words
            'using', 'example', 'through', 'into', 'out', 'about',
            'getting', 'doing', 'build', 'building', 'built',
            'project', 'tool', 'console', 'api', 'number',
            
            # Additional context-specific words
            'stuff', 'thing', 'something', 'everything', 'anything',
            'click', 'clicking', 'clicked', 'user', 'users',
            'information', 'day', 'year', 'time', 'website','ask','few','doesnt','today','said','whatever','theres',
            'thing','things','lot','kind','want','need','look','see','right','going','get','got','well','just','thats','im','dont','okay','sure','maybe','probably','obviously','essentially',
            'come','make','way','look','good','thing','things','lot','kind','want','need','look','see','right','going','get','got','well','just','thats','im','dont','okay','sure','maybe','probably','obviously','essentially',
            'talk','say','those','who','oh','able','than','having','talking','youre','these','before','ive','part','hey','tell'
        }


    def get_color_func(self, word, **kwargs):
        """Return color based on word category."""
        word = word.lower()
        
        # Check which category the word belongs to
        for category, terms in self.color_categories.items():
            if any(term in word for term in terms):
                return self.colors[category]
                
        return '#666666'  # Default gray for uncategorized terms

    def get_word_frequencies(self, text):
        """Get word frequencies after cleaning."""
        words = text.split()
        return Counter(words)

    def create_wordcloud(self, output_path='wordcloud.png', style='modern'):
        # Combine all cleaned text
        all_text = ' '.join(talk['content']['cleaned_text'] 
                           for talk in self.data['talks'])
       
        
        # Get word frequencies
        word_freq = self.get_word_frequencies(all_text)
        
        # Create figure with custom grid
        fig = plt.figure(figsize=(20, 10))
        
        # Create grid with custom ratio (80% wordcloud, 20% table)
        gs = fig.add_gridspec(1, 2, width_ratios=[4, 1])
        
        # Word cloud subplot (larger)
        cloud_ax = fig.add_subplot(gs[0])
        wordcloud = WordCloud(
            width=2000,
            height=1200,
            background_color='white',
            max_words=75,
            stopwords=self.custom_stop_words,
            color_func=self.get_color_func,
            collocations=True,
            min_font_size=12,
            max_font_size=160,
            random_state=42,
            prefer_horizontal=0.9,
            relative_scaling=0.7,
            margin=3
        )
        
        # Generate word cloud
        wordcloud.generate(all_text)
        cloud_ax.imshow(wordcloud, interpolation='bilinear')
        cloud_ax.axis('off')
        
        # Table subplot (smaller)
        table_ax = fig.add_subplot(gs[1])
        table_ax.axis('off')
        
        # Get top 10 words and their frequencies
        word_freq = Counter(all_text.split())
        top_words = sorted(
            [(word, count) for word, count in word_freq.items() 
             if word not in self.custom_stop_words],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Create table data
        table_data = [['Term', 'Count']]
        table_data.extend(top_words)
        
        # Create and style the table
        table = table_ax.table(
            cellText=[[str(item) for item in row] for row in table_data],
            colWidths=[0.6, 0.4],
            cellLoc='left',
            loc='center',
            bbox=[0.1, 0.5, 0.9, 0.4]  # Adjust table position and size
        )
        
        # Modern table styling
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1.4, 2.0)
        
        # Style cells
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                # Header styling
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#2C3E50')  # Dark blue header
                cell.set_edgecolor('white')
            else:
                # Alternate row colors
                if row % 2:
                    cell.set_facecolor('#F8F9F9')  # Light gray
                else:
                    cell.set_facecolor('white')
                cell.set_edgecolor('#E5E8E8')  # Light border
            
            # Add padding
            cell.PAD = 0.3
        
        # Add title above table
        table_ax.text(
            0.5, 0.95, 
            'Top 10 Terms',
            horizontalalignment='center',
            fontsize=16,
            fontweight='bold'
        )
        
        plt.tight_layout()
        
        # Save with high quality
        plt.savefig(
            output_path, 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none',
            pad_inches=0.3
        )
        plt.close()

    def extract_bigrams(self, text):
        """Extract and count meaningful bigrams from text."""
        # Tokenize the text
        tokens = nltk.word_tokenize(text.lower())
        
        # Skip bigrams containing stop words or short words
        bigrams = [
            ' '.join(bigram) for bigram in nltk.bigrams(tokens)
            if all(word not in self.custom_stop_words and len(word) > 2 
                  for word in bigram)
        ]
        
        return Counter(bigrams)

    def create_bigram_cloud(self, output_path='bigram_cloud.png'):
        # Get the text data
        all_text = ' '.join(talk['content']['cleaned_text'] 
                            for talk in self.data['talks'])
        
        # Get bigram frequencies
        bigram_freq = self.extract_bigrams(all_text)
        
        # Create figure with custom grid
        fig = plt.figure(figsize=(20, 10))
        gs = fig.add_gridspec(1, 2, width_ratios=[4, 1])
        
        # Word cloud subplot
        cloud_ax = fig.add_subplot(gs[0])
        wordcloud = WordCloud(
            width=1800,
            height=1200,
            background_color='white',
            max_words=40,  # Fewer words for bigrams
            collocations=False,  # Important when using custom frequencies
            min_font_size=12,
            color_func=self.get_color_func_bigrams,
            max_font_size=160,
            random_state=42,
            prefer_horizontal=0.9,
            relative_scaling=0.7,
            margin=3
        )
        
        # Generate from bigram frequencies
        wordcloud.generate_from_frequencies(bigram_freq)
        cloud_ax.imshow(wordcloud, interpolation='bilinear')
        cloud_ax.axis('off')
        
        # Table subplot
        table_ax = fig.add_subplot(gs[1])
        table_ax.axis('off')
        
        # Get top 10 bigrams
        top_bigrams = sorted(
            bigram_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Create table data
        table_data = [['Phrase', 'Count']]
        table_data.extend(top_bigrams)
        
        # Create and style the table
        table = table_ax.table(
            cellText=[[str(item) for item in row] for row in table_data],
            colWidths=[0.7, 0.3],
            cellLoc='left',
            loc='center',
            bbox=[0.1, 0.5, 0.9, 0.4]
        )
        
        # Modern table styling
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1.4, 2.0)
        
        # Style cells
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                # Header styling
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#2C3E50')
                cell.set_edgecolor('white')
            else:
                # Alternate row colors
                if row % 2:
                    cell.set_facecolor('#F8F9F9')
                else:
                    cell.set_facecolor('white')
                cell.set_edgecolor('#E5E8E8')
            
            cell.PAD = 0.3
        
        # Add title above table
        table_ax.text(
            0.5, 0.95, 
            'Top 10 Phrases',
            horizontalalignment='center',
            fontsize=12,
            fontweight='bold'
        )
        
        plt.tight_layout()
        
        # Save with high quality
        plt.savefig(
            output_path, 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none',
            pad_inches=0.3
        )
        plt.close()

    def get_color_func_bigrams(self, word, **kwargs):
        """Modified color function for bigrams using the same categories as self.color_categories."""
        word = word.lower()
        
        # Use the same categories and colors as defined in __init__
        for category, terms in self.color_categories.items():
            if any(term in word for term in terms):
                return self.colors[category]
        
        return '#666666'  # Default gray for uncategorized terms
        

    def print_top_terms(self, n=30):
        """Print top terms and their frequencies for verification."""
        all_text = ' '.join(talk['content']['cleaned_text'] 
                           for talk in self.data['talks'])
        words = all_text.split()
        word_freq = Counter(words)
        
        print("\nMost common terms:")
        for word, count in word_freq.most_common(n):
            print(f"{word}: {count}")
            
    def create_topic_network(self, output_path='topic_network.png', min_similarity=0.2):
        # Extract talk titles and content
        talks = [(talk['metadata']['title'], talk['content']['cleaned_text']) 
                for talk in self.data['talks']]
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            stop_words=list(self.custom_stop_words),
            min_df=2
        )
        
        tfidf_matrix = vectorizer.fit_transform([text for _, text in talks])
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes (talks)
        for i, (title, _) in enumerate(talks):
            # Shorten title if too long
            short_title = title[:30] + '...' if len(title) > 30 else title
            G.add_node(i, title=short_title)
        
        # Add edges (connections between similar talks)
        for i in range(len(talks)):
            for j in range(i + 1, len(talks)):
                similarity = similarity_matrix[i, j]
                if similarity > min_similarity:
                    G.add_edge(i, j, weight=similarity)
        
        # Calculate community structure
        communities = community.best_partition(G)
        
        # Set up the visualization
        plt.figure(figsize=(20, 20))
        
        # Calculate node sizes based on degree centrality
        centrality = nx.degree_centrality(G)
        node_sizes = [v * 3000 for v in centrality.values()]
        
        # Calculate edge widths based on similarity
        edge_widths = [G[u][v]['weight'] * 2 for u, v in G.edges()]
        
        # Set up layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw the network
        nx.draw_networkx_edges(G, pos, 
                             alpha=0.2, 
                             width=edge_widths,
                             edge_color='gray')
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos,
                             node_size=node_sizes,
                             node_color=list(communities.values()),
                             cmap=plt.cm.Set3,
                             alpha=0.7)
        
        # Add labels
        labels = nx.get_node_attributes(G, 'title')
        nx.draw_networkx_labels(G, pos, 
                              labels,
                              font_size=8,
                              font_weight='bold')
        
        # Add title
        plt.title('Talk Similarity Network\n(Connections show shared topics)',
                 fontsize=16,
                 pad=20)
        
        # Add legend for communities
        unique_communities = set(communities.values())
        legend_elements = [plt.Line2D([0], [0],
                                    marker='o',
                                    color='w',
                                    label=f'Topic Cluster {i+1}',
                                    markerfacecolor=plt.cm.Set3(i),
                                    markersize=10)
                         for i in unique_communities]
        
        plt.legend(handles=legend_elements,
                  loc='center left',
                  bbox_to_anchor=(1, 0.5))
        
        plt.axis('off')
        plt.tight_layout()
        
        # Save the visualization
        plt.savefig(output_path,
                   dpi=300,
                   bbox_inches='tight',
                   facecolor='white',
                   edgecolor='none')
        plt.close()

    def get_shared_topics(self, talk1_idx, talk2_idx):
        """Get the shared topics between two talks."""
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top terms for each talk
        talk1_terms = set(self._get_top_terms(talk1_idx, feature_names))
        talk2_terms = set(self._get_top_terms(talk2_idx, feature_names))
        
        return talk1_terms.intersection(talk2_terms)


# Usage
if __name__ == "__main__":
    visualizer = ConferenceVisualizer('tech-seo-connect-summary/all_talks.json')
    visualizer.create_wordcloud()
    visualizer.create_bigram_cloud()
    visualizer.print_top_terms()  # Optional: to verify terms
