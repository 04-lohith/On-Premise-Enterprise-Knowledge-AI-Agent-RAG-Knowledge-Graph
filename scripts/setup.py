"""
Setup Script - Initialize databases with AIinTime support documents
Run this after starting Docker containers
"""
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def wait_for_services():
    """Wait for all services to be ready"""
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    print("✅ Services ready!")


def init_vector_store():
    """Initialize ChromaDB with AIinTime support documents"""
    print("\n📚 Loading AIinTime Knowledge Base...")
    
    from app.services.vector_search import add_document, get_document_count
    
    # AIinTime specific support documents
    aiintime_docs = [
        # Product Overview
        {
            "content": "AI Intime is an enterprise AI knowledge management platform that transforms scattered knowledge into instant insights. It serves as your company's private, living memory - searchable, auditable, and accessible anytime. AI Intime ensures your enterprise never forgets.",
            "metadata": {"category": "product", "topic": "overview", "priority": "high"}
        },
        {
            "content": "AI Intime is developed by Vegam Solutions Inc., a company with over two decades of enterprise expertise. We have offices in USA, Dubai, and India. For inquiries, contact us at info@aiintime.com.",
            "metadata": {"category": "company", "topic": "about", "priority": "medium"}
        },
        
        # Key Features
        {
            "content": "AI Intime provides enterprise knowledge search capabilities. Unlike generic AI tools like ChatGPT, AI Intime works with your company's private data, ensuring information stays within your organization. All searches and responses are auditable for compliance.",
            "metadata": {"category": "features", "topic": "search", "priority": "high"}
        },
        {
            "content": "AI Intime offers knowledge auditing features. Every query, response, and document access is logged and traceable. This ensures compliance with enterprise governance requirements and provides complete visibility into how organizational knowledge is being used.",
            "metadata": {"category": "features", "topic": "audit", "priority": "high"}
        },
        {
            "content": "AI Intime supports multiple data sources and integrations. You can connect your existing document repositories, databases, and enterprise systems. The platform indexes and makes all your organizational knowledge searchable through natural language queries.",
            "metadata": {"category": "features", "topic": "integrations", "priority": "medium"}
        },
        
        # Getting Started
        {
            "content": "To get started with AI Intime, you can book a demo through our website at www.aiintime.com. Our team will walk you through the platform capabilities and discuss your specific enterprise knowledge management needs.",
            "metadata": {"category": "onboarding", "topic": "demo", "priority": "high"}
        },
        {
            "content": "AI Intime offers a pilot program for enterprises to test the platform with their own data before full deployment. Request a pilot through our website to experience how AI Intime can transform your organization's knowledge management.",
            "metadata": {"category": "onboarding", "topic": "pilot", "priority": "medium"}
        },
        
        # Pricing & Plans
        {
            "content": "AI Intime pricing is customized based on your organization's size, data volume, and specific requirements. Contact our sales team at info@aiintime.com for a personalized quote. We offer flexible plans for enterprises of all sizes.",
            "metadata": {"category": "pricing", "topic": "plans", "priority": "medium"}
        },
        
        # Security & Privacy
        {
            "content": "AI Intime is designed for enterprise security. Your data remains private and within your organization's control. We do not use your company's data to train external models. All data processing complies with enterprise security standards.",
            "metadata": {"category": "security", "topic": "privacy", "priority": "high"}
        },
        {
            "content": "AI Intime supports on-premise deployment for organizations with strict data residency requirements. We also offer cloud deployment options with data encryption at rest and in transit. Contact us to discuss the best deployment model for your needs.",
            "metadata": {"category": "security", "topic": "deployment", "priority": "high"}
        },
        
        # Support
        {
            "content": "For technical support, contact our team at info@aiintime.com. We offer dedicated support for enterprise customers including onboarding assistance, training, and ongoing technical help. Our support team is available during business hours across USA, Dubai, and India time zones.",
            "metadata": {"category": "support", "topic": "contact", "priority": "high"}
        },
        {
            "content": "AI Intime provides comprehensive training and documentation for administrators and end users. After onboarding, your team will have access to user guides, admin manuals, and best practices for maximizing the value of your knowledge management platform.",
            "metadata": {"category": "support", "topic": "training", "priority": "medium"}
        },
        
        # Use Cases
        {
            "content": "AI Intime is ideal for enterprise teams that need to quickly find information across large document repositories. Common use cases include employee knowledge portals, customer support knowledge bases, technical documentation search, and policy/compliance document management.",
            "metadata": {"category": "use-cases", "topic": "applications", "priority": "medium"}
        },
        {
            "content": "AI Intime helps reduce time spent searching for information. Instead of manually browsing folders or using keyword search, employees can ask natural language questions and get instant, accurate answers with source citations.",
            "metadata": {"category": "use-cases", "topic": "benefits", "priority": "medium"}
        },
        
        # FAQ
        {
            "content": "What makes AI Intime different from ChatGPT? Unlike ChatGPT which uses public internet data, AI Intime works exclusively with your organization's private knowledge. It's designed for enterprise use with auditing, security, and compliance features built-in.",
            "metadata": {"category": "faq", "topic": "comparison", "priority": "high"}
        },
        {
            "content": "How long does it take to implement AI Intime? Implementation timeline varies based on data volume and integration requirements. Typical pilot programs can be set up within 2-4 weeks. Full enterprise deployments usually take 4-8 weeks depending on complexity.",
            "metadata": {"category": "faq", "topic": "implementation", "priority": "medium"}
        }
    ]
    
    for i, doc in enumerate(aiintime_docs):
        doc_id = add_document(
            content=doc["content"],
            doc_id=f"aiintime_doc_{i+1}",
            metadata=doc["metadata"]
        )
        topic = doc["metadata"].get("topic", "")
        print(f"  ✓ Added: {doc_id} ({topic})")
    
    print(f"\n✅ Loaded {get_document_count()} AIinTime support documents!")


def init_knowledge_graph():
    """Initialize Neo4j with AIinTime entities and relationships"""
    print("\n🔗 Building AIinTime Knowledge Graph...")
    
    from app.services.graph_search import add_entity, add_relationship
    
    # Entities
    entities = [
        # Company
        ("AI Intime", "Product"),
        ("Vegam Solutions Inc.", "Company"),
        ("USA", "Location"),
        ("Dubai", "Location"),
        ("India", "Location"),
        
        # Features
        ("Knowledge Search", "Feature"),
        ("Audit Trail", "Feature"),
        ("Data Integrations", "Feature"),
        ("Enterprise Security", "Feature"),
        ("On-Premise Deployment", "Feature"),
        ("Cloud Deployment", "Feature"),
        
        # Services
        ("Demo", "Service"),
        ("Pilot Program", "Service"),
        ("Technical Support", "Service"),
        ("Training", "Service"),
        
        # Concepts
        ("Knowledge Management", "Concept"),
        ("Private Data", "Concept"),
        ("Compliance", "Concept"),
        ("Natural Language", "Concept"),
        
        # Contact
        ("info@aiintime.com", "Contact"),
    ]
    
    for name, etype in entities:
        add_entity(name, etype)
        print(f"  ✓ Entity: {name} ({etype})")
    
    # Relationships
    relationships = [
        ("AI Intime", "Vegam Solutions Inc.", "DEVELOPED_BY"),
        ("Vegam Solutions Inc.", "USA", "HAS_OFFICE_IN"),
        ("Vegam Solutions Inc.", "Dubai", "HAS_OFFICE_IN"),
        ("Vegam Solutions Inc.", "India", "HAS_OFFICE_IN"),
        
        ("AI Intime", "Knowledge Search", "HAS_FEATURE"),
        ("AI Intime", "Audit Trail", "HAS_FEATURE"),
        ("AI Intime", "Data Integrations", "HAS_FEATURE"),
        ("AI Intime", "Enterprise Security", "HAS_FEATURE"),
        
        ("AI Intime", "On-Premise Deployment", "SUPPORTS"),
        ("AI Intime", "Cloud Deployment", "SUPPORTS"),
        
        ("AI Intime", "Demo", "OFFERS"),
        ("AI Intime", "Pilot Program", "OFFERS"),
        ("AI Intime", "Technical Support", "OFFERS"),
        ("AI Intime", "Training", "OFFERS"),
        
        ("AI Intime", "Knowledge Management", "ENABLES"),
        ("Enterprise Security", "Private Data", "PROTECTS"),
        ("Audit Trail", "Compliance", "ENSURES"),
        ("Knowledge Search", "Natural Language", "USES"),
        
        ("Technical Support", "info@aiintime.com", "CONTACT_VIA"),
    ]
    
    for from_e, to_e, rel in relationships:
        add_relationship(from_e, to_e, rel)
        print(f"  ✓ {from_e} --[{rel}]--> {to_e}")
    
    print("\n✅ Knowledge graph ready!")


def main():
    """Run full setup for AIinTime"""
    print("=" * 55)
    print("🚀 AI Intime Customer Support - Setup")
    print("=" * 55)
    
    wait_for_services()
    
    try:
        init_vector_store()
    except Exception as e:
        print(f"❌ Vector store error: {e}")
    
    try:
        init_knowledge_graph()
    except Exception as e:
        print(f"❌ Graph store error: {e}")
    
    print("\n" + "=" * 55)
    print("🎉 AIinTime Support System Ready!")
    print("   Open http://localhost:5000 to test")
    print("=" * 55)


if __name__ == "__main__":
    main()
