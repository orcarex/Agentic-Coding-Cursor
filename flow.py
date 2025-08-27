from pocketflow import Flow
from nodes import (
    GetQuestionNode,
    AnswerNode,
    MainDecisionAgentNode,
    ReadFileActionNode,
    GrepSearchActionNode,
    ListDirectoryActionNode,
    DeleteFileActionNode,
    ReadTargetFileNode,
    AnalyzeAndPlanChangesNode,
    ApplyChangesBatchNode,
    FormatResponseNode,
)

def create_qa_flow():
    """Create and return a question-answering flow."""
    # Create nodes
    get_question_node = GetQuestionNode()
    answer_node = AnswerNode()
    
    # Connect nodes in sequence
    get_question_node >> answer_node
    
    # Create flow starting with input node
    return Flow(start=get_question_node)

qa_flow = create_qa_flow()


def create_coding_agent_flow():
    decide = MainDecisionAgentNode()
    read_file = ReadFileActionNode()
    grep = GrepSearchActionNode()
    list_dir = ListDirectoryActionNode()
    delete_file = DeleteFileActionNode()

    # Edit subflow
    read_target = ReadTargetFileNode()
    plan = AnalyzeAndPlanChangesNode()
    apply_changes = ApplyChangesBatchNode()

    # Wiring main decisions
    decide - "read_file" >> read_file
    decide - "grep_search" >> grep
    decide - "list_dir" >> list_dir
    decide - "delete_file" >> delete_file
    decide - "edit_file" >> read_target
    decide - "finish" >> FormatResponseNode()

    # Edit agent subflow
    read_file - "decide_next" >> decide
    grep - "decide_next" >> decide
    list_dir - "decide_next" >> decide
    delete_file - "decide_next" >> decide

    read_target - "analyze_plan" >> plan
    plan - "apply_changes" >> apply_changes
    apply_changes - "decide_next" >> decide

    return Flow(start=decide)


coding_agent_flow = create_coding_agent_flow()