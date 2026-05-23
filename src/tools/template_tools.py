"""Tool wrappers for Survey Template, Questions, and Integration Field operations."""
from typing import Optional, List, Dict, Any
from callhub.survey_templates import (
    list_survey_templates,
    get_survey_template,
    create_survey_template,
    update_survey_template,
    delete_survey_template,
    get_template_schema,
)
from callhub.questions import (
    list_questions,
    get_question,
)
from callhub.integration_fields import (
    list_integration_fields,
    get_integration_field,
    get_integration_field_schema,
)


def register(server):
    @server.tool(name="listSurveyTemplates", description="List all survey templates for the authenticated user.")
    def list_survey_templates_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return list_survey_templates(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getSurveyTemplate", description="Get details for a specific survey template by ID.")
    def get_survey_template_tool(
        account: Optional[str] = None,
        templateId: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if templateId:
                params["templateId"] = templateId
            return get_survey_template(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createSurveyTemplate", description="Create a new survey template with questions. Pass questions as a list of dictionaries with 'type', 'question', and optional 'question_name', 'is_initial_message' fields.")
    def create_survey_template_tool(
        account: Optional[str] = None,
        label: str = None,
        questions: List[Dict[str, Any]] = None
    ) -> dict:
        try:
            if not label:
                return {"isError": True, "content": [{"type": "text", "text": "label is required"}]}

            params = {
                "label": label,
                "questions": questions or []
            }
            if account:
                params["accountName"] = account

            return create_survey_template(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateSurveyTemplate", description="Update an existing survey template.")
    def update_survey_template_tool(
        account: Optional[str] = None,
        templateId: str = None,
        label: Optional[str] = None,
        questions: Optional[List[Dict[str, Any]]] = None
    ) -> dict:
        try:
            if not templateId:
                return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}

            params = {"templateId": templateId}
            if account:
                params["accountName"] = account
            if label:
                params["label"] = label
            if questions:
                params["questions"] = questions

            return update_survey_template(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteSurveyTemplate", description="Delete a survey template by ID.")
    def delete_survey_template_tool(
        account: Optional[str] = None,
        templateId: str = None
    ) -> dict:
        try:
            if not templateId:
                return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}

            params = {"templateId": templateId}
            if account:
                params["accountName"] = account

            return delete_survey_template(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listQuestions", description="List all questions with optional type filtering (PDI_QUESTION, VAN_QUESTION).")
    def list_questions_tool(
        account: Optional[str] = None,
        type: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if type:
                params["type"] = type

            return list_questions(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getQuestion", description="Get details for a specific question by ID.")
    def get_question_tool(
        account: Optional[str] = None,
        questionId: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if questionId:
                params["questionId"] = questionId

            return get_question(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listIntegrationFields", description="List all integration fields.")
    def list_integration_fields_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return list_integration_fields(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getIntegrationField", description="Get details for a specific integration field by ID.")
    def get_integration_field_tool(
        account: Optional[str] = None,
        fieldId: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if fieldId:
                params["fieldId"] = fieldId

            return get_integration_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getTemplateSchema", description="Get the JSON schema for template API resources.")
    def get_template_schema_tool(
        account: Optional[str] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_template_schema(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getIntegrationFieldSchema", description="Get the JSON schema for integration field API resources.")
    def get_integration_field_schema_tool(
        account: Optional[str] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_integration_field_schema(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
