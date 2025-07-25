from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase

# NDA Documents Knowledge Base
nda_knowledge = PDFKnowledgeBase(
    path="data/nda_documents",
    vector_db=nda_vector_db,
)

# FAQ Knowledge Base  
faq_knowledge = TextKnowledgeBase(
    path="data/faq",
    vector_db=faq_vector_db,
)

# Clauses Knowledge Base
clauses_knowledge = JSONKnowledgeBase(
    path="data/clauses", 
    vector_db=clauses_vector_db,
)

# Jurisprudences Knowledge Base
jurisprudences_knowledge = PDFKnowledgeBase(
    path="data/jurisprudences",
    vector_db=jurisprudences_vector_db,
)