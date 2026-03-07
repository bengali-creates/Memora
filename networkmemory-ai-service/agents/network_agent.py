"""
Network Graph Agent

This agent builds and analyzes relationship networks from conversation data.
Uses NetworkX for graph analysis and finds valuable connection patterns.

Capabilities:
1. Build relationship graph from conversations
2. Find shortest paths between contacts
3. Identify key connectors (high centrality)
4. Suggest strategic introductions
5. Detect clusters and communities
6. Calculate network metrics
"""

from crewai import Agent, Task
from typing import Dict, List, Optional, Tuple
import networkx as nx
from datetime import datetime
import json


def create_network_analyst() -> Agent:
    """
    Create network analysis agent

    This agent specializes in analyzing professional networks
    and finding valuable connection opportunities.

    Returns:
        Agent configured for network analysis
    """
    return Agent(
        role='Professional Network Analyst',
        goal='Analyze professional networks to identify valuable connections, strategic introductions, and relationship opportunities',
        backstory="""You are an expert at analyzing professional networks and understanding
        the value of connections. You can identify key connectors, find shortest paths
        between people, and suggest strategic introductions that create mutual value.
        You understand network effects, the strength of weak ties, and how to leverage
        professional networks for career growth and business development.""",
        verbose=True,
        allow_delegation=False,
        tools=[]
    )


class NetworkGraph:
    """
    Professional network graph manager

    Manages the relationship graph and provides analysis methods
    """

    def __init__(self):
        """Initialize empty network graph"""
        self.graph = nx.Graph()
        self.user_node = "user"  # The user is the center of the network

        # Add user node
        self.graph.add_node(self.user_node, node_type="user")

    def add_contact(self, contact_data: Dict):
        """
        Add a contact to the network

        Args:
            contact_data: Contact information including name, company, role, etc.
        """
        contact_name = contact_data.get('name', 'Unknown')

        # Add contact node
        self.graph.add_node(
            contact_name,
            node_type="contact",
            company=contact_data.get('company'),
            role=contact_data.get('role'),
            met_at=contact_data.get('met_at'),
            met_date=contact_data.get('met_date'),
            topics=contact_data.get('topics_discussed', []),
            priority=contact_data.get('priority_score', 50)
        )

        # Add edge between user and contact
        self.graph.add_edge(
            self.user_node,
            contact_name,
            relationship="met",
            strength=calculate_relationship_strength(contact_data)
        )

        # Add mentioned connections (if any)
        mentioned_connections = extract_mentioned_connections(contact_data)
        for connection in mentioned_connections:
            self.add_indirect_connection(contact_name, connection)

    def add_indirect_connection(self, contact_name: str, connection_name: str):
        """
        Add an indirect connection (someone mentioned by a contact)

        Args:
            contact_name: Name of the contact who mentioned the connection
            connection_name: Name of the mentioned person
        """
        # Add connection node if not exists
        if connection_name not in self.graph:
            self.graph.add_node(
                connection_name,
                node_type="indirect",
                source=contact_name
            )

        # Add edge between contact and their connection
        self.graph.add_edge(
            contact_name,
            connection_name,
            relationship="knows",
            strength=0.5  # Lower strength for indirect connections
        )

    def find_path_to_contact(self, target_contact: str) -> Optional[List[str]]:
        """
        Find shortest path from user to a target contact

        Args:
            target_contact: Name of the contact to reach

        Returns:
            List of names representing the path, or None if no path exists
        """
        try:
            if target_contact in self.graph:
                return nx.shortest_path(self.graph, self.user_node, target_contact)
            return None
        except nx.NetworkXNoPath:
            return None

    def find_key_connectors(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Find contacts who are key connectors (high betweenness centrality)

        These are people who connect different parts of your network.

        Args:
            top_n: Number of top connectors to return

        Returns:
            List of (name, centrality_score) tuples
        """
        centrality = nx.betweenness_centrality(self.graph)

        # Filter out user node
        contact_centrality = {k: v for k, v in centrality.items() if k != self.user_node}

        # Sort by centrality score
        sorted_connectors = sorted(contact_centrality.items(), key=lambda x: x[1], reverse=True)

        return sorted_connectors[:top_n]

    def suggest_introductions(self, contact_name: str) -> List[Dict]:
        """
        Suggest introductions for a contact based on:
        1. Shared topics/interests
        2. Complementary roles
        3. Same company or industry

        Args:
            contact_name: Name of the contact to find introductions for

        Returns:
            List of introduction suggestions with reasoning
        """
        if contact_name not in self.graph:
            return []

        suggestions = []
        contact_data = self.graph.nodes[contact_name]

        # Get all other contacts (not indirect connections)
        other_contacts = [
            n for n in self.graph.nodes()
            if n != contact_name and n != self.user_node
            and self.graph.nodes[n].get('node_type') == 'contact'
        ]

        for other in other_contacts:
            # Skip if they're already connected
            if self.graph.has_edge(contact_name, other):
                continue

            other_data = self.graph.nodes[other]

            # Calculate introduction value
            shared_topics = set(contact_data.get('topics', [])) & set(other_data.get('topics', []))
            same_company = contact_data.get('company') == other_data.get('company')

            if shared_topics or same_company:
                suggestions.append({
                    'introduce': other,
                    'to': contact_name,
                    'reason': create_introduction_reason(
                        contact_name, other, shared_topics, same_company, contact_data, other_data
                    ),
                    'shared_interests': list(shared_topics),
                    'value_score': len(shared_topics) * 10 + (20 if same_company else 0)
                })

        # Sort by value score
        suggestions.sort(key=lambda x: x['value_score'], reverse=True)

        return suggestions[:5]  # Top 5 suggestions

    def detect_communities(self) -> List[List[str]]:
        """
        Detect communities (clusters) in the network

        Useful for understanding different groups in your network
        (e.g., work colleagues, conference contacts, etc.)

        Returns:
            List of communities (each community is a list of names)
        """
        communities = nx.community.greedy_modularity_communities(self.graph)

        return [list(community) for community in communities]

    def calculate_network_metrics(self) -> Dict:
        """
        Calculate overall network metrics

        Returns:
            Dictionary with network statistics
        """
        return {
            'total_contacts': self.graph.number_of_nodes() - 1,  # Exclude user
            'total_connections': self.graph.number_of_edges(),
            'network_density': nx.density(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'connected_components': nx.number_connected_components(self.graph),
            'largest_component_size': len(max(nx.connected_components(self.graph), key=len)),
        }

    def export_for_visualization(self) -> Dict:
        """
        Export graph data for visualization (e.g., D3.js, Cytoscape)

        Returns:
            Dictionary with nodes and edges for visualization
        """
        nodes = []
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                'id': node,
                'type': data.get('node_type', 'unknown'),
                'company': data.get('company'),
                'role': data.get('role'),
                'topics': data.get('topics', []),
                'priority': data.get('priority', 50)
            })

        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                'source': source,
                'target': target,
                'relationship': data.get('relationship', 'connected'),
                'strength': data.get('strength', 1.0)
            })

        return {
            'nodes': nodes,
            'edges': edges
        }


def calculate_relationship_strength(contact_data: Dict) -> float:
    """
    Calculate relationship strength based on:
    - Number of topics discussed
    - Number of action items
    - Meeting context (conference, 1-on-1, etc.)

    Args:
        contact_data: Contact information

    Returns:
        Strength score (0.0 to 1.0)
    """
    strength = 0.5  # Base strength

    topics = contact_data.get('topics_discussed', [])
    strength += min(len(topics) * 0.1, 0.3)  # Up to +0.3 for topics

    action_items = contact_data.get('follow_ups', [])
    strength += min(len(action_items) * 0.1, 0.2)  # Up to +0.2 for action items

    return min(strength, 1.0)


def extract_mentioned_connections(contact_data: Dict) -> List[str]:
    """
    Extract names of people mentioned in the conversation

    Args:
        contact_data: Contact information with conversation

    Returns:
        List of mentioned names
    """
    # In production, use NLP (spaCy) to extract person names
    # For demo, return mock data
    conversation = contact_data.get('conversation_summary', '')

    # Simple heuristic: look for "introduced me to", "knows", "works with"
    mentioned = []

    # This would be replaced with actual NER in production
    # For now, return empty list (can be enhanced with spaCy)

    return mentioned


def create_introduction_reason(contact1: str, contact2: str, shared_topics: set,
                               same_company: bool, data1: Dict, data2: Dict) -> str:
    """Create a compelling reason for introduction"""
    reasons = []

    if shared_topics:
        topics_str = ', '.join(list(shared_topics)[:2])
        reasons.append(f"both interested in {topics_str}")

    if same_company:
        reasons.append(f"both at {data1.get('company')}")

    role1 = data1.get('role', 'professional')
    role2 = data2.get('role', 'professional')

    if role1 and role2:
        reasons.append(f"complementary roles ({role1} and {role2})")

    if not reasons:
        reasons.append("potential synergy in professional interests")

    return f"{contact1} and {contact2}: " + ", ".join(reasons)


def analyze_network(contacts: List[Dict]) -> Dict:
    """
    Main function to analyze a network of contacts

    Args:
        contacts: List of contact dictionaries

    Returns:
        Comprehensive network analysis

    Example:
        >>> contacts = [{"name": "Alice", "company": "Google"}, ...]
        >>> analysis = analyze_network(contacts)
        >>> print(analysis['key_connectors'])
    """
    # Create network graph
    network = NetworkGraph()

    # Add all contacts
    for contact in contacts:
        network.add_contact(contact)

    # Perform analysis
    key_connectors = network.find_key_connectors()
    communities = network.detect_communities()
    metrics = network.calculate_network_metrics()
    graph_data = network.export_for_visualization()

    # Generate introduction suggestions for all contacts
    all_suggestions = []
    for contact in contacts:
        contact_name = contact.get('name')
        if contact_name:
            suggestions = network.suggest_introductions(contact_name)
            if suggestions:
                all_suggestions.extend(suggestions)

    # Sort all suggestions by value
    all_suggestions.sort(key=lambda x: x['value_score'], reverse=True)

    analysis = {
        'network_metrics': metrics,
        'key_connectors': [
            {'name': name, 'centrality_score': score, 'impact': 'high' if score > 0.1 else 'medium'}
            for name, score in key_connectors
        ],
        'communities': [
            {'id': i, 'members': community, 'size': len(community)}
            for i, community in enumerate(communities)
        ],
        'introduction_suggestions': all_suggestions[:10],  # Top 10
        'graph_visualization': graph_data,
        'insights': generate_network_insights(metrics, key_connectors, communities),
        'analyzed_at': datetime.utcnow().isoformat()
    }

    return analysis


def generate_network_insights(metrics: Dict, key_connectors: List, communities: List) -> List[str]:
    """Generate human-readable insights about the network"""
    insights = []

    total_contacts = metrics['total_contacts']
    insights.append(f"Your network has {total_contacts} contacts")

    if key_connectors:
        top_connector = key_connectors[0][0]
        insights.append(f"{top_connector} is your most valuable connector - they bridge different parts of your network")

    num_communities = len(communities)
    if num_communities > 1:
        insights.append(f"Your network has {num_communities} distinct communities (e.g., work, conferences, industry groups)")

    density = metrics['network_density']
    if density < 0.3:
        insights.append("Your network is loosely connected - there are opportunities to create more introductions")
    else:
        insights.append("Your network is well-connected - people know each other")

    return insights


# Example usage
if __name__ == "__main__":
    # Test the agent with sample contact data
    sample_contacts = [
        {
            "name": "Sarah Chen",
            "role": "ML Engineer",
            "company": "Google",
            "topics_discussed": ["AI safety", "Machine Learning"],
            "follow_ups": ["Send GitHub repo"],
            "met_at": "DevFest Kolkata 2026",
            "priority_score": 85
        },
        {
            "name": "John Smith",
            "role": "Product Manager",
            "company": "Microsoft",
            "topics_discussed": ["Product Development", "AI"],
            "follow_ups": ["Schedule call"],
            "met_at": "Tech Summit 2026",
            "priority_score": 75
        },
        {
            "name": "Emily Davis",
            "role": "Data Scientist",
            "company": "Google",
            "topics_discussed": ["Machine Learning", "Data Analysis"],
            "follow_ups": [],
            "met_at": "DevFest Kolkata 2026",
            "priority_score": 80
        }
    ]

    print("\n" + "="*70)
    print("TESTING NETWORK ANALYSIS AGENT")
    print("="*70)

    analysis = analyze_network(sample_contacts)

    print("\nNetwork Analysis:")
    print(json.dumps(analysis, indent=2))

    print("\n" + "="*70)
    print("[OK] Network agent test complete!")
    print("="*70)
