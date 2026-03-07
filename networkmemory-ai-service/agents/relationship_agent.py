"""
Relationship Health Agent

This agent analyzes and tracks the health of professional relationships.
Monitors interaction patterns and suggests relationship maintenance activities.

Capabilities:
1. Calculate relationship strength score
2. Detect relationships needing attention
3. Track interaction frequency
4. Suggest relationship maintenance activities
5. Predict relationship decay
6. Celebrate relationship milestones
"""

from crewai import Agent, Task
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


def create_relationship_analyst() -> Agent:
    """
    Create relationship health analysis agent

    This agent specializes in understanding relationship dynamics
    and suggesting ways to maintain and strengthen connections.

    Returns:
        Agent configured for relationship analysis
    """
    return Agent(
        role='Professional Relationship Health Analyst',
        goal='Analyze relationship health and suggest activities to maintain and strengthen professional connections',
        backstory="""You are an expert at understanding professional relationship dynamics.
        You can identify when relationships are thriving, stagnating, or at risk of fading.
        You understand the importance of regular touch-points, mutual value creation, and
        authentic engagement. You help people maintain meaningful relationships that
        benefit both parties over the long term.""",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )


class RelationshipHealthAnalyzer:
    """
    Analyzer for professional relationship health

    Tracks interactions and calculates relationship health scores
    """

    @staticmethod
    def calculate_relationship_health(contact_data: Dict, interaction_history: List[Dict] = None) -> Dict:
        """
        Calculate comprehensive relationship health score

        Factors considered:
        1. Recency of last interaction
        2. Frequency of interactions
        3. Quality of interactions (depth, topics)
        4. Mutual value exchange
        5. Relationship age
        6. Engagement level

        Args:
            contact_data: Contact information
            interaction_history: List of past interactions

        Returns:
            Relationship health analysis
        """
        if not interaction_history:
            interaction_history = []

        # Calculate component scores
        recency_score = calculate_recency_score(contact_data, interaction_history)
        frequency_score = calculate_frequency_score(interaction_history)
        quality_score = calculate_quality_score(contact_data, interaction_history)
        engagement_score = calculate_engagement_score(contact_data)
        age_score = calculate_relationship_age_score(contact_data)

        # Weighted overall health score
        health_score = (
            recency_score * 0.30 +      # 30% - Recent interaction is critical
            frequency_score * 0.25 +     # 25% - Regular touch-points matter
            quality_score * 0.25 +       # 25% - Quality over quantity
            engagement_score * 0.15 +    # 15% - Mutual engagement
            age_score * 0.05            # 5% - Relationship maturity
        )

        # Determine health status
        health_status = determine_health_status(health_score)

        # Generate insights and recommendations
        insights = generate_health_insights(
            health_score, recency_score, frequency_score,
            quality_score, engagement_score
        )

        recommendations = generate_maintenance_recommendations(
            contact_data, health_status, health_score,
            recency_score, frequency_score
        )

        return {
            'health_score': round(health_score, 2),
            'health_status': health_status,
            'component_scores': {
                'recency': round(recency_score, 2),
                'frequency': round(frequency_score, 2),
                'quality': round(quality_score, 2),
                'engagement': round(engagement_score, 2),
                'age': round(age_score, 2)
            },
            'insights': insights,
            'recommendations': recommendations,
            'risk_level': calculate_risk_level(health_score, recency_score),
            'next_touchpoint': suggest_next_touchpoint(contact_data, health_score),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    def batch_analyze_relationships(contacts: List[Dict]) -> Dict:
        """
        Analyze relationship health for multiple contacts

        Args:
            contacts: List of contacts to analyze

        Returns:
            Batch analysis with priorities
        """
        analyses = []

        for contact in contacts:
            analysis = RelationshipHealthAnalyzer.calculate_relationship_health(contact)
            analyses.append({
                'contact_name': contact.get('name'),
                'contact_id': contact.get('id'),
                **analysis
            })

        # Sort by risk level (highest risk first)
        analyses.sort(key=lambda x: (
            0 if x['risk_level'] == 'high' else 1 if x['risk_level'] == 'medium' else 2,
            -x['health_score']
        ))

        # Generate overall insights
        overall_insights = generate_overall_relationship_insights(analyses)

        return {
            'total_contacts': len(contacts),
            'relationship_analyses': analyses,
            'priority_contacts': analyses[:5],  # Top 5 needing attention
            'overall_insights': overall_insights,
            'analyzed_at': datetime.utcnow().isoformat()
        }


def calculate_recency_score(contact_data: Dict, interaction_history: List[Dict]) -> float:
    """Calculate score based on recency of last interaction"""
    met_date_str = contact_data.get('met_date')

    if not met_date_str:
        # If no date, assume recent (for new contacts)
        return 90.0

    try:
        met_date = datetime.fromisoformat(met_date_str.replace('Z', '+00:00'))
    except:
        # Fallback: try just the date part
        try:
            met_date = datetime.strptime(met_date_str.split('T')[0], '%Y-%m-%d')
        except:
            return 50.0  # Unknown, assume medium

    days_since = (datetime.now() - met_date.replace(tzinfo=None)).days

    # Scoring logic
    if days_since <= 7:
        return 100.0
    elif days_since <= 14:
        return 90.0
    elif days_since <= 30:
        return 75.0
    elif days_since <= 60:
        return 55.0
    elif days_since <= 90:
        return 35.0
    else:
        return max(10.0, 100.0 - (days_since * 0.5))


def calculate_frequency_score(interaction_history: List[Dict]) -> float:
    """Calculate score based on interaction frequency"""
    if not interaction_history:
        return 50.0  # Neutral for new relationships

    # Count interactions in last 90 days
    recent_interactions = len(interaction_history)

    if recent_interactions >= 10:
        return 100.0
    elif recent_interactions >= 5:
        return 80.0
    elif recent_interactions >= 3:
        return 60.0
    elif recent_interactions >= 1:
        return 40.0
    else:
        return 20.0


def calculate_quality_score(contact_data: Dict, interaction_history: List[Dict]) -> float:
    """Calculate score based on interaction quality"""
    topics = contact_data.get('topics_discussed', [])
    action_items = contact_data.get('follow_ups', [])

    score = 50.0  # Base score

    # More topics = deeper conversation
    score += min(len(topics) * 10, 30)

    # Action items indicate engagement
    score += min(len(action_items) * 10, 20)

    return min(score, 100.0)


def calculate_engagement_score(contact_data: Dict) -> float:
    """Calculate score based on mutual engagement"""
    # Check for mutual engagement indicators
    score = 50.0

    # LinkedIn connection
    if contact_data.get('linkedin_profile', {}).get('found'):
        score += 20

    # Action items suggest mutual interest
    if contact_data.get('follow_ups'):
        score += 20

    # High priority indicates value
    priority = contact_data.get('priority_score', 50)
    if priority >= 80:
        score += 10

    return min(score, 100.0)


def calculate_relationship_age_score(contact_data: Dict) -> float:
    """Calculate score based on relationship age"""
    # Newer relationships get boost (easier to maintain momentum)
    # Older relationships are valuable but may naturally have lower frequency

    met_date_str = contact_data.get('met_date')
    if not met_date_str:
        return 80.0  # New relationship

    try:
        met_date = datetime.fromisoformat(met_date_str.replace('Z', '+00:00'))
        days_old = (datetime.now() - met_date.replace(tzinfo=None)).days

        if days_old <= 30:
            return 100.0  # Very new
        elif days_old <= 90:
            return 90.0   # New
        elif days_old <= 180:
            return 80.0   # Established
        else:
            return 70.0   # Mature
    except:
        return 75.0


def determine_health_status(health_score: float) -> str:
    """Determine health status from score"""
    if health_score >= 80:
        return 'thriving'
    elif health_score >= 60:
        return 'healthy'
    elif health_score >= 40:
        return 'at_risk'
    else:
        return 'declining'


def generate_health_insights(health_score: float, recency: float, frequency: float,
                             quality: float, engagement: float) -> List[str]:
    """Generate human-readable insights"""
    insights = []

    if health_score >= 80:
        insights.append("This relationship is thriving - keep up the great work!")

    if recency < 50:
        insights.append("It's been a while since you last connected - time for a check-in")

    if frequency < 40:
        insights.append("Interaction frequency is low - consider more regular touch-points")

    if quality >= 75:
        insights.append("You've had deep, meaningful conversations")

    if engagement >= 80:
        insights.append("Strong mutual engagement - this person values the relationship")

    if health_score < 40:
        insights.append("This relationship needs immediate attention to prevent it from fading")

    return insights


def generate_maintenance_recommendations(contact_data: Dict, health_status: str,
                                        health_score: float, recency: float,
                                        frequency: float) -> List[Dict]:
    """Generate specific maintenance recommendations"""
    recommendations = []
    name = contact_data.get('name', 'this contact')
    topics = contact_data.get('topics_discussed', [])

    # Recency-based recommendations
    if recency < 50:
        recommendations.append({
            'type': 'immediate_action',
            'priority': 'high',
            'action': f"Reach out to {name} this week",
            'reason': "It's been too long since last contact",
            'suggested_approach': 'Send a casual check-in message'
        })

    # Frequency-based recommendations
    if frequency < 40:
        recommendations.append({
            'type': 'schedule_recurring',
            'priority': 'medium',
            'action': f"Set up monthly check-ins with {name}",
            'reason': "Regular touch-points will strengthen the relationship",
            'suggested_approach': 'Calendar reminder for monthly coffee chat'
        })

    # Value-add recommendations
    if topics:
        recommendations.append({
            'type': 'value_add',
            'priority': 'medium',
            'action': f"Share relevant content about {topics[0]}",
            'reason': "Show you remember their interests",
            'suggested_approach': f"Send article or resource related to {topics[0]}"
        })

    # Celebration opportunities
    linkedin_profile = contact_data.get('linkedin_profile', {})
    if linkedin_profile.get('is_active'):
        recommendations.append({
            'type': 'engagement',
            'priority': 'low',
            'action': f"Engage with {name}'s LinkedIn content",
            'reason': "Support their professional presence",
            'suggested_approach': 'Like or comment on their posts'
        })

    return recommendations


def calculate_risk_level(health_score: float, recency_score: float) -> str:
    """Calculate risk of relationship fading"""
    if health_score < 40 or recency_score < 30:
        return 'high'
    elif health_score < 60 or recency_score < 50:
        return 'medium'
    else:
        return 'low'


def suggest_next_touchpoint(contact_data: Dict, health_score: float) -> Dict:
    """Suggest when and how to reach out next"""
    name = contact_data.get('name', 'contact')

    if health_score < 40:
        # Urgent - reach out ASAP
        when = datetime.now() + timedelta(days=1)
        method = 'message'
        message = f"Hi {name.split()[0]}, been thinking about you! How have you been?"
    elif health_score < 60:
        # Soon - within a week
        when = datetime.now() + timedelta(days=7)
        method = 'email'
        message = f"Hi {name.split()[0]}, wanted to catch up. Are you free for a quick call?"
    else:
        # Healthy - regular check-in
        when = datetime.now() + timedelta(days=30)
        method = 'linkedin'
        message = f"Hope all is well, {name.split()[0]}! Let's catch up soon."

    return {
        'suggested_date': when.strftime('%Y-%m-%d'),
        'suggested_method': method,
        'suggested_message': message
    }


def generate_overall_relationship_insights(analyses: List[Dict]) -> List[str]:
    """Generate insights about the overall relationship portfolio"""
    insights = []

    total = len(analyses)
    at_risk = sum(1 for a in analyses if a['health_status'] in ['at_risk', 'declining'])
    thriving = sum(1 for a in analyses if a['health_status'] == 'thriving')

    insights.append(f"You have {total} contacts in your network")

    if thriving > 0:
        insights.append(f"{thriving} relationships are thriving - great job!")

    if at_risk > 0:
        insights.append(f"{at_risk} relationships need attention to prevent them from fading")

    avg_health = sum(a['health_score'] for a in analyses) / len(analyses) if analyses else 0
    insights.append(f"Average relationship health score: {avg_health:.0f}/100")

    return insights


# Convenience function for API
def analyze_relationship_health(contact_data: Dict, interaction_history: List[Dict] = None) -> Dict:
    """
    Analyze relationship health for a single contact

    Args:
        contact_data: Contact information
        interaction_history: Optional list of past interactions

    Returns:
        Relationship health analysis

    Example:
        >>> analysis = analyze_relationship_health(contact)
        >>> print(analysis['health_status'])
        'healthy'
    """
    analyzer = RelationshipHealthAnalyzer()
    return analyzer.calculate_relationship_health(contact_data, interaction_history)


# Example usage
if __name__ == "__main__":
    # Test with sample contact
    sample_contact = {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "Machine Learning"],
        "follow_ups": ["Send GitHub repo"],
        "met_at": "DevFest Kolkata 2026",
        "met_date": "2026-02-15",
        "priority_score": 85,
        "linkedin_profile": {
            "found": True,
            "is_active": True
        }
    }

    print("\n" + "="*70)
    print("TESTING RELATIONSHIP HEALTH AGENT")
    print("="*70)

    analysis = analyze_relationship_health(sample_contact)

    print("\nRelationship Health Analysis:")
    print(json.dumps(analysis, indent=2))

    print("\n" + "="*70)
    print("[OK] Relationship health agent test complete!")
    print("="*70)
