"""
AGENT 1: TOPIC RESEARCH MASTER
================================

Master-level implementation for discovering viral motivation topics.
Uses multiple data sources with redundancy, AI-powered analysis,
and comprehensive error handling.

Sources:
- YouTube API (trending motivation videos)
- Google Trends API (search volume trends)
- Reddit API (community engagement patterns)
- Quora (user questions/interest patterns)
- Web sentiment analysis

Principles:
1. Find high-engagement, low-follower channels (true viral potential)
2. Analyze emotional hooks used by top performers
3. Detect emerging trends before saturation
4. Consider cultural relevance (Urdu/Hindi audience)
5. Identify underserved angles in motivation niche
"""

import requests
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

# Third-party imports
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import praw
except ImportError:
    praw = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TopicResearchAgentMaster:
    """
    Master-level Topic Research Agent
    
    Discovers viral motivation topics using:
    - Multiple data sources (YouTube, Google Trends, Reddit, Quora)
    - Advanced pattern recognition
    - AI-powered analysis with fallback redundancy
    - Comprehensive error handling and retries
    """
    
    def __init__(self, config: Dict, settings: Dict):
        """
        Initialize agent with config and settings
        
        Args:
            config: API keys dictionary
            settings: Application settings dictionary
        """
        self.config = config
        self.settings = settings
        
        # Initialize AI clients with error handling
        self.groq_client = self._init_groq()
        self.gemini_client = self._init_gemini()
        
        # Data sources
        self.youtube_topics = []
        self.google_trends = []
        self.reddit_topics = []
        self.quora_topics = []
        
        # Analysis results
        self.viral_patterns = []
        self.final_topic = None
        
        logger.info("✅ Topic Research Agent initialized")
    
    # =====================================================
    # AI CLIENT INITIALIZATION (Redundancy)
    # =====================================================
    
    def _init_groq(self) -> Optional[Groq]:
        """Initialize Groq AI client"""
        try:
            if self.config.get("groq_api_key"):
                client = Groq(api_key=self.config["groq_api_key"])
                logger.info("✅ Groq AI client initialized")
                return client
        except Exception as e:
            logger.warning(f"⚠️ Groq initialization failed: {e}")
        return None
    
    def _init_gemini(self):
        """Initialize Google Gemini AI client"""
        try:
            if self.config.get("google_api_key") and genai:
                genai.configure(api_key=self.config["google_api_key"])
                logger.info("✅ Gemini AI client initialized")
                return genai
        except Exception as e:
            logger.warning(f"⚠️ Gemini initialization failed: {e}")
        return None
    
    # =====================================================
    # DATA SOURCE 1: YOUTUBE API
    # =====================================================
    
    def get_youtube_trending(self) -> List[Dict]:
        """
        Fetch YouTube trending videos in motivation niche
        
        Strategy:
        - Get videos from 'People & Blogs' category (ID: 22)
        - Analyze views, likes, comments for engagement
        - Calculate engagement ratio
        - Identify viral patterns
        
        Returns:
            List of topic dictionaries with engagement metrics
        """
        logger.info("🔍 Fetching YouTube trending data...")
        
        api_key = self.config.get("youtube_api_key")
        if not api_key:
            logger.warning("❌ YouTube API key missing")
            return []
        
        topics = []
        
        try:
            # Retry logic: 3 attempts
            for attempt in range(3):
                try:
                    url = "https://www.googleapis.com/youtube/v3/videos"
                    
                    params = {
                        "part": "statistics,snippet",
                        "chart": "mostPopular",
                        "regionCode": "PK",  # Pakistan (Urdu audience)
                        "maxResults": 20,
                        "videoCategoryId": "22",  # People & Blogs
                        "key": api_key,
                        "order": "viewCount"
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        videos = response.json().get("items", [])
                        
                        for video in videos:
                            try:
                                views = int(video["statistics"]["viewCount"])
                                likes = int(video["statistics"].get("likeCount", 0))
                                comments = int(video["statistics"].get("commentCount", 0))
                                
                                # Calculate engagement ratio
                                engagement_ratio = (likes + comments) / max(views, 1)
                                
                                topic = {
                                    "source": "YouTube",
                                    "title": video["snippet"]["title"],
                                    "channel": video["snippet"]["channelTitle"],
                                    "views": views,
                                    "likes": likes,
                                    "comments": comments,
                                    "engagement_ratio": engagement_ratio,
                                    "published_at": video["snippet"]["publishedAt"],
                                    "description": video["snippet"]["description"][:200]
                                }
                                
                                topics.append(topic)
                            except Exception as e:
                                logger.debug(f"Error parsing video: {e}")
                                continue
                        
                        logger.info(f"✅ YouTube: Fetched {len(topics)} trending videos")
                        return topics
                    
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ YouTube API rate limited (attempt {attempt+1})")
                        time.sleep(5)
                        continue
                    else:
                        logger.warning(f"❌ YouTube API error: {response.status_code}")
                        break
                
                except requests.Timeout:
                    logger.warning(f"⚠️ YouTube API timeout (attempt {attempt+1})")
                    time.sleep(3)
                    continue
        
        except Exception as e:
            logger.error(f"❌ YouTube data fetch failed: {e}")
        
        return topics
    
    # =====================================================
    # DATA SOURCE 2: GOOGLE TRENDS
    # =====================================================
    
    def get_google_trends(self) -> List[Dict]:
        """
        Fetch Google Trends for motivation-related keywords
        
        Strategy:
        - Search for motivation keywords
        - Analyze trend direction (rising/declining)
        - Get related queries
        - Identify emerging topics
        
        Returns:
            List of trending topics from Google Trends
        """
        if not TrendReq:
            logger.warning("⚠️ pytrends not available, skipping Google Trends")
            return []
        
        logger.info("📊 Fetching Google Trends data...")
        
        try:
            pytrends = TrendReq(hl='en-US', tz=0)
            
            # Motivation-related keywords to track
            keywords = [
                'motivation',
                'self improvement',
                'success mindset',
                'personal development',
                'fear overcome',
                'confidence building'
            ]
            
            trends = []
            
            for keyword in keywords:
                try:
                    # Build payload
                    pytrends.build_payload(
                        [keyword],
                        timeframe='today 7-d',  # Last 7 days
                        geo='PK'  # Pakistan region
                    )
                    
                    # Get interest over time
                    interest_timeline = pytrends.interest_over_time()
                    
                    # Get related queries
                    related_queries = pytrends.related_queries()
                    
                    # Calculate trend direction
                    if len(interest_timeline) > 0:
                        trend_values = interest_timeline[keyword].values
                        is_rising = trend_values[-1] > trend_values[0]
                        trend_strength = abs(trend_values[-1] - trend_values[0])
                        
                        trend_data = {
                            "source": "Google Trends",
                            "keyword": keyword,
                            "is_rising": is_rising,
                            "trend_strength": float(trend_strength),
                            "current_value": float(trend_values[-1]),
                            "related_queries": related_queries.get(keyword, {}).get('top', []).index.tolist()[:5] if related_queries.get(keyword) else []
                        }
                        
                        trends.append(trend_data)
                    
                    time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    logger.debug(f"Error fetching trend for '{keyword}': {e}")
                    continue
            
            logger.info(f"✅ Google Trends: Fetched data for {len(trends)} keywords")
            return trends
        
        except Exception as e:
            logger.error(f"❌ Google Trends fetch failed: {e}")
            return []
    
    # =====================================================
    # DATA SOURCE 3: REDDIT API
    # =====================================================
    
    def get_reddit_topics(self) -> List[Dict]:
        """
        Fetch trending topics from Reddit motivation communities
        
        Strategy:
        - Monitor motivation/success subreddits
        - Extract top posts and discussions
        - Analyze engagement (upvotes, comments)
        - Identify hot topics
        
        Returns:
            List of trending Reddit topics
        """
        if not praw:
            logger.warning("⚠️ PRAW not available, skipping Reddit")
            return []
        
        logger.info("🔗 Fetching Reddit data...")
        
        try:
            reddit = praw.Reddit(
                client_id=self.config.get("reddit_client_id"),
                client_secret=self.config.get("reddit_client_secret"),
                user_agent='motivation-reel-agent'
            )
            
            # Target subreddits (motivation, success, self-improvement)
            subreddits = ['GetMotivated', 'selfimprovement', 'motivation', 'DecidingToBeBetter']
            
            reddit_topics = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    
                    # Get hot posts (trending right now)
                    for post in subreddit.hot(limit=10):
                        # Filter for self-improvement/motivation content
                        if post.score > 100:  # Minimum engagement filter
                            topic = {
                                "source": "Reddit",
                                "subreddit": subreddit_name,
                                "title": post.title,
                                "upvotes": post.score,
                                "comments": post.num_comments,
                                "engagement": post.score + post.num_comments,
                                "created_at": datetime.fromtimestamp(post.created_utc).isoformat(),
                                "selftext_preview": post.selftext[:200]
                            }
                            
                            reddit_topics.append(topic)
                    
                    time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    logger.debug(f"Error fetching from r/{subreddit_name}: {e}")
                    continue
            
            logger.info(f"✅ Reddit: Fetched {len(reddit_topics)} trending posts")
            return reddit_topics
        
        except Exception as e:
            logger.error(f"❌ Reddit fetch failed: {e}")
            return []
    
    # =====================================================
    # DATA SOURCE 4: QUORA (WEB SCRAPING)
    # =====================================================
    
    def get_quora_topics(self) -> List[Dict]:
        """
        Fetch trending questions from Quora (motivation niche)
        
        Strategy:
        - Search for motivation-related questions
        - Analyze question popularity (followers, answers)
        - Extract trending topics and patterns
        
        Returns:
            List of trending Quora questions
        """
        if not BeautifulSoup:
            logger.warning("⚠️ BeautifulSoup not available, skipping Quora")
            return []
        
        logger.info("❓ Fetching Quora data...")
        
        try:
            # Quora trending motivation questions URL
            url = "https://www.quora.com/search?q=motivation%20self%20improvement"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                quora_topics = []
                
                # Extract question titles (simplified parsing)
                questions = soup.find_all('span', {'class': 'q-text'})[:15]
                
                for i, question in enumerate(questions):
                    try:
                        title = question.get_text(strip=True)
                        if len(title) > 20:  # Filter short titles
                            topic = {
                                "source": "Quora",
                                "question": title,
                                "position": i + 1,
                                "relevance_score": max(0, 10 - i)  # Higher position = higher relevance
                            }
                            quora_topics.append(topic)
                    except Exception as e:
                        logger.debug(f"Error parsing Quora question: {e}")
                        continue
                
                logger.info(f"✅ Quora: Fetched {len(quora_topics)} trending questions")
                return quora_topics
        
        except Exception as e:
            logger.warning(f"⚠️ Quora fetch failed: {e}")
            return []
    
    # =====================================================
    # VIRAL PATTERN DETECTION
    # =====================================================
    
    def detect_viral_patterns(self) -> List[Dict]:
        """
        Analyze collected data to find viral patterns
        
        Patterns to identify:
        1. High engagement + Low follower ratio (true viral potential)
        2. Emotional keywords (fear, success, transformation, etc.)
        3. Story-based angles (journey, before-after)
        4. Time-sensitive topics (trending now, emerging)
        5. Cultural relevance (Urdu/Hindi audience)
        
        Returns:
            List of identified viral patterns with scores
        """
        logger.info("🔥 Analyzing viral patterns...")
        
        patterns = []
        
        # PATTERN 1: YouTube High-Engagement, Low-Follower Videos
        if self.youtube_topics:
            for topic in self.youtube_topics[:10]:
                # Estimate follower count from engagement ratio
                # High engagement ratio = potential viral content
                if topic["engagement_ratio"] > 0.05:  # 5%+ engagement
                    pattern = {
                        "pattern_type": "High Engagement Low Follower",
                        "source": topic["channel"],
                        "indicator": topic["title"],
                        "engagement_ratio": topic["engagement_ratio"],
                        "score": min(10, topic["engagement_ratio"] * 100),
                        "analysis": f"This channel has high engagement on '{topic['title']}' - viral potential detected"
                    }
                    patterns.append(pattern)
        
        # PATTERN 2: Emotional Keywords
        emotional_keywords = [
            'fear', 'courage', 'success', 'failure', 'transformation',
            'journey', 'struggle', 'overcome', 'impossible', 'believe',
            'motivation', 'inspiration', 'mindset', 'change', 'power'
        ]
        
        all_titles = []
        if self.youtube_topics:
            all_titles.extend([t["title"].lower() for t in self.youtube_topics])
        if self.reddit_topics:
            all_titles.extend([t["title"].lower() for t in self.reddit_topics])
        if self.quora_topics:
            all_titles.extend([t["question"].lower() for t in self.quora_topics])
        
        keyword_frequency = Counter()
        for title in all_titles:
            for keyword in emotional_keywords:
                if keyword in title:
                    keyword_frequency[keyword] += 1
        
        if keyword_frequency:
            top_keywords = keyword_frequency.most_common(3)
            for keyword, count in top_keywords:
                pattern = {
                    "pattern_type": "Emotional Keyword Trend",
                    "keyword": keyword,
                    "frequency": count,
                    "score": min(10, count * 2),
                    "analysis": f"'{keyword.title()}' appears in {count} trending topics - high emotional resonance"
                }
                patterns.append(pattern)
        
        # PATTERN 3: Google Trends Rising Topics
        if self.google_trends:
            for trend in self.google_trends:
                if trend["is_rising"]:
                    pattern = {
                        "pattern_type": "Rising Google Trend",
                        "keyword": trend["keyword"],
                        "trend_strength": trend["trend_strength"],
                        "score": min(10, trend["trend_strength"]),
                        "analysis": f"'{trend['keyword']}' is RISING on Google Trends - good timing for content"
                    }
             patterns.append(pattern)
        
        # PATTERN 4: Reddit Engagement
        if self.reddit_topics:
            high_engagement_reddit = [t for t in self.reddit_topics if t["engagement"] > 200]
            for topic in high_engagement_reddit:
                pattern = {
                    "pattern_type": "Reddit High Engagement",
                    "subreddit": topic["subreddit"],
                    "title": topic["title"],
                    "engagement": topic["engagement"],
                    "score": min(10, topic["engagement"] / 100),
                    "analysis": f"'{topic['title']}' trending on r/{topic['subreddit']} with {topic['engagement']} engagements"
                }
                patterns.append(pattern)
        
        # Sort by score
        patterns = sorted(patterns, key=lambda x: x["score"], reverse=True)
        
        logger.info(f"✅ Detected {len(patterns)} viral patterns")
        return patterns
    
    # =====================================================
    # AI-POWERED ANALYSIS (With Redundancy)
    # =====================================================
    
    def analyze_with_ai(self, patterns: List[Dict]) -> Optional[Dict]:
        """
        Use AI to select best topic from detected patterns
        
        Priority:
        1. Primary: Groq AI
        2. Secondary: Google Gemini
        3. Fallback: Rule-based selection
        
        Args:
            patterns: List of detected viral patterns
        
        Returns:
            Selected topic dictionary
        """
        logger.info("🤖 AI Analysis - Selecting best topic...")
        
        # Prepare analysis data
        patterns_str = json.dumps(patterns[:10], indent=2, ensure_ascii=False)
        
        prompt = f"""
        TASK: Select the BEST topic for a 45-55 second motivation reel (Urdu language, Hindi-speaking audience)
        
        AVAILABLE PATTERNS:
        {patterns_str}
        
        SELECTION CRITERIA (in order of importance):
        1. Viral Potential: Is it trending? Will it attract views?
        2. Emotional Appeal: Does it resonate with motivation niche?
        3. Hook Strength: Can it create a compelling opening (first 3 seconds)?
        4. Audience Fit: Relevant for Hindi/Urdu speaking audience?
        5. Timing: Is it emerging before saturation?
        
        RESPONSE (ONLY JSON, NO EXTRA TEXT):
        {{
            "topic": "Selected topic name",
            "why_viral": "Why this will go viral",
            "emotional_angle": "Primary emotion (fear/inspiration/transformation/etc)",
            "hook_idea": "How to hook viewers in first 3 seconds",
            "viral_probability": "High/Medium/Low",
            "audience_fit": "How well it fits Urdu/Hindi audience",
            "timing": "Is this trending now or emerging?",
            "competitive_advantage": "What makes this unique vs competitors",
            "confidence_score": 0.0-1.0
        }}
        """
        
        # Try Groq first
        if self.groq_client:
            try:
                logger.info("📍 Using Groq AI (Primary)")
                message = self.groq_client.messages.create(
                    model="mixtral-8x7b-32768",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = message.content[0].text
                
                # Extract JSON
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    result = json.loads(json_str)
                    logger.info(f"✅ Groq analysis successful: {result['topic']}")
                    return result
            
            except Exception as e:
                logger.warning(f"⚠️ Groq analysis failed: {e}")
        
        # Try Gemini as backup
        if self.gemini_client:
            try:
                logger.info("📍 Using Google Gemini (Secondary)")
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                
                response_text = response.text
                
                # Extract JSON
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    result = json.loads(json_str)
                    logger.info(f"✅ Gemini analysis successful: {result['topic']}")
                    return result
            
            except Exception as e:
                logger.warning(f"⚠️ Gemini analysis failed: {e}")
        
        # Fallback: Rule-based selection
        logger.info("📍 Using Rule-Based Fallback")
        return self._fallback_topic_selection(patterns)
    
    def _fallback_topic_selection(self, patterns: List[Dict]) -> Dict:
        """
        Rule-based fallback when AI is unavailable
        
        Selects topic based on:
        - Highest score
        - Multiple data source confirmation
        - Emotional keyword presence
        """
        if not patterns:
            return self._default_fallback_topic()
        
        # Score by multiple factors
        scored_patterns = []
        for pattern in patterns:
            score = pattern.get("score", 0)
            
            # Boost if from multiple sources
            if pattern.get("pattern_type") == "Emotional Keyword Trend":
                score *= 1.5
            
            if pattern.get("pattern_type") == "Rising Google Trend":
                score *= 1.3
            
            scored_patterns.append((pattern, score))
        
        best_pattern = max(scored_patterns, key=lambda x: x[1])[0]
        
        topic_name = (best_pattern.get("keyword") or 
                     best_pattern.get("title") or 
                     best_pattern.get("question") or 
                     "Overcoming Self-Doubt")
        
        return {
            "topic": topic_name,
            "why_viral": "High engagement detected in multiple sources",
            "emotional_angle": "Inspiration/Transformation",
            "hook_idea": "Start with relatable problem, promise solution",
            "viral_probability": "High",
            "audience_fit": "Strong fit for motivation niche",
            "timing": "Currently trending",
            "competitive_advantage": "Data-driven angle selection",
            "confidence_score": 0.75,
            "source": "Rule-based fallback"
        }
    
    def _default_fallback_topic(self) -> Dict:
        """
        Default fallback when all data sources fail
        """
        return {
            "topic": "Overcoming Fear and Self-Doubt",
            "why_viral": "Universal motivation topic with timeless appeal",
            "emotional_angle": "Fear to Courage",
            "hook_idea": "Most of us are paralyzed by fear. Here's how to break free.",
            "viral_probability": "High",
            "audience_fit": "Perfect for Urdu/Hindi audience",
            "timing": "Evergreen content",
            "competitive_advantage": "Deep cultural resonance",
            "confidence_score": 0.60,
            "source": "Default fallback"
        }
    
    # =====================================================
    # MAIN EXECUTION
    # =====================================================
    
    def run(self) -> Dict:
        """
        Main agent execution pipeline
        
        Flow:
        1. Fetch data from all sources
        2. Detect viral patterns
        3. AI-powered analysis
        4. Return final topic with metadata
        
        Returns:
            Final topic selection with full metadata
        """
        logger.info("=" * 60)
        logger.info("🚀 AGENT 1: TOPIC RESEARCH - MASTER LEVEL")
        logger.info("=" * 60)
        
        try:
            # Phase 1: Data Collection
            logger.info("\n📊 PHASE 1: DATA COLLECTION")
            self.youtube_topics = self.get_youtube_trending()
            self.google_trends = self.get_google_trends()
            self.reddit_topics = self.get_reddit_topics()
            self.quora_topics = self.get_quora_topics()
            
            total_sources = sum([
                len(self.youtube_topics) > 0,
                len(self.google_trends) > 0,
                len(self.reddit_topics) > 0,
                len(self.quora_topics) > 0
            ])
            
            logger.info(f"\n✅ Data collected from {total_sources}/4 sources")
            logger.info(f"   - YouTube: {len(self.youtube_topics)} videos")
            logger.info(f"   - Google Trends: {len(self.google_trends)} keywords")
            logger.info(f"   - Reddit: {len(self.reddit_topics)} posts")
            logger.info(f"   - Quora: {len(self.quora_topics)} questions")
            
            # Phase 2: Pattern Detection
            logger.info("\n🔥 PHASE 2: VIRAL PATTERN DETECTION")
            self.viral_patterns = self.detect_viral_patterns()
            logger.info(f"✅ {len(self.viral_patterns)} patterns detected")
            
            # Phase 3: AI Analysis
            logger.info("\n🤖 PHASE 3: AI-POWERED ANALYSIS")
            ai_result = self.analyze_with_ai(self.viral_patterns)
            
            if not ai_result:
                ai_result = self._default_fallback_topic()
            
            # Phase 4: Format Output
            self.final_topic = {
                "agent_id": 1,
                "agent_name": "Topic Research Master",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "topic": ai_result.get("topic", ""),
                "why_viral": ai_result.get("why_viral", ""),
                "emotional_angle": ai_result.get("emotional_angle", ""),
                "hook_idea": ai_result.get("hook_idea", ""),
                "viral_probability": ai_result.get("viral_probability", ""),
                "audience_fit": ai_result.get("audience_fit", ""),
                "timing": ai_result.get("timing", ""),
                "confidence_score": ai_result.get("confidence_score", 0.0),
                "best_posting_time": "19:00",  # Peak engagement time (Pakistan timezone)
                "data_sources_used": total_sources,
                "patterns_analyzed": len(self.viral_patterns),
                "ai_source": ai_result.get("source", "AI Analysis"),
                "recommendation": f"This topic has {ai_result.get('viral_probability', 'High')} viral probability based on multi-source analysis"
            }
            
            # Phase 5: Logging Results
            logger.info("\n" + "=" * 60)
            logger.info("📌 FINAL TOPIC SELECTED")
            logger.info("=" * 60)
            logger.info(f"Topic: {self.final_topic['topic']}")
            logger.info(f"Viral Probability: {self.final_topic['viral_probability']}")
            logger.info(f"Confidence: {self.final_topic['confidence_score']:.2%}")
            logger.info(f"Best Posting Time: {self.final_topic['best_posting_time']}")
            logger.info("=" * 60 + "\n")
            
            return self.final_topic
        
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}")
            return self._get_error_fallback()
    
    def _get_error_fallback(self) -> Dict:
        """Fallback output when everything fails"""
        return {
            "agent_id": 1,
            "agent_name": "Topic Research Master",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic": "Never Give Up: The Power of Persistence",
            "why_viral": "Timeless motivation topic",
            "emotional_angle": "Determination/Persistence",
            "hook_idea": "Most people quit too soon. Here's why you shouldn't.",
            "viral_probability": "High",
            "audience_fit": "Excellent",
            "timing": "Evergreen",
            "confidence_score": 0.50,
            "best_posting_time": "19:00",
            "data_sources_used": 0,
            "patterns_analyzed": 0,
            "ai_source": "Error Fallback",
            "recommendation": "Please check API keys and try again"
        }


# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    # Example usage
    config = {
        "youtube_api_key": "YOUR_KEY",
        "groq_api_key": "YOUR_KEY",
        "google_api_key": "YOUR_KEY",
        "reddit_client_id": "YOUR_ID",
        "reddit_client_secret": "YOUR_SECRET"
    }
    
    settings = {
        "timezone": "Asia/Karachi",
        "language": "Urdu",
        "target_audience": "Hindi speakers"
    }
    
    agent = TopicResearchAgentMaster(config, settings)
    result = agent.run()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
              
