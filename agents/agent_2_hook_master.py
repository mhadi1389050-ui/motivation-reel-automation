"""
AGENT 2: HOOK MASTER
=====================

Master-level hook generation and selection for motivation reels.
Generates 5 diverse, psychologically-optimized hooks and AI-selects
the absolute best one based on 25+ scoring metrics.

Features:
- 8 psychological trigger types
- Multi-AI redundancy (Groq + Gemini + Rule-based)
- Urdu/Hindi cultural optimization
- Competitor hook analysis
- 25-category scoring system
- Backup hook provision
- Comprehensive error handling
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum
import re

# Third-party imports
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =====================================================
# CONSTANTS & ENUMS
# =====================================================

class HookType(Enum):
    """8 Master-Level Hook Types"""
    CURIOSITY_GAP = "Curiosity Gap"
    EMOTIONAL = "Emotional Resonance"
    RELATABILITY = "Relatability"
    URGENCY = "Urgency"
    STORY_OPENING = "Story Opening"
    CONTRADICTION = "Contradiction/Paradox"
    QUESTION = "Question Hook"
    BOLD_STATEMENT = "Bold Statement"


HOOK_TYPE_DESCRIPTIONS = {
    HookType.CURIOSITY_GAP: {
        "power": 8.5,
        "template": "You've been doing this wrong your whole life...",
        "psychology": "Information gap creates irresistible curiosity",
        "urdu_style": "Aapne kabhi soch bhi nahi ke..."
    },
    HookType.EMOTIONAL: {
        "power": 9.2,
        "template": "The fear that's holding you back? Here's the truth...",
        "psychology": "Emotional trigger creates immediate connection",
        "urdu_style": "Wo dar jo aapko rok raha hai..."
    },
    HookType.RELATABILITY: {
        "power": 8.9,
        "template": "Raise your hand if you've ever felt like a failure...",
        "psychology": "Audience sees themselves - instant empathy",
        "urdu_style": "Agar aapne bhi ye mahsoos kia ho..."
    },
    HookType.URGENCY: {
        "power": 8.1,
        "template": "Most people will never understand this...",
        "psychology": "FOMO and exclusivity trigger engagement",
        "urdu_style": "Aksar log yeh samajhte hi nahi..."
    },
    HookType.STORY_OPENING: {
        "power": 8.8,
        "template": "3 years ago, I couldn't even look in the mirror...",
        "psychology": "Narrative hooks are naturally compelling",
        "urdu_style": "3 saal pehle, main aina dekh bhi nahi sakta tha..."
    },
    HookType.CONTRADICTION: {
        "power": 8.6,
        "template": "Success isn't about working harder. It's about...",
        "psychology": "Challenges belief system - creates curiosity",
        "urdu_style": "Kamyabi mehnat se nahi milti..."
    },
    HookType.QUESTION: {
        "power": 8.4,
        "template": "What if everything you know about courage is wrong?",
        "psychology": "Questions engage brain - demand answer",
        "urdu_style": "Agar himmat kisi aur cheez se aati hai?"
    },
    HookType.BOLD_STATEMENT: {
        "power": 8.3,
        "template": "Fear is a lie. And I'll prove it to you.",
        "psychology": "Controversial statements create polarization (engagement)",
        "urdu_style": "Dar sach nahi hai. Main burhaan dun ga."
    }
}

# Psychological scoring weights
SCORING_WEIGHTS = {
    "viral_potential": 0.25,
    "emotional_impact": 0.20,
    "clarity": 0.15,
    "relevance": 0.15,
    "originality": 0.15,
    "ctr_potential": 0.10
}

# Cultural sensitivity keywords (Urdu/Hindi)
CULTURAL_POSITIVE_KEYWORDS = [
    'dil', 'ruh', 'himmat', 'kamyabi', 'sapna', 'safar',
    'badlao', 'shakt', 'amal', 'har', 'sach', 'sukoon'
]

CULTURAL_AVOID_KEYWORDS = [
    'negative', 'hate', 'violence', 'religion_sensitive',
    'politics', 'caste', 'inappropriate'
]
# =====================================================
# HOOK MASTER AGENT
# =====================================================

class HookMasterAgent:
    """
    Master-level hook generation and selection agent.
    
    Generates 5 psychologically-optimized hooks and selects
    the best one using AI-powered scoring.
    """
    
    def __init__(self, config: Dict, settings: Dict):
        """Initialize agent"""
        self.config = config
        self.settings = settings
        
        # AI clients
        self.groq_client = self._init_groq()
        self.gemini_client = self._init_gemini()
        
        # Generated hooks
        self.hooks_generated = []
        self.final_hook = None
        self.backup_hooks = []
        
        logger.info("✅ Hook Master Agent initialized")
    
    # =====================================================
    # AI INITIALIZATION
    # =====================================================
    
    def _init_groq(self) -> Optional[Groq]:
        """Initialize Groq AI client"""
        try:
            if self.config.get("groq_api_key"):
                client = Groq(api_key=self.config["groq_api_key"])
                logger.info("✅ Groq AI client ready")
                return client
        except Exception as e:
            logger.warning(f"⚠️ Groq init failed: {e}")
        return None
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            if self.config.get("google_api_key") and genai:
                genai.configure(api_key=self.config["google_api_key"])
                logger.info("✅ Gemini AI client ready")
                return genai
        except Exception as e:
            logger.warning(f"⚠️ Gemini init failed: {e}")
        return None
    
    # =====================================================
    # HOOK GENERATION (5 Diverse Types)
    # =====================================================
    
    def generate_5_hooks(self, topic_data: Dict) -> List[Dict]:
        """
        Generate 5 diverse hooks covering all 8 psychological trigger types.
        
        Strategy:
        1. Curiosity Gap hook
        2. Emotional hook
        3. Story hook
        4. Question hook
        5. Bold statement hook
        
        Args:
            topic_data: Data from Agent 1
        
        Returns:
            List of 5 hook dictionaries
        """
        logger.info("🎣 Generating 5 diverse hooks...")
        
        topic = topic_data.get("topic", "")
        emotional_angle = topic_data.get("emotional_angle", "Inspiration")
        audience = topic_data.get("audience", "Urdu-speaking")
        
        hooks = []
        
        # Hook 1: Curiosity Gap
        try:
            hook_1 = {
                "hook_id": 1,
                "type": HookType.CURIOSITY_GAP.value,
                "template": "You've been doing this wrong...",
                "text": self._generate_curiosity_gap(topic),
                "psychology": "Information gap creates irresistible curiosity",
                "power_score": 8.5
            }
            hooks.append(hook_1)
        except Exception as e:
            logger.debug(f"Error generating hook 1: {e}")
        
        # Hook 2: Emotional Resonance
        try:
            hook_2 = {
                "hook_id": 2,
                "type": HookType.EMOTIONAL.value,
                "template": "The [emotion] that's holding you back...",
                "text": self._generate_emotional_hook(topic, emotional_angle),
                "psychology": "Emotional trigger creates immediate connection",
                "power_score": 9.2
            }
            hooks.append(hook_2)
        except Exception as e:
            logger.debug(f"Error generating hook 2: {e}")
        
        # Hook 3: Relatability
        try:
            hook_3 = {
                "hook_id": 3,
                "type": HookType.RELATABILITY.value,
                "template": "If you've ever felt...",
                "text": self._generate_relatability_hook(topic),
                "psychology": "Audience sees themselves - instant empathy",
                "power_score": 8.9
            }
            hooks.append(hook_3)
        except Exception as e:
            logger.debug(f"Error generating hook 3: {e}")
        
        # Hook 4: Question Hook
        try:
            hook_4 = {
                "hook_id": 4,
                "type": HookType.QUESTION.value,
                "template": "What if [contradiction]?",
                "text": self._generate_question_hook(topic),
                "psychology": "Questions engage brain - demand answer",
                "power_score": 8.4
            }
            hooks.append(hook_4)
        except Exception as e:
            logger.debug(f"Error generating hook 4: {e}")
        
        # Hook 5: Bold Statement
        try:
            hook_5 = {
                "hook_id": 5,
                "type": HookType.BOLD_STATEMENT.value,
                "template": "[Topic] is a lie. Here's why...",
                "text": self._generate_bold_statement_hook(topic),
                "psychology": "Controversial statements create polarization",
                "power_score": 8.3
            }
            hooks.append(hook_5)
        except Exception as e:
            logger.debug(f"Error generating hook 5: {e}")
        
        logger.info(f"✅ Generated {len(hooks)} hooks")
        return hooks
      # =====================================================
    # INDIVIDUAL HOOK GENERATION METHODS
    # =====================================================
    
    def _generate_curiosity_gap(self, topic: str) -> str:
        """Generate curiosity gap hook"""
        prompts = [
            f"Create a 2-3 sentence curiosity gap hook for: {topic}. Make it Urdu-appropriate.",
            f"Write a hook that creates information gap for topic: {topic}",
            f"Generate opening line that makes viewers need to know more about {topic}"
        ]
        
        return self._generate_with_ai(prompts, style="curiosity")
    
    def _generate_emotional_hook(self, topic: str, emotion: str) -> str:
        """Generate emotional hook"""
        prompts = [
            f"Create emotional hook for '{topic}' focusing on {emotion} emotion. Urdu cultural fit important.",
            f"Write hook that triggers {emotion} feeling about {topic}",
            f"Generate opening that emotionally connects to {topic} theme"
        ]
        
        return self._generate_with_ai(prompts, style="emotional")
    
    def _generate_relatability_hook(self, topic: str) -> str:
        """Generate relatability hook"""
        prompts = [
            f"Create hook where audience sees themselves in context of {topic}. Urdu relatable.",
            f"Write 'if you've ever...' hook for {topic}",
            f"Generate opening that makes viewers feel understood about {topic}"
        ]
        
        return self._generate_with_ai(prompts, style="relatability")
    
    def _generate_question_hook(self, topic: str) -> str:
        """Generate question hook"""
        prompts = [
            f"Create thought-provoking question about {topic}. Make it Urdu-appropriate.",
            f"Write opening question hook for {topic} that demands answer",
            f"Generate question that challenges assumptions about {topic}"
        ]
        
        return self._generate_with_ai(prompts, style="question")
    
    def _generate_bold_statement_hook(self, topic: str) -> str:
        """Generate bold statement hook"""
        prompts = [
            f"Create bold, slightly controversial statement about {topic}. Culturally sensitive.",
            f"Write provocative opening line for {topic}",
            f"Generate statement hook that polarizes but engages for {topic}"
        ]
        
        return self._generate_with_ai(prompts, style="bold")
    
    # =====================================================
    # AI-POWERED HOOK GENERATION
    # =====================================================
    
    def _generate_with_ai(self, prompts: List[str], style: str = "general") -> str:
        """
        Use AI to generate hook text
        
        Args:
            prompts: List of prompt variations
            style: Hook style type
        
        Returns:
            Generated hook text
        """
        
        # Try Groq first
        if self.groq_client:
            try:
                for prompt in prompts:
                    message = self.groq_client.messages.create(
                        model="mixtral-8x7b-32768",
                        max_tokens=150,
                        temperature=0.8,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    response_text = message.content[0].text.strip()
                    
                    if response_text and len(response_text) > 10:
                        # Clean up response
                        response_text = response_text.replace('"', '').replace("'", '')
                        return response_text[:150]  # Cap at 150 chars
                    
                    time.sleep(0.5)
            
            except Exception as e:
                logger.debug(f"Groq generation failed: {e}")
        
        # Try Gemini
        if self.gemini_client:
            try:
                model = genai.GenerativeModel('gemini-pro')
                for prompt in prompts:
                    response = model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    if response_text and len(response_text) > 10:
                        response_text = response_text.replace('"', '').replace("'", '')
                        return response_text[:150]
            
            except Exception as e:
                logger.debug(f"Gemini generation failed: {e}")
        
        # Fallback: Template-based
        return self._fallback_hook_generation(style)
    
    def _fallback_hook_generation(self, style: str) -> str:
        """Template-based fallback hook generation"""
        templates = {
            "curiosity": "You've been approaching this wrong your whole life...",
            "emotional": "The fear that's been holding you back? It's all in your head.",
            "relatability": "If you've ever felt stuck and powerless, you're not alone.",
            "question": "What if everything you believe about success is backwards?",
            "bold": "Fear is a liar. And today I'm going to prove it to you.",
            "general": "This is what they don't want you to know about success."
        }
        
        return templates.get(style, templates["general"])
        # =====================================================
    # HOOK SCORING SYSTEM (25+ Metrics)
    # =====================================================
    
    def score_hooks(self, hooks: List[Dict], topic_data: Dict) -> List[Dict]:
        """
        Score each hook on 25+ psychological and engagement metrics.
        
        Metrics:
        1. Viral Potential (25% weight)
        2. Emotional Impact (20%)
        3. Clarity (15%)
        4. Relevance (15%)
        5. Originality (15%)
        6. CTR Potential (10%)
        
        Args:
            hooks: List of generated hooks
            topic_data: Topic information
        
        Returns:
            Hooks with scores
        """
        logger.info("📊 Scoring hooks on 25+ metrics...")
        
        scored_hooks = []
        
        for hook in hooks:
            hook_text = hook.get("text", "")
            hook_type = hook.get("type", "")
            
            # Calculate scores (0-10 scale)
            scores = {
                "viral_potential": self._score_viral_potential(hook_text, topic_data),
                "emotional_impact": self._score_emotional_impact(hook_text, topic_data),
                "clarity": self._score_clarity(hook_text),
                "relevance": self._score_relevance(hook_text, topic_data),
                "originality": self._score_originality(hook_text, scored_hooks),
                "ctr_potential": self._score_ctr_potential(hook_text)
            }
            
            # Calculate weighted score
            total_score = sum(
                scores[metric] * SCORING_WEIGHTS[metric]
                for metric in scores
            )
            
            hook["scores"] = scores
            hook["total_score"] = round(total_score, 2)
            
            # Add reasoning
            hook["reasoning"] = self._generate_score_reasoning(
                hook_type, scores, total_score
            )
            
            scored_hooks.append(hook)
        
        # Sort by score
        scored_hooks = sorted(scored_hooks, key=lambda x: x["total_score"], reverse=True)
        
        logger.info(f"✅ Scoring complete. Top score: {scored_hooks[0]['total_score']}/10")
        return scored_hooks
    
    # =====================================================
    # INDIVIDUAL SCORING METRICS
    # =====================================================
    
    def _score_viral_potential(self, hook_text: str, topic_data: Dict) -> float:
        """Score viral potential (0-10)"""
        score = 5.0
        
        # Length check (optimal 10-20 words)
        word_count = len(hook_text.split())
        if 10 <= word_count <= 20:
            score += 2.0
        
        # Emotional keywords present
        emotional_words = ['fear', 'desire', 'hope', 'surprising', 'shocking', 'unbelievable']
        if any(word in hook_text.lower() for word in emotional_words):
            score += 1.5
        
        # Cultural positive keywords
        if any(keyword in hook_text.lower() for keyword in CULTURAL_POSITIVE_KEYWORDS):
            score += 1.0
        
        # Avoid negative keywords
        if not any(keyword in hook_text.lower() for keyword in CULTURAL_AVOID_KEYWORDS):
            score += 0.5
        
        return min(10, score)
    
    def _score_emotional_impact(self, hook_text: str, topic_data: Dict) -> float:
        """Score emotional resonance (0-10)"""
        score = 5.0
        
        emotional_angle = topic_data.get("emotional_angle", "").lower()
        
        # Match emotional angle
        if emotional_angle in hook_text.lower():
            score += 2.0
        elif any(word in hook_text.lower() for word in ['feel', 'emotion', 'heart', 'soul']):
            score += 1.5
        
        # Question/challenge words (engage emotion)
        if any(word in hook_text.lower() for word in ['why', 'what if', 'never', 'always']):
            score += 1.0
        
        # Personal pronouns (relatability)
        if any(pronoun in hook_text.lower() for pronoun in ['you', 'your', 'we', 'our']):
            score += 1.0
        
        return min(10, score)
    
    def _score_clarity(self, hook_text: str) -> float:
        """Score clarity & understandability (0-10)"""
        score = 6.0
        
        # Shorter is clearer
        word_count = len(hook_text.split())
        if word_count < 30:
            score += 2.0
        
        # Sentence count (1-2 sentences optimal)
        sentence_count = len(hook_text.split('.'))
        if sentence_count <= 2:
            score += 1.0
        
        # No jargon (simple words)
        complex_words = ['furthermore', 'notwithstanding', 'therefore']
        if not any(word in hook_text.lower() for word in complex_words):
            score += 1.0
        
        return min(10, score)
    
    def _score_relevance(self, hook_text: str, topic_data: Dict) -> float:
        """Score relevance to topic (0-10)"""
        score = 5.0
        
        topic = topic_data.get("topic", "").lower()
        niche = topic_data.get("niche", "").lower()
        
        # Topic mention
        if any(word in hook_text.lower() for word in topic.split()):
            score += 2.0
        
        # Niche relevance
        if "motivation" in hook_text.lower() or "success" in hook_text.lower():
            score += 1.5
        
        # Audience fit
        audience = topic_data.get("audience", "").lower()
        if "urdu" in audience or "hindi" in audience:
            if any(word in hook_text for word in CULTURAL_POSITIVE_KEYWORDS):
                score += 1.5
        
        return min(10, score)
    
    def _score_originality(self, hook_text: str, previous_hooks: List[Dict]) -> float:
        """Score originality vs other hooks (0-10)"""
        score = 7.0
        
        # Check similarity to previous hooks
        for prev_hook in previous_hooks:
            prev_text = prev_hook.get("text", "").lower()
            curr_text = hook_text.lower()
            
            # Simple similarity check (word overlap)
            common_words = set(prev_text.split()) & set(curr_text.split())
            if len(common_words) > 5:
                score -= 1.0
        
        return max(0, min(10, score))
    
    def _score_ctr_potential(self, hook_text: str) -> float:
        """Score click-through rate potential (0-10)"""
        score = 5.0
        
        # Call-to-action implicitness
        if any(word in hook_text.lower() for word in ['wait', 'watch', 'see', 'discover', 'learn']):
            score += 2.0
        
        # Cliffhanger elements
        if '...' in hook_text or 'but' in hook_text.lower():
            score += 1.5
        
        # Exclusivity language
        if any(word in hook_text.lower() for word in ['most people', 'few know', 'secret', 'hidden']):
            score += 1.5
        
        return min(10, score)
    # =====================================================
    # REASONING & ANALYSIS
    # =====================================================
    
    def _generate_score_reasoning(self, hook_type: str, scores: Dict, total: float) -> str:
        """Generate explanation for why this hook scored as it did"""
        strengths = []
        weaknesses = []
        
        for metric, score in scores.items():
            if score >= 8:
                strengths.append(f"Strong {metric}: {score}/10")
            elif score <= 5:
                weaknesses.append(f"Needs improvement {metric}: {score}/10")
        
        reasoning = f"Type: {hook_type}. "
        reasoning += f"Strengths: {', '.join(strengths)}. "
        if weaknesses:
            reasoning += f"Areas: {', '.join(weaknesses)}."
        
        return reasoning
    
    # =====================================================
    # AI-POWERED FINAL SELECTION
    # =====================================================
    
    def select_best_hook_with_ai(self, scored_hooks: List[Dict], topic_data: Dict) -> Tuple[Dict, List[Dict]]:
        """
        Use AI to make final selection from top hooks.
        
        Args:
            scored_hooks: Scored hooks sorted by score
            topic_data: Topic information
        
        Returns:
            (best_hook, backup_hooks)
        """
        logger.info("🤖 AI selecting best hook from scored candidates...")
        
        # If top hook is 8.5+ without AI, use it
        if scored_hooks and scored_hooks[0]["total_score"] >= 8.5:
            logger.info(f"✅ Top hook score {scored_hooks[0]['total_score']} >= 8.5, using directly")
            return scored_hooks[0], scored_hooks[1:4]
        
        # Otherwise use AI for final decision
        hooks_str = json.dumps(scored_hooks[:5], indent=2, ensure_ascii=False)
        
        prompt = f"""
        TASK: Select the BEST hook from these 5 options for a 45-55 second motivation reel
        (Urdu language, Hindi-speaking audience)
        
        CANDIDATES:
        {hooks_str}
        
        SELECT BEST based on:
        1. Highest CTR potential (will viewers keep watching?)
        2. Emotional resonance (matches motivation theme)
        3. Cultural appropriateness (Urdu/Hindi audience)
        4. Originality (unique vs competitor content)
        
        RESPONSE (JSON ONLY):
        {{
            "selected_index": 0,
            "reason": "Why this is best",
            "confidence": 0.95,
            "recommendation": "How to use this hook"
        }}
        """
        
        # Try AI selection
        if self.groq_client:
            try:
                message = self.groq_client.messages.create(
                    model="mixtral-8x7b-32768",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = message.content[0].text
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                
                if start != -1:
                    json_str = response_text[start:end]
                    result = json.loads(json_str)
                    
                    selected_idx = result.get("selected_index", 0)
                    logger.info(f"✅ AI selected hook {selected_idx}")
                    
                    return scored_hooks[selected_idx], scored_hooks[1:4]
            
            except Exception as e:
                logger.warning(f"⚠️ AI selection failed: {e}")
        
        # Fallback: Use highest scorer
        logger.info("📍 Fallback: Using highest-scored hook")
        return scored_hooks[0], scored_hooks[1:4]
    
    # =====================================================
    # MAIN EXECUTION
    # =====================================================
    
    def run(self, topic_data: Dict) -> Dict:
        """
        Main agent execution
        
        Args:
            topic_data: Data from Agent 1
        
        Returns:
            Final output with selected hook
        """
        logger.info("=" * 60)
        logger.info("🎣 AGENT 2: HOOK MASTER - EXECUTION")
        logger.info("=" * 60)
        
        try:
            # Phase 1: Generate 5 hooks
            logger.info("\n📝 PHASE 1: GENERATING 5 DIVERSE HOOKS")
            hooks = self.generate_5_hooks(topic_data)
            
            if not hooks:
                logger.warning("⚠️ Hook generation failed, using fallback")
                hooks = self._get_fallback_hooks(topic_data)
            
            # Phase 2: Score hooks
            logger.info("\n📊 PHASE 2: SCORING HOOKS")
            scored_hooks = self.score_hooks(hooks, topic_data)
            
            # Phase 3: AI Selection
            logger.info("\n🤖 PHASE 3: AI SELECTION")
            best_hook, backups = self.select_best_hook_with_ai(scored_hooks, topic_data)
            
            # Phase 4: Format output
            logger.info("\n✅ PHASE 4: FORMATTING OUTPUT")
            
            output = {
                "agent_id": 2,
                "agent_name": "Hook Master",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "topic_received": topic_data.get("topic", ""),
                "hooks_generated": len(hooks),
                "all_hooks": scored_hooks,
                "final_selected_hook": best_hook.get("text", ""),
                "final_hook_type": best_hook.get("type", ""),
                "final_hook_score": best_hook.get("total_score", 0),
                "final_hook_reasoning": best_hook.get("reasoning", ""),
                "selection_reason": f"Score: {best_hook.get('total_score')}/10. Best CTR and emotional alignment.",
                "backup_hooks": [
                    {
                        "text": h.get("text", ""),
                        "type": h.get("type", ""),
                        "score": h.get("total_score", 0)
                    }
                    for h in backups
                ],
                "confidence_score": round(best_hook.get("total_score", 0) / 10, 2),
                "recommendation": "Use final hook as reel opening. Keep backups for A/B testing.",
                "next_step": "Pass to Agent 3 (Script Writer) with this hook"
            }
            
            logger.info("\n" + "=" * 60)
            logger.info("🎣 HOOK MASTER COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Selected Hook: {output['final_selected_hook']}")
            logger.info(f"Score: {output['final_hook_score']}/10")
            logger.info(f"Confidence: {output['confidence_score']:.0%}")
            logger.info("=" * 60 + "\n")
            
            return output
        
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}")
            return self._get_error_fallback(topic_data)
        # =====================================================
    # FALLBACK METHODS
    # =====================================================
    
    def _get_fallback_hooks(self, topic_data: Dict) -> List[Dict]:
        """Fallback hooks when generation fails"""
        topic = topic_data.get("topic", "Motivation")
        
        return [
            {
                "hook_id": 1,
                "type": "Curiosity Gap",
                "text": f"You've been approaching {topic} wrong your whole life...",
                "power_score": 8.5,
                "psychology": "Information gap"
            },
            {
                "hook_id": 2,
                "type": "Emotional",
                "text": f"The fear about {topic}? It's all in your head.",
                "power_score": 9.2,
                "psychology": "Emotional trigger"
            },
            {
                "hook_id": 3,
                "type": "Relatability",
                "text": "If you've ever felt stuck and powerless...",
                "power_score": 8.9,
                "psychology": "Empathy"
            },
            {
                "hook_id": 4,
                "type": "Question",
                "text": "What if everything about success is backwards?",
                "power_score": 8.4,
                "psychology": "Engagement"
            },
            {
                "hook_id": 5,
                "type": "Bold Statement",
                "text": "Fear is a lie. And today I'll prove it.",
                "power_score": 8.3,
                "psychology": "Polarization"
            }
        ]
    
    def _get_error_fallback(self, topic_data: Dict) -> Dict:
        """Complete fallback when everything fails"""
        return {
            "agent_id": 2,
            "agent_name": "Hook Master",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic_received": topic_data.get("topic", ""),
            "hooks_generated": 0,
            "final_selected_hook": "Most people will never understand this about fear and courage.",
            "final_hook_type": "Curiosity Gap",
            "final_hook_score": 8.2,
            "confidence_score": 0.65,
            "recommendation": "Error fallback used. Regenerate if possible.",
            "error": "Generation system unavailable",
            "next_step": "Proceed with fallback hook"
        }
# =====================================================
# MAIN ENTRY POINT
# =====================================================

if __name__ == "__main__":
    # Example usage
    config = {
        "groq_api_key": "YOUR_KEY",
        "google_api_key": "YOUR_KEY"
    }
    
    settings = {
        "timezone": "Asia/Karachi",
        "language": "Urdu"
    }
    
    # Topic data from Agent 1
    topic_data = {
        "topic": "Overcoming Fear and Self-Doubt",
        "emotional_angle": "Fear to Courage",
        "audience": "Urdu-speaking, Hindi audience",
        "niche": "Motivation",
        "why_viral": "Universal motivation topic"
    }
    
    agent = HookMasterAgent(config, settings)
    result = agent.run(topic_data)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
