import json
from typing import Dict, List, Optional, Any
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.tools import tool
from pepperlaw_intelligent_agents.src.crud.da_database_crud import NDADatabaseCrud
from pepperlaw_intelligent_agents.src.models.doc_template_model import DocTemplateModel
from pepperlaw_intelligent_agents.src.models.clause_model import ClauseModel
from pepperlaw_intelligent_agents.src.models.document_agent import DocumentAgentModel
from pepperlaw_intelligent_agents.src.models.clause_type import ClauseType


@tool(show_result=True)
def start_nda_creation(self) -> str:
    """Start the NDA creation process by selecting a template and initializing the document."""
    try:
        # Select template (for now, use the first available)
        if not self.doc_template_ids:
            return "❌ No document templates available. Please contact administrator."
        
        self.current_template_id = self.doc_template_ids[0]  # Use first template
        template = self.db.get_doc_template(self.current_template_id)
        
        if not template:
            return f"❌ Template with ID {self.current_template_id} not found."
        
        # Load clauses for this template
        self.current_clauses = self.db.get_clauses_by_template(self.current_template_id)
        
        if not self.current_clauses:
            return f"❌ No clauses found for template '{template.name}'."
        
        # Create new document agent record
        doc_agent = self.db.create_document_agent(self.current_template_id)
        self.current_document_id = doc_agent.id
        self.current_clause_index = 0
        
        return f"""
✅ **NDA Creation Started**

📋 **Template**: {template.name}
📄 **Document ID**: {self.current_document_id}
📊 **Total Clauses**: {len(self.current_clauses)}

Let's begin with the first clause. I'll guide you through each section step by step.

{self._get_current_clause_prompt()}
"""
    except Exception as e:
        return f"❌ Error starting NDA creation: {str(e)}"

@tool(show_result=True)
def process_clause_response(self, user_response: str) -> str:
    """Process the user's response to the current clause."""
    try:
        if not self.current_document_id or self.current_clause_index >= len(self.current_clauses):
            return "❌ No active NDA creation session. Please start a new NDA creation."
        
        current_clause = self.current_clauses[self.current_clause_index]
        
        # Validate response against alert conditions
        validation_result = self._validate_response(user_response, current_clause)
        if not validation_result["valid"]:
            return f"""
⚠️ **Validation Alert**

{validation_result['message']}

Please provide a corrected response for: **{current_clause.section_name}**

{current_clause.system_prompt}
"""
        
        # Save the response
        self.db.update_document_agent_content(
            self.current_document_id,
            current_clause.section_name,
            user_response,
            current_clause.order_num
        )
        
        response = f"""
✅ **Section Completed**: {current_clause.section_name}

Your response has been saved: "{user_response}"

Tudo certo nessa seção. Posso seguir para a próxima cláusula?
"""
        
        return response
        
    except Exception as e:
        return f"❌ Error processing response: {str(e)}"

@tool(show_result=True)
def skip_optional_clause(self, section_name: str) -> str:
    """Skip an optional clause."""
    try:
        current_clause = self.current_clauses[self.current_clause_index]
        
        if current_clause.type != ClauseType.OPTIONAL:
            return f"❌ Cannot skip mandatory clause: {current_clause.section_name}"
        
        if current_clause.section_name != section_name:
            return f"❌ Section name mismatch. Expected: {current_clause.section_name}"
        
        return f"✅ Optional clause '{section_name}' has been skipped. Ready to proceed to the next clause."
        
    except Exception as e:
        return f"❌ Error skipping clause: {str(e)}"

@tool(show_result=True)
def proceed_to_next_clause(self) -> str:
    """Move to the next clause in the NDA creation process."""
    try:
        self.current_clause_index += 1
        
        if self.current_clause_index >= len(self.current_clauses):
            return self._finalize_document()
        
        return self._get_current_clause_prompt()
        
    except Exception as e:
        return f"❌ Error proceeding to next clause: {str(e)}"

@tool(show_result=True)
def get_document_preview(self) -> str:
    """Get a live preview of the current document state."""
    try:
        if not self.current_document_id:
            return "❌ No active document session."
        
        doc_agent = self.db.get_document_agent(self.current_document_id)
        if not doc_agent:
            return "❌ Document not found."
        
        template = self.db.get_doc_template(self.current_template_id)
        current_clause = self.current_clauses[self.current_clause_index] if self.current_clause_index < len(self.current_clauses) else None
        
        preview = f"""
📄 **Live Document Preview**

**Template**: {template.name}
**Status**: {doc_agent.status}
**Progress**: {len(doc_agent.content)}/{len(self.current_clauses)} clauses completed

---

**Completed Sections:**
"""
        
        for section_name, content in doc_agent.content.items():
            preview += f"\n**{section_name}**: {content}"
        
        if current_clause:
            preview += f"\n\n🔄 **Currently Working On**: {current_clause.section_name}"
        
        preview += "\n\n---"
        return preview
        
    except Exception as e:
        return f"❌ Error getting document preview: {str(e)}"

@tool(show_result=True)
def validate_clause_content(self, content: str) -> str:
    """Validate content against the current clause's alert conditions."""
    try:
        if self.current_clause_index >= len(self.current_clauses):
            return "❌ No current clause to validate against."
        
        current_clause = self.current_clauses[self.current_clause_index]
        validation_result = self._validate_response(content, current_clause)
        
        if validation_result["valid"]:
            return f"✅ Content validation passed for '{current_clause.section_name}'"
        else:
            return f"⚠️ Validation failed: {validation_result['message']}"
            
    except Exception as e:
        return f"❌ Error validating content: {str(e)}"


@tool(show_result=True)
def complete_nda_document(self) -> str:
    """Complete the NDA document creation process."""
    try:
        if not self.current_document_id:
            return "❌ No active document session."
        
        # Check if all mandatory clauses are completed
        doc_agent = self.db.get_document_agent(self.current_document_id)
        if not doc_agent:
            return "❌ Document not found."
        
        mandatory_clauses = [c for c in self.current_clauses if c.type == ClauseType.MANDATORY]
        completed_mandatory = [c.section_name for c in mandatory_clauses if c.section_name in doc_agent.content]
        
        if len(completed_mandatory) < len(mandatory_clauses):
            missing = [c.section_name for c in mandatory_clauses if c.section_name not in doc_agent.content]
            return f"""
❌ **Cannot Complete Document**

Missing mandatory clauses:
{chr(10).join(f"• {clause}" for clause in missing)}

Please complete all mandatory clauses before finalizing the document.
"""
        
        # Mark document as completed
        completed_doc = self.db.complete_document_agent(self.current_document_id)
        template = self.db.get_doc_template(self.current_template_id)
        
        # Generate final document summary
        final_document = self._generate_final_document(completed_doc, template)
        
        # Reset session state
        self.current_document_id = None
        self.current_template_id = None
        self.current_clauses = []
        self.current_clause_index = 0
        
        return f"""
🎉 **NDA Document Completed Successfully!**

**Document ID**: {completed_doc.id}
**Template**: {template.name}
**Completion Date**: {completed_doc.updated_at}
**Total Clauses**: {len(completed_doc.content)}

---

{final_document}

---

✅ Your NDA document has been saved and is ready for use. You can start a new NDA creation anytime by calling the start_nda_creation tool.
"""
            
    except Exception as e:
        return f"❌ Error completing document: {str(e)}"


def _get_current_clause_prompt(self) -> str:
    """Get the prompt for the current clause."""
    if self.current_clause_index >= len(self.current_clauses):
        return "All clauses completed!"
    
    current_clause = self.current_clauses[self.current_clause_index]
    
    prompt = f"""
---

**Clause {self.current_clause_index + 1}/{len(self.current_clauses)}**: {current_clause.section_name}
**Type**: {'🔴 Mandatory' if current_clause.type == ClauseType.MANDATORY else '🟡 Optional'}

"""
        
    # For optional clauses, ask if they want to include it
    if current_clause.type == ClauseType.OPTIONAL:
        prompt += f"❓ **Do you want to include the clause '{current_clause.section_name}'?** (Yes/No)\n\n"
    
    prompt += f"📝 **{current_clause.system_prompt}**"
    
    # Add suggestions if available
    if current_clause.suggestions:
        prompt += f"\n\n💡 **Suggestions**:\n"
        for key, value in current_clause.suggestions.items():
            prompt += f"• **{key}**: {value}\n"
    
    # Add type alternatives if available
    if current_clause.type_alternatives:
        prompt += f"\n\n🔄 **Alternative Options**:\n"
        for key, value in current_clause.type_alternatives.items():
            prompt += f"• **{key}**: {value}\n"
    
    return prompt
    
def _validate_response(self, response: str, clause: Clause) -> Dict[str, Any]:
    """Validate user response against clause alert conditions."""
    if not clause.alert_conditions:
        return {"valid": True, "message": ""}
    
    response_lower = response.lower().strip()
    
    for condition_name, condition_data in clause.alert_conditions.items():
        condition_type = condition_data.get("type", "")
        condition_value = condition_data.get("value", "")
        alert_message = condition_data.get("message", f"Alert condition '{condition_name}' triggered")
            
        if condition_type == "contains_forbidden_words":
            forbidden_words = condition_value if isinstance(condition_value, list) else [condition_value]
            for word in forbidden_words:
                if word.lower() in response_lower:
                    return {
                        "valid": False,
                        "message": f"{alert_message}\n\nForbidden word detected: '{word}'"
                    }
            
        elif condition_type == "min_length":
            if len(response.strip()) < condition_value:
                return {
                    "valid": False,
                    "message": f"{alert_message}\n\nMinimum length required: {condition_value} characters"
                }
            
        elif condition_type == "max_length":
            if len(response.strip()) > condition_value:
                return {
                    "valid": False,
                    "message": f"{alert_message}\n\nMaximum length allowed: {condition_value} characters"
                }
            
        elif condition_type == "required_pattern":
            import re
            if not re.search(condition_value, response, re.IGNORECASE):
                return {
                    "valid": False,
                    "message": f"{alert_message}\n\nRequired pattern not found: {condition_value}"
                }
            
        elif condition_type == "must_contain":
            required_terms = condition_value if isinstance(condition_value, list) else [condition_value]
            for term in required_terms:
                if term.lower() not in response_lower:
                    return {
                        "valid": False,
                        "message": f"{alert_message}\n\nRequired term missing: '{term}'"
                    }
    
    return {"valid": True, "message": ""}

def _generate_final_document(self, doc_agent: DocumentAgent, template: DocTemplate) -> str:
    """Generate the final formatted NDA document."""
    document = f"""
# {template.name}

**Document ID**: {doc_agent.id}
**Created**: {doc_agent.created_at}
**Completed**: {doc_agent.updated_at}

---
"""

    # Add each completed clause in order
    for clause in self.current_clauses:
        if clause.section_name in doc_agent.content:
            content = doc_agent.content[clause.section_name]
            document += f"""
## {clause.section_name}

{content}

---
"""

    document += """
**End of Document**

This NDA document has been generated using the AGNO NDA Creator system.
"""
        
    return document
    

def _finalize_document(self) -> str:
    """Finalize the document when all clauses are completed."""
    return """
🎯 **All Clauses Completed!**

You have successfully completed all clauses for this NDA document. 

To finalize and save your document, please confirm by saying "Complete the document" or use the complete_nda_document tool.

You can also use get_document_preview to review the final document before completion.
"""