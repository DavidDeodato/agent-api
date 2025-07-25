# Load knowledge bases (run once to populate the databases)
def load_knowledge_bases():
    print("Loading NDA knowledge base...")
    nda_knowledge.load(upsert=True)
    
    print("Loading FAQ knowledge base...")
    faq_knowledge.load(upsert=True)
    
    print("Loading Clauses knowledge base...")
    clauses_knowledge.load(upsert=True)
    
    print("Loading Jurisprudences knowledge base...")
    jurisprudences_knowledge.load(upsert=True)
    
    print("All knowledge bases loaded successfully!")

# Run this once to populate the databases
# load_knowledge_bases()


# Example usage
# if __name__ == "__main__":
#     # Analyze a specific NDA document
#     creator_nda_team.print_response(
#         "Please analyze this NDA for a YouTube creator partnership. "
#         "What are the key obligations and potential risks?",
#         stream=True
#     )
    
#     # Ask about specific clauses
#     creator_nda_team.print_response(
#         "What does a non-compete clause typically mean for content creators?",
#         stream=True
#     )
    
#     # Get FAQ information
#     creator_nda_team.print_response(
#         "What are the most common questions creators have about NDAs?",
#         stream=True
#     )