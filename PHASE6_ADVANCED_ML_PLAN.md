# 🧠 PHASE 6: ADVANCED ML — PLAN

**Status:** 📋 Ready to Build  
**Estimated Time:** 2-3 weeks  
**Priority:** HIGH (Revenue/UX multiplier)  
**Tech Stack:** Python + OpenAI + scikit-learn + PostgreSQL  

---

## 🎯 PHASE 6 GOAL

Превратить Contacts из "тупого CRM" в **"умного советника"**, который:

1. **Recommends** — "Ты должен познакомиться с Иваном" (semantic match)
2. **Predicts** — "Петр скоро перестанет быть важным в твоей сети" (churn prediction)
3. **Understands** — "Твои контакты в основном позитивны" (sentiment)
4. **Groups** — "Вот 5 кластеров контактов по интересам" (clustering)

---

## 📦 PHASE 6 COMPONENTS

### Component 1: Contact Embeddings (Semantic Search)

**Что:** Каждый контакт → 1536-мерный вектор (OpenAI text-embedding-3-small)

**Зачем:** 
- Найти похожих людей по description/tags/organization
- "Найди людей похожих на Петра"
- Cluster контакты по интересам

**Файл:** `api/ml/embeddings_service.py`

```python
class ContactEmbeddingsService:
    def __init__(self, supabase, openai_client):
        self.supabase = supabase
        self.client = openai_client
    
    async def generate_embedding(self, contact: Dict) -> np.ndarray:
        """Генерировать embedding для контакта"""
        # Конкатенация: first_name + last_name + organization + tags + notes
        text = f"{contact['first_name']} {contact['last_name']} \
                {contact.get('organization', '')} \
                {' '.join(contact.get('tags', []))}"
        
        response = await asyncio.to_thread(
            self.client.embeddings.create,
            input=text,
            model="text-embedding-3-small"
        )
        return np.array(response.data[0].embedding)
    
    async def find_similar_contacts(self, contact_id: str, top_n: int = 10) -> List[Dict]:
        """Найти топ-N похожих контактов"""
        # 1. Получить embedding target contact
        target_emb = await self.supabase.table('contact_embeddings')\
            .select('embedding').eq('contact_id', contact_id).execute()
        
        # 2. Использовать pgvector для similarity search
        # SELECT contact_id, 1 - (embedding <=> target_emb) as similarity
        # FROM contact_embeddings
        # ORDER BY similarity DESC LIMIT top_n
        
        similar = await self.supabase.rpc(
            'search_similar_contacts',
            {'target_embedding': target_emb[0]['embedding'], 'limit': top_n}
        ).execute()
        
        return similar.data
    
    async def batch_generate_embeddings(self, contacts: List[Dict]) -> None:
        """Batch генерировать embeddings для всех контактов (nightly job)"""
        embeddings_data = []
        
        for contact in contacts:
            emb = await self.generate_embedding(contact)
            embeddings_data.append({
                'contact_id': contact['id'],
                'embedding': emb.tolist(),  # pgvector format
                'updated_at': datetime.utcnow().isoformat()
            })
        
        await self.supabase.table('contact_embeddings').upsert(embeddings_data).execute()
```

**GraphQL Query:**
```graphql
query {
  similarContacts(contactId: "uuid", limit: 10) {
    id
    firstName
    lastName
    similarity  # 0.0-1.0
    organization
  }
}
```

---

### Component 2: Contact Recommendations ("People You Should Know")

**Что:** ML модель предсказывает "какие контакты ты должен знать" на основе:
- Твоей сети (кто ты уже знаешь)
- Его сети (кто он знает)
- Семантического match (похожий фокус/интересы)
- Его influence (важный = рекомендуем)

**Файл:** `api/ml/recommendation_engine.py`

```python
class RecommendationEngine:
    def __init__(self, supabase, embeddings_service):
        self.supabase = supabase
        self.embeddings = embeddings_service
    
    async def recommend_contacts(
        self,
        user_contact_id: str,
        limit: int = 20,
        min_score: float = 0.6
    ) -> List[Dict]:
        """Рекомендовать контакты для знакомства"""
        
        recommendations = []
        
        # 1. Получить контакты друзей (2-hop network)
        friends_of_friends = await self._get_friends_of_friends(user_contact_id)
        
        # 2. Для каждого кандидата считать score:
        for candidate in friends_of_friends:
            score = await self._compute_recommendation_score(
                user_contact_id,
                candidate,
                weights={
                    'mutual_friends': 0.3,
                    'semantic_similarity': 0.3,
                    'influence_score': 0.25,
                    'same_organization': 0.15
                }
            )
            
            if score >= min_score:
                recommendations.append({
                    'contact_id': candidate['id'],
                    'score': score,
                    'reason': self._explain_reason(score, candidate),
                    **candidate
                })
        
        # 3. Sort by score, return top-N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    async def _compute_recommendation_score(
        self,
        user_id: str,
        candidate: Dict,
        weights: Dict
    ) -> float:
        """Вычислить score рекомендации"""
        score = 0.0
        
        # Mutual friends (кол-во общих контактов)
        mutual = await self._count_mutual_friends(user_id, candidate['id'])
        score += (mutual / 10.0) * weights['mutual_friends']  # Normalize
        
        # Semantic similarity (embedding match)
        similarity = await self.embeddings.get_similarity(
            user_id, candidate['id']
        )
        score += similarity * weights['semantic_similarity']
        
        # Influence score (важность кандидата)
        influence = candidate.get('influence_score', 0)
        score += influence * weights['influence_score']
        
        # Same organization bonus
        if candidate.get('organization') == user_contact['organization']:
            score += weights['same_organization']
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _explain_reason(self, score: float, candidate: Dict) -> str:
        """Объяснить почему рекомендуем"""
        if score > 0.85:
            return f"Strong match: mutual friends + high influence"
        elif score > 0.7:
            return f"Good match: shares your interests"
        else:
            return f"Potential connection: {score*100:.0f}% match"
```

**GraphQL Query:**
```graphql
query {
  recommendedContacts(limit: 20, minScore: 0.6) {
    id
    firstName
    score
    reason
    influence
    organization
  }
}
```

---

### Component 3: Churn Prediction ("Who Will Become Unimportant?")

**Что:** Предсказать кто будет терять значимость в твоей сети

**Сигналы:**
- ↓ Frequency of interactions (emails/meetings/calls)
- ↓ Shared tags/groups
- → Different organization (job change)
- → Long time no contact (>3 months)

**Файл:** `api/ml/churn_predictor.py`

```python
from sklearn.ensemble import RandomForestClassifier
import pickle

class ChurnPredictor:
    def __init__(self, supabase):
        self.supabase = supabase
        self.model = None  # Will load/train nightly
    
    async def predict_churn(
        self,
        contact_id: str
    ) -> Dict:
        """Предсказать вероятность "выпадения" контакта"""
        
        # 1. Извлечь features
        features = await self._extract_features(contact_id)
        
        # 2. Predict
        churn_probability = self.model.predict_proba([features])[0][1]
        
        return {
            'contact_id': contact_id,
            'churn_probability': churn_probability,  # 0.0-1.0
            'risk_level': self._risk_level(churn_probability),
            'interventions': self._suggest_interventions(features)
        }
    
    async def _extract_features(self, contact_id: str) -> List[float]:
        """Извлечь признаки для модели"""
        contact = await self.supabase.table('apple_contacts').select('*')\
            .eq('id', contact_id).execute()
        
        # Get interaction history
        sync_history = await self.supabase.table('contact_sync_history')\
            .select('*').eq('contact_id', contact_id)\
            .order('created_at', desc=True).limit(12).execute()
        
        features = [
            # 1. Days since last update
            (datetime.utcnow() - contact['updated_at']).days / 365,
            
            # 2. Interaction frequency (interactions per month, last 3 months)
            len([s for s in sync_history if (datetime.utcnow() - s['created_at']).days < 90]) / 3,
            
            # 3. Influence score (higher influence = lower churn)
            1.0 - (contact['influence_score'] or 0),
            
            # 4. Number of tags (more tags = more connected)
            len(contact.get('tags', [])) / 10,
            
            # 5. Community size (bigger community = lower churn)
            await self._get_community_size(contact['community_id']) / 100,
        ]
        
        return features
    
    def _risk_level(self, probability: float) -> str:
        """Уровень риска"""
        if probability > 0.7:
            return "HIGH"
        elif probability > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _suggest_interventions(self, features: List[float]) -> List[str]:
        """Что делать, чтобы не потерять контакт"""
        suggestions = []
        
        if features[0] > 0.5:  # Days since update
            suggestions.append("Reach out - no recent contact")
        
        if features[1] < 0.1:  # Low interaction
            suggestions.append("Schedule a meeting")
        
        if features[4] < 0.2:  # Small community
            suggestions.append("Introduce to others in your network")
        
        return suggestions
    
    async def train_model(self, training_data: List[Tuple]) -> None:
        """Тренировать модель (nightly job, раз в неделю)"""
        X = [t[0] for t in training_data]  # Features
        y = [t[1] for t in training_data]  # Labels (churned=1, active=0)
        
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10)
        self.model.fit(X, y)
        
        # Save model to disk or DB
        model_bytes = pickle.dumps(self.model)
        await self.supabase.table('ml_models').upsert({
            'model_name': 'churn_predictor',
            'model_data': model_bytes,
            'trained_at': datetime.utcnow().isoformat()
        }).execute()
```

**GraphQL Query:**
```graphql
query {
  churnRisk(contactId: "uuid") {
    probability  # 0.0-1.0
    riskLevel    # HIGH, MEDIUM, LOW
    interventions  # ["Reach out", ...]
  }
}
```

---

### Component 4: Sentiment Analysis (Contact Tone/Vibe)

**Что:** Анализировать "тон" контакта на основе:
- Tags (positive: "mentor", "friend"; negative: "difficult", "skeptical")
- Notes (если они есть)
- Interaction history (частота, позитив/негатив)

**Файл:** `api/ml/sentiment_analyzer.py`

```python
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self, supabase):
        self.supabase = supabase
    
    async def analyze_contact_sentiment(self, contact_id: str) -> Dict:
        """Анализировать 'тон' контакта"""
        
        contact = await self.supabase.table('apple_contacts').select('*')\
            .eq('id', contact_id).execute()
        
        # 1. Tag-based sentiment
        tag_sentiment = self._analyze_tags(contact.get('tags', []))
        
        # 2. Notes-based sentiment (если есть)
        notes_sentiment = 0.0
        if contact.get('notes'):
            blob = TextBlob(contact['notes'])
            notes_sentiment = blob.sentiment.polarity  # -1 to 1
        
        # 3. Interaction pattern (частые контакты = позитив)
        interaction_sentiment = await self._analyze_interaction_pattern(contact_id)
        
        # Weighted average
        overall_sentiment = (
            tag_sentiment * 0.4 +
            notes_sentiment * 0.3 +
            interaction_sentiment * 0.3
        )
        
        return {
            'contact_id': contact_id,
            'overall_sentiment': overall_sentiment,  # -1 to 1
            'sentiment_label': self._sentiment_label(overall_sentiment),
            'components': {
                'tags': tag_sentiment,
                'notes': notes_sentiment,
                'interactions': interaction_sentiment
            }
        }
    
    def _analyze_tags(self, tags: List[str]) -> float:
        """Анализировать tags"""
        positive_tags = {'mentor', 'friend', 'collaborator', 'advisor', 'supporter'}
        negative_tags = {'difficult', 'skeptical', 'competitor', 'rival'}
        
        positive_count = len([t for t in tags if t.lower() in positive_tags])
        negative_count = len([t for t in tags if t.lower() in negative_tags])
        total = positive_count + negative_count
        
        if total == 0:
            return 0.0  # Neutral
        
        return (positive_count - negative_count) / total
    
    def _sentiment_label(self, sentiment: float) -> str:
        """Текстовый лейбл"""
        if sentiment > 0.5:
            return "Very Positive"
        elif sentiment > 0.2:
            return "Positive"
        elif sentiment > -0.2:
            return "Neutral"
        elif sentiment > -0.5:
            return "Negative"
        else:
            return "Very Negative"
```

**GraphQL Query:**
```graphql
query {
  contactSentiment(contactId: "uuid") {
    overallSentiment  # -1 to 1
    label             # "Very Positive", etc
  }
}
```

---

### Component 5: Contact Clustering (Interest Groups)

**Что:** Автоматически группировать контакты по интересам (K-means)

**Зачем:** Видеть "кто с кем общается" по интересам

**Файл:** `api/ml/clustering_service.py`

```python
from sklearn.cluster import KMeans
import numpy as np

class ContactClusteringService:
    def __init__(self, supabase, embeddings_service):
        self.supabase = supabase
        self.embeddings = embeddings_service
    
    async def cluster_contacts(self, n_clusters: int = 5) -> Dict:
        """Кластеризовать контакты по интересам"""
        
        # 1. Получить все embeddings
        embeddings_data = await self.supabase.table('contact_embeddings')\
            .select('contact_id, embedding').execute()
        
        embeddings = np.array([e['embedding'] for e in embeddings_data])
        contact_ids = [e['contact_id'] for e in embeddings_data]
        
        # 2. K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        # 3. Сохранить clusters
        clusters = defaultdict(list)
        for contact_id, label in zip(contact_ids, labels):
            clusters[int(label)].append(contact_id)
        
        # 4. Сохранить в DB
        for cluster_id, contacts in clusters.items():
            await self.supabase.table('contact_clusters').upsert({
                'cluster_id': cluster_id,
                'contacts': contacts,
                'cluster_size': len(contacts),
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        
        return {
            'total_clusters': n_clusters,
            'clusters': dict(clusters),
            'cluster_sizes': {k: len(v) for k, v in clusters.items()}
        }
```

**GraphQL Query:**
```graphql
query {
  contactClusters {
    id
    size
    topTopics  # Inferred from contact tags in cluster
  }
}
```

---

## 📊 PHASE 6 DATABASE SCHEMA ADDITIONS

```sql
-- Contact embeddings (pgvector)
CREATE TABLE contact_embeddings (
    contact_id UUID PRIMARY KEY,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contact_embeddings_cosine ON contact_embeddings
    USING ivfflat (embedding vector_cosine_ops);

-- Contact recommendations
CREATE TABLE contact_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_contact_id UUID NOT NULL,
    recommended_contact_id UUID NOT NULL,
    score NUMERIC(5,4),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Churn predictions
CREATE TABLE churn_predictions (
    contact_id UUID PRIMARY KEY,
    churn_probability NUMERIC(5,4),
    risk_level TEXT,  -- HIGH, MEDIUM, LOW
    interventions TEXT[],
    predicted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact sentiment
CREATE TABLE contact_sentiment (
    contact_id UUID PRIMARY KEY,
    overall_sentiment NUMERIC(5,3),  -- -1 to 1
    sentiment_label TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact clusters
CREATE TABLE contact_clusters (
    cluster_id INT,
    contact_id UUID,
    cluster_size INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML models (versioning)
CREATE TABLE ml_models (
    model_name TEXT,
    model_data BYTEA,  -- Pickled scikit-learn model
    trained_at TIMESTAMPTZ,
    accuracy NUMERIC(5,4),  -- For churn predictor
    PRIMARY KEY (model_name, trained_at)
);
```

---

## 🔄 PHASE 6 NIGHTLY PIPELINE

Добавить в `scheduler.py`:

```python
@scheduler.scheduled_job("cron", hour=4, minute=0)
async def phase6_embeddings_job():
    """Генерировать embeddings для всех контактов (nightly)"""
    contacts = supabase.table('apple_contacts').select('*').execute().data
    service = ContactEmbeddingsService(supabase, openai_client)
    await service.batch_generate_embeddings(contacts)
    logger.info("✅ Embeddings generated for all contacts")

@scheduler.scheduled_job("cron", hour=4, minute=15)
async def phase6_recommendations_job():
    """Генерировать recommendations"""
    engine = RecommendationEngine(supabase, embeddings_service)
    contacts = supabase.table('apple_contacts').select('id').execute().data
    
    for contact in contacts:
        recommendations = await engine.recommend_contacts(
            contact['id'],
            limit=20,
            min_score=0.6
        )
        # Save to DB
    
    logger.info("✅ Recommendations generated")

@scheduler.scheduled_job("cron", hour=4, minute=30)
async def phase6_churn_job():
    """Предсказать churn (раз в неделю)"""
    predictor = ChurnPredictor(supabase)
    
    # Train model
    training_data = await prepare_training_data(supabase)
    await predictor.train_model(training_data)
    
    # Predict for all contacts
    contacts = supabase.table('apple_contacts').select('id').execute().data
    for contact in contacts:
        prediction = await predictor.predict_churn(contact['id'])
        # Save to DB
    
    logger.info("✅ Churn predictions updated")

@scheduler.scheduled_job("cron", hour=4, minute=45)
async def phase6_sentiment_job():
    """Анализировать sentiment"""
    analyzer = SentimentAnalyzer(supabase)
    contacts = supabase.table('apple_contacts').select('*').execute().data
    
    for contact in contacts:
        sentiment = await analyzer.analyze_contact_sentiment(contact['id'])
        # Save to DB
    
    logger.info("✅ Sentiment analysis completed")

@scheduler.scheduled_job("cron", hour=5, minute=0)
async def phase6_clustering_job():
    """Кластеризовать контакты"""
    clustering = ContactClusteringService(supabase, embeddings_service)
    result = await clustering.cluster_contacts(n_clusters=5)
    logger.info(f"✅ Clustering complete: {result['total_clusters']} clusters")
```

---

## 🚀 PHASE 6 GraphQL ADDITIONS

```graphql
type Query {
    # Embeddings
    similarContacts(contactId: UUID!, limit: Int): [Contact!]!
    
    # Recommendations
    recommendedContacts(limit: Int, minScore: Float): [ContactRecommendation!]!
    
    # Churn Prediction
    churnRisk(contactId: UUID!): ChurnPrediction!
    allChurnRisks(riskLevel: String): [ChurnPrediction!]!
    
    # Sentiment
    contactSentiment(contactId: UUID!): ContactSentiment!
    sentimentOverview: SentimentStats!
    
    # Clustering
    contactClusters: [ContactCluster!]!
    clusterDetails(clusterId: Int!): ClusterDetails!
}

type ContactRecommendation {
    id: UUID!
    score: Float!
    reason: String!
    contact: Contact!
}

type ChurnPrediction {
    contactId: UUID!
    probability: Float!  # 0.0-1.0
    riskLevel: String!   # HIGH, MEDIUM, LOW
    interventions: [String!]!
}

type ContactSentiment {
    contactId: UUID!
    overallSentiment: Float!  # -1 to 1
    label: String!  # "Very Positive", etc
}

type SentimentStats {
    averageSentiment: Float!
    positiveCount: Int!
    neutralCount: Int!
    negativeCount: Int!
}

type ContactCluster {
    id: Int!
    size: Int!
    topTopics: [String!]!
    members: [Contact!]!
}
```

---

## 📊 PHASE 6 WEB UI ADDITIONS

Добавить новые страницы в `web/app/dashboard/`:

1. **`recommendations/page.tsx`**
   - "People You Should Know"
   - Cards с score + reason
   - "Connect" button

2. **`churn-analysis/page.tsx`**
   - Таблица контактов с churn_probability
   - Filter by risk level
   - Interventions suggestions

3. **`sentiment-analysis/page.tsx`**
   - Overall sentiment distribution (pie chart)
   - Per-contact sentiment labels
   - Sentiment trends over time

4. **`interest-clusters/page.tsx`**
   - Clusters visualization (circles/bubbles)
   - Click cluster → see members
   - Inferred topics per cluster

---

## ✅ PHASE 6 "DONE" CRITERIA

- [ ] Contact embeddings (text-embedding-3-small via OpenAI)
- [ ] pgvector installed in Supabase
- [ ] Similarity search working (find_similar_contacts)
- [ ] Recommendation engine implemented
- [ ] Churn predictor trained (RandomForest)
- [ ] Sentiment analyzer working
- [ ] Contact clustering (K-means)
- [ ] All 5 nightly jobs running
- [ ] All GraphQL queries implemented
- [ ] 5 new web pages created
- [ ] Tests written (unit + integration)
- [ ] Documentation updated

**Итого:** ~3,000+ строк Python + ~1,500 строк React

---

## 📈 REVENUE/UX IMPACT

**After Phase 6 complete:**

✨ **"Smart CRM"** — система, которая:
- Рекомендует кого нужно познакомить → больше продаж
- Предупреждает о потере контактов → лучше manage relationships
- Группирует по интересам → лучше организовать сеть
- Анализирует тон → лучше понимать отношения

💰 **Monetization potential:**
- B2B: Sales teams (finding leads)
- B2C: Networking apps
- Enterprise: HR/recruiting

---

## 🎯 NEXT STEPS

1. **Setup OpenAI API key** (for embeddings)
2. **Add pgvector to Supabase** (in DB)
3. **Implement Component 1** (Embeddings) → test
4. **Implement Component 2** (Recommendations) → test
5. **Implement Component 3** (Churn) → train model
6. **Implement Component 4** (Sentiment) → test
7. **Implement Component 5** (Clustering) → visualize
8. **Add to nightly pipeline**
9. **Add GraphQL queries**
10. **Build web UI pages**
11. **Test end-to-end**
12. **Deploy**

---

**Phase 6 = "AI-Powered CRM"**

После этого Contacts v2.0 будет готова к:
- Enterprise sales
- Venture capital
- IPO readiness

**Let's build the future of contact management.** 🚀
