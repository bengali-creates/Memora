"""
Mood Detection Service for NetworkMemory

Analyzes conversation mood and emotional indicators from transcripts.
Uses pretrained models for hackathon, supports custom model training later.
"""

from typing import Dict, List, Optional
import re


class MoodAnalyzer:
    """
    Analyzes mood and emotional indicators from conversation transcripts

    Architecture:
    - Phase 1 (Hackathon): Use rule-based + sentiment keywords
    - Phase 2 (Production): Integrate HuggingFace pretrained models
    - Phase 3 (Custom): Train custom model on networking conversations
    """

    def __init__(self, use_pretrained: bool = False):
        """
        Initialize mood analyzer

        Args:
            use_pretrained: Whether to load pretrained models (slower but more accurate)
        """
        self.use_pretrained = use_pretrained
        self.model = None
        self.emotion_model = None

        # Phase 1: Keyword-based approach (fast, good enough for demo)
        self.mood_keywords = {
            "enthusiastic": [
                "amazing", "awesome", "fantastic", "love", "definitely",
                "excited", "can't wait", "brilliant", "incredible"
            ],
            "excited": [
                "wow", "omg", "really", "yes!", "absolutely",
                "so cool", "that's great", "perfect"
            ],
            "professional": [
                "indeed", "certainly", "absolutely", "understand",
                "appreciate", "regarding", "consider"
            ],
            "friendly": [
                "haha", "lol", "nice", "cool", "sounds good",
                "for sure", "totally", "yeah"
            ],
            "neutral": [
                "okay", "alright", "sure", "thanks", "yes", "no"
            ],
            "reserved": [
                "maybe", "perhaps", "I suppose", "not sure",
                "I'll think about it", "possibly"
            ],
            "cold": [
                "busy", "later", "can't", "no time", "sorry",
                "have to go", "running late"
            ],
            "stressed": [
                "overwhelmed", "rushed", "quickly", "no time",
                "deadline", "urgent", "pressure"
            ]
        }

        self.excited_words = [
            "amazing", "awesome", "fantastic", "love", "excited",
            "definitely", "brilliant", "incredible", "wonderful",
            "perfect", "excellent", "great"
        ]

        self.hesitation_words = [
            "um", "uh", "hmm", "well", "like", "you know",
            "maybe", "perhaps", "not sure", "I guess"
        ]

        self.agreement_phrases = [
            "totally agree", "exactly", "for sure", "absolutely",
            "you're right", "that makes sense", "I agree",
            "couldn't agree more", "same here"
        ]

        # Load pretrained models if requested (Phase 2)
        if use_pretrained:
            self._load_pretrained_models()

    def _load_pretrained_models(self):
        """Load HuggingFace pretrained models for emotion detection"""
        try:
            from transformers import pipeline

            print("[INIT] Loading pretrained mood detection models...")

            # Sentiment analysis
            self.model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )

            # Emotion detection
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )

            print("[OK] Pretrained models loaded successfully")

        except Exception as e:
            print(f"[WARNING] Could not load pretrained models: {e}")
            print("[INFO] Falling back to keyword-based approach")
            self.use_pretrained = False

    def analyze_conversation(
        self,
        transcript: str,
        speaker_labels: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Analyze mood from full conversation transcript

        Args:
            transcript: Full conversation text
            speaker_labels: Optional dict mapping speaker names to roles
                           e.g. {"You": "self", "Sarah": "contact"}

        Returns:
            dict with mood analysis including:
            - contact_mood, your_mood
            - conversation_energy
            - sentiment_score
            - emotional_indicators
            - engagement metrics
        """

        # Split transcript by speaker if possible
        your_lines, contact_lines = self._split_by_speaker(transcript, speaker_labels)

        # Analyze both speakers
        contact_analysis = self._analyze_speaker(contact_lines, "contact")
        your_analysis = self._analyze_speaker(your_lines, "you")

        # Calculate conversation-level metrics
        energy = self._calculate_energy(transcript)
        sentiment = self._calculate_sentiment(transcript)
        emotional_indicators = self._extract_emotional_indicators(transcript)

        # Calculate engagement
        engagement = self._calculate_engagement(
            transcript, your_lines, contact_lines
        )

        return {
            "contact_mood": contact_analysis["mood"],
            "contact_mood_confidence": contact_analysis["confidence"],
            "your_mood": your_analysis["mood"],
            "your_mood_confidence": your_analysis["confidence"],
            "conversation_energy": energy["level"],
            "energy_score": energy["score"],
            "sentiment_score": sentiment,
            "emotional_indicators": emotional_indicators,
            "engagement": engagement,
            "follow_up_likelihood": self._predict_followup(
                contact_analysis, sentiment, engagement
            )
        }

    def _split_by_speaker(
        self,
        transcript: str,
        speaker_labels: Optional[Dict[str, str]] = None
    ) -> tuple:
        """Split transcript into your lines vs contact's lines"""

        your_lines = []
        contact_lines = []

        lines = transcript.split("\n")
        for line in lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                speaker = speaker.strip()
                text = text.strip()

                if speaker_labels:
                    role = speaker_labels.get(speaker, "unknown")
                    if role == "self":
                        your_lines.append(text)
                    elif role == "contact":
                        contact_lines.append(text)
                else:
                    # Assume first speaker is you
                    if "You" in speaker or speaker == lines[0].split(":")[0].strip():
                        your_lines.append(text)
                    else:
                        contact_lines.append(text)

        return your_lines, contact_lines

    def _analyze_speaker(self, lines: List[str], speaker_type: str) -> Dict:
        """Analyze mood for a single speaker"""

        if not lines:
            return {"mood": "neutral", "confidence": 0.5}

        text = " ".join(lines).lower()

        if self.use_pretrained and self.emotion_model:
            # Use pretrained model
            return self._analyze_with_model(text)
        else:
            # Use keyword-based approach
            return self._analyze_with_keywords(text)

    def _analyze_with_keywords(self, text: str) -> Dict:
        """Keyword-based mood detection (fast, decent accuracy)"""

        mood_scores = {}

        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for word in keywords if word.lower() in text.lower())
            mood_scores[mood] = score

        # Get top mood
        if max(mood_scores.values()) == 0:
            return {"mood": "neutral", "confidence": 0.5}

        top_mood = max(mood_scores, key=mood_scores.get)
        max_score = mood_scores[top_mood]
        total_matches = sum(mood_scores.values())

        confidence = min(0.95, 0.6 + (max_score / (total_matches + 1)) * 0.35)

        return {
            "mood": top_mood,
            "confidence": round(confidence, 2)
        }

    def _analyze_with_model(self, text: str) -> Dict:
        """Model-based mood detection (slower, more accurate)"""

        try:
            # Get emotion predictions
            results = self.emotion_model(text[:512])  # Limit text length

            # Get top emotion
            top_emotion = max(results[0], key=lambda x: x['score'])

            # Map emotion to our mood categories
            emotion_to_mood = {
                "joy": "enthusiastic",
                "surprise": "excited",
                "neutral": "neutral",
                "fear": "reserved",
                "sadness": "cold",
                "anger": "stressed",
                "disgust": "cold"
            }

            mood = emotion_to_mood.get(
                top_emotion['label'].lower(),
                "neutral"
            )

            return {
                "mood": mood,
                "confidence": round(top_emotion['score'], 2)
            }

        except Exception as e:
            print(f"[WARNING] Model inference failed: {e}")
            return self._analyze_with_keywords(text)

    def _calculate_energy(self, transcript: str) -> Dict:
        """Calculate conversation energy level"""

        text = transcript.lower()

        # Energy indicators
        exclamation_count = text.count("!")
        question_count = text.count("?")
        caps_count = sum(1 for c in transcript if c.isupper())

        # Check for high-energy words
        high_energy_words = [
            "wow", "amazing", "awesome", "definitely", "excited",
            "love", "great", "fantastic"
        ]
        energy_word_count = sum(
            1 for word in high_energy_words if word in text
        )

        # Calculate score
        score = min(1.0, (
            exclamation_count * 0.1 +
            energy_word_count * 0.15 +
            (caps_count / len(transcript)) * 2
        ))

        # Determine level
        if score >= 0.6:
            level = "high"
        elif score >= 0.3:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "score": round(score, 2)
        }

    def _calculate_sentiment(self, transcript: str) -> float:
        """Calculate overall sentiment score (-1 to +1)"""

        if self.use_pretrained and self.model:
            try:
                result = self.model(transcript[:512])
                label = result[0]['label']
                score = result[0]['score']

                # Convert to -1 to +1 scale
                if label == "POSITIVE":
                    return round(score, 2)
                else:
                    return round(-score, 2)

            except Exception as e:
                print(f"[WARNING] Sentiment analysis failed: {e}")

        # Fallback: keyword-based sentiment
        positive_words = [
            "great", "good", "excellent", "love", "happy",
            "amazing", "wonderful", "fantastic", "awesome"
        ]
        negative_words = [
            "bad", "terrible", "hate", "awful", "worst",
            "disappointed", "frustrating", "annoying"
        ]

        text = transcript.lower()
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        sentiment = (pos_count - neg_count) / total
        return round(sentiment, 2)

    def _extract_emotional_indicators(self, transcript: str) -> Dict:
        """Extract emotional indicators from text"""

        text = transcript.lower()

        found_excited = [
            word for word in self.excited_words
            if word in text
        ]

        found_hesitation = [
            word for word in self.hesitation_words
            if word in text
        ]

        found_agreement = [
            phrase for phrase in self.agreement_phrases
            if phrase in text
        ]

        return {
            "excited_words": list(set(found_excited))[:5],
            "hesitation_words": list(set(found_hesitation))[:5],
            "agreement_phrases": list(set(found_agreement))[:5]
        }

    def _calculate_engagement(
        self,
        transcript: str,
        your_lines: List[str],
        contact_lines: List[str]
    ) -> Dict:
        """Calculate engagement levels for both parties"""

        # Count exchanges
        your_word_count = sum(len(line.split()) for line in your_lines)
        contact_word_count = sum(len(line.split()) for line in contact_lines)

        # Calculate engagement (longer responses = more engaged)
        if len(your_lines) > 0:
            your_avg = your_word_count / len(your_lines)
            your_engagement = min(100, int(your_avg * 5))
        else:
            your_engagement = 50

        if len(contact_lines) > 0:
            contact_avg = contact_word_count / len(contact_lines)
            contact_engagement = min(100, int(contact_avg * 5))
        else:
            contact_engagement = 50

        return {
            "contact_engagement": contact_engagement,
            "your_engagement": your_engagement
        }

    def _predict_followup(
        self,
        contact_analysis: Dict,
        sentiment: float,
        engagement: Dict
    ) -> Dict:
        """Predict likelihood of successful follow-up"""

        # Positive indicators
        will_followup = (
            sentiment > 0.3 and
            engagement["contact_engagement"] > 50 and
            contact_analysis["mood"] in ["enthusiastic", "excited", "friendly", "professional"]
        )

        # Calculate confidence
        confidence = (
            (sentiment + 1) / 2 * 0.3 +  # Sentiment contribution
            engagement["contact_engagement"] / 100 * 0.4 +  # Engagement contribution
            contact_analysis["confidence"] * 0.3  # Mood confidence contribution
        )

        # Determine reason
        if will_followup:
            reason = f"Contact seems {contact_analysis['mood']} with high engagement"
        else:
            if sentiment < 0:
                reason = "Conversation had negative sentiment"
            elif engagement["contact_engagement"] < 50:
                reason = "Contact showed low engagement"
            else:
                reason = f"Contact seems {contact_analysis['mood']} - may need time"

        return {
            "will_followup": will_followup,
            "confidence": round(confidence, 2),
            "reason": reason
        }


# Global instance (lazy loaded)
_mood_analyzer = None


def get_mood_analyzer(use_pretrained: bool = False) -> MoodAnalyzer:
    """Get or create mood analyzer instance"""
    global _mood_analyzer

    if _mood_analyzer is None:
        _mood_analyzer = MoodAnalyzer(use_pretrained=use_pretrained)

    return _mood_analyzer
