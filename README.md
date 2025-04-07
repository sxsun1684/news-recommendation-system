# News Recommendation System
## Background

With the rapid development of digital media and increasing demand for efficient information acquisition, personalized news recommendation systems have emerged as a key solution to the problem of information overload. Traditional news curation methods, such as editor-based selection or rule-based filtering, struggle to keep pace with the volume and diversity of today's news content. As a result, building intelligent recommendation systems that can dynamically model user preferences and deliver timely, relevant news has become a significant research and engineering challenge.

Compared to general recommendation systems, news recommendation poses several unique challenges:  
1. News items have extremely short lifespans, requiring real-time relevance;  
2. User feedback is often implicit (e.g., clicks), which is sparse and noisy;  
3. User interests are complex, diverse, and evolve rapidly;  
4. News content is typically high-dimensional text, requiring sophisticated semantic modeling.

In this context, Wu et al. (2021) proposed a comprehensive research framework in their survey *"Personalized News Recommendation: Methods and Challenges"*. Rather than categorizing by traditional recommendation methods (e.g., collaborative filtering, content-based), they structured the field around six core research problems:  
- **News Modeling**: Learning semantic representations of news from text, images, and metadata;  
- **User Modeling**: Capturing dynamic, multi-interest profiles from behavior data;  
- **Personalized Ranking**: Accurately ranking candidate news items based on user interest;  
- **Model Training**: Utilizing supervised, weakly supervised, or multi-task learning techniques;  
- **Evaluation & Datasets**: Designing meaningful metrics and using real-world datasets (e.g., MIND, Adressa);  
- **Responsible Recommendation**: Addressing fairness, diversity, and privacy concerns in system design.

This project is inspired by the aforementioned framework and aims to build a real-world personalized news recommendation system. Leveraging deep learning and natural language processing techniques, the system covers the entire pipeline — from content understanding and user modeling to recommendation and evaluation. The architecture is built using a Flask-based backend and React-based frontend, integrated with Kafka as a message queue for scalability and DynamoDB for efficient data storage and retrieval.

Our goal is not only to optimize recommendation accuracy but also to tackle broader challenges such as cold start, user interest shift, and responsible recommendation. This project serves as a practical implementation that bridges cutting-edge research insights with production-ready system design.


## Overview
This project is a **news recommendation system** that provides personalized news recommendations to users. It utilizes **Flask** as the backend, **React** as the frontend, **DynamoDB** for data storage, and **Kafka** for message queuing. Machine learning algorithms are employed to enhance recommendation quality.
![system design](display/general.png)
## Features
- **News Scraping**: Uses Python crawlers to collect BBC news articles.
- **Data Storage**: Stores news articles and user interactions in **DynamoDB**.
- **Recommendation Algorithm**: Implements **Collaborative Filtering** (SVD, Item-based CF) and **Content-based Recommendation**.
- **Backend API**: Flask-based API that delivers news recommendations to users.
- **Frontend**: A React-based UI that displays categorized news and recommendations.
- **Caching Optimization**: Uses **Redis** to cache frequently accessed news data.
- **High Concurrency Support**: Utilizes **Kafka** for message processing and Redis for reducing database load.

## System Architecture
1. **Data Collection**:
    - Python crawler fetches BBC news articles and sends them to Kafka.
    - Kafka streams data into DynamoDB for storage.
2. **Data Processing & Storage**:
    - DynamoDB stores articles and user data.
    - Redis caches hot articles to enhance query efficiency.
3. **Recommendation Engine**:
    - User activity logs feed into the recommendation system.
    - Machine learning models process user preferences to suggest articles.
4. **Backend & API**:
    - Flask API provides endpoints for retrieving news and recommendations.
    - The system supports user authentication and browsing history tracking.
5. **Frontend**:
    - A React-based UI that displays categorized news and personalized recommendations.

## Installation & Setup
### Prerequisites
Ensure you have the following installed:

- Python 3.x
- Node.js 16+
- Flask
- DynamoDB (AWS setup required)
- Kafka (Local or cloud setup)
- Redis
### Backend Setup
1. Clone the repository:
    ```
    git clone https://github.com/your-repo/news-recommendation.git
    cd news-recommendation/backend
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Set up environment variables in a `.env` file:
    ```
    AWS_ACCESS_KEY=your_key
    AWS_SECRET_KEY=your_secret
    DYNAMODB_REGION=us-west-1
    ``` 
4. Run the Flask server:
    ```
    python3 server.py
    ```
### Frontend Setup

1. Navigate to the frontend directory:
    ```
    cd ../frontend
    ```
2. Install dependencies:
    ```
    npm install
    ```
3. Start the development server:
    ```
    npm run dev
    ```
## API Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/news` | Get latest news articles |
| GET | `/recommendations?user_id=<id>` | Get personalized recommendations |
| POST | `/user/activity` | Log user activity |

## Future Improvements
- Add real-time recommendation updates.
- Expand dataset to more news sources.
- Improve recommendation model with NLP/ML techniques.

### Node2Vec Combined with PageRank for Weight Adjustment 

### Method
1. **Compute News Content Similarity**:
   - Use **TF-IDF** to extract text features from news articles.
   - Calculate **cosine similarity** to measure the semantic closeness between articles.

2. **Construct a News-Graph (News-to-News Network)**:
   - Represent news articles as **nodes** in the graph.
   - Establish **edges** between similar articles, with weights based on their TF-IDF similarity score.

3. **Apply PageRank to Compute News Importance**:
   - Run the **PageRank algorithm** to determine the relative importance of each news article.
   - Higher PageRank scores indicate more significant articles, which should be prioritized in recommendations.

4. **Incorporate Node2Vec for Learning News Embeddings (Optional)**:
   - Use **Node2Vec to generate vector representations (embeddings) of news articles**, capturing deeper structural relationships.
   - Employ **KNN or MLP models** to refine recommendations based on learned embeddings.

---

### Use Cases
**Content-Based Recommendation**: Enhances recommendations by leveraging both **news content and structure**, rather than solely relying on user interaction data.  
**Cold Start Problem**: Helps recommend relevant news articles even for new users with limited interaction history.  
**Graph-Based AI Optimization**: Provides a structured way to rank and recommend news using **graph-based learning techniques**.

---

### Reference

Wu, C., Wu, F., Ge, S., Qi, T., Huang, Y., & Xie, X. (2021). *Personalized News Recommendation: Methods and Challenges*. ACM Transactions on Information Systems (TOIS), 39(2), 1–42. https://doi.org/10.1145/3447553
