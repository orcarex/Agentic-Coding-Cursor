import logging
from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.read_file import read_file as util_read_file
from utils.search_ops import grep_search as util_grep_search
from utils.dir_ops import list_directory as util_list_directory
from utils.delete_file import delete_file as util_delete_file
from utils.replace_file import replace_range as util_replace_range

class GetQuestionNode(Node):
    def exec(self, _):
        # Get question directly from user input
        user_question = input("Enter your question: ")
        return user_question
    
    def post(self, shared, prep_res, exec_res):
        # Store the user's question
        shared["question"] = exec_res
        return "default"  # Go to the next node

class AnswerNode(Node):
    def prep(self, shared):
        # Read question from shared
        return shared["question"]
    
    def exec(self, question):
        # Call LLM to get the answer
        return call_llm(question)
    
    def post(self, shared, prep_res, exec_res):
        # Store the answer in shared
        shared["answer"] = exec_res
        logging.info("AnswerNode stored answer of length=%s", len(exec_res) if exec_res else 0)


def get_initial_shared(working_dir: str, user_query: str = "") -> dict:
    """
    Create initial shared store per design.
    """
    return {
        "user_query": user_query,
        "working_dir": working_dir,
        "history": [],
        "edit_operations": [],
        "response": "",
    }


class MainDecisionAgentNode(Node):
    def prep(self, shared):
        return shared.get("user_query", ""), shared.get("history", [])

    def exec(self, inputs):
        user_query, history = inputs
        prompt = (
            "You are a coding agent deciding next action.\n"
            "Tools: read_file, edit_file, delete_file, grep_search, list_dir, finish.\n"
            "Given the user request and prior history, choose one tool and params as JSON:\n"
            "{tool: string, reason: string, params: object}\n\n"
            f"User: {user_query}\nHistory: {history}"
        )
        result = call_llm(prompt)
        return result

    def post(self, shared, prep_res, exec_res):
        # Expect exec_res is JSON-like; if parsing fails, default to finish
        import json
        try:
            decision = json.loads(exec_res)
            assert isinstance(decision, dict)
            tool = decision.get("tool", "finish")
            params = decision.get("params", {})
            reason = decision.get("reason", "")
        except Exception:
            tool = "finish"
            params = {}
            reason = "fallback: parsing error"

        shared.setdefault("history", []).append({
            "tool": tool,
            "reason": reason,
            "params": params,
            "result": None,
        })
        logging.info("MainDecisionAgent selected tool=%s reason=%s", tool, reason)
        return tool


class ReadFileActionNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        target = entry.get("params", {}).get("target_file", "")
        return shared["working_dir"], target

    def exec(self, inputs):
        working_dir, target = inputs
        ok, content, err = util_read_file(working_dir, target)
        return {"success": ok, "content": content, "error": err}

    def post(self, shared, prep_res, exec_res):
        shared["history"][-1]["result"] = exec_res
        logging.info("ReadFileActionNode success=%s bytes=%s", exec_res.get("success"), len(exec_res.get("content") or ""))
        return "decide_next"


class GrepSearchActionNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        params = entry.get("params", {})
        return (
            shared["working_dir"],
            params.get("query", ""),
            params.get("case_sensitive", None),
            params.get("include_pattern", None),
            params.get("exclude_pattern", None),
        )

    def exec(self, inputs):
        working_dir, query, case_sensitive, include_pattern, exclude_pattern = inputs
        ok, results, err = util_grep_search(
            working_dir=working_dir,
            query=query,
            case_sensitive=case_sensitive,
            include_pattern=include_pattern,
            exclude_pattern=exclude_pattern,
        )
        return {"success": ok, "results": results, "error": err}

    def post(self, shared, prep_res, exec_res):
        shared["history"][-1]["result"] = exec_res
        logging.info("GrepSearchActionNode success=%s matches=%s", exec_res.get("success"), len(exec_res.get("results") or []))
        return "decide_next"


class ListDirectoryActionNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        path = entry.get("params", {}).get("relative_workspace_path", ".")
        return shared["working_dir"], path

    def exec(self, inputs):
        working_dir, rel = inputs
        ok, tree_str = util_list_directory(working_dir, rel)
        return {"success": ok, "tree_visualization": tree_str}

    def post(self, shared, prep_res, exec_res):
        shared["history"][-1]["result"] = exec_res
        logging.info("ListDirectoryActionNode success=%s", exec_res.get("success"))
        return "decide_next"


class DeleteFileActionNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        target = entry.get("params", {}).get("target_file", "")
        return shared["working_dir"], target

    def exec(self, inputs):
        working_dir, target = inputs
        ok, err = util_delete_file(working_dir, target)
        return {"success": ok, "error": err}

    def post(self, shared, prep_res, exec_res):
        shared["history"][-1]["result"] = exec_res
        logging.info("DeleteFileActionNode success=%s", exec_res.get("success"))
        return "decide_next"


class ReadTargetFileNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        target = entry.get("params", {}).get("target_file", "")
        return shared["working_dir"], target

    def exec(self, inputs):
        working_dir, target = inputs
        ok, content, err = util_read_file(working_dir, target)
        return {"success": ok, "content": content, "error": err}

    def post(self, shared, prep_res, exec_res):
        shared["history"][-1]["result"] = exec_res
        logging.info("ReadTargetFileNode success=%s bytes=%s", exec_res.get("success"), len(exec_res.get("content") or ""))
        return "analyze_plan"


class AnalyzeAndPlanChangesNode(Node):
    def prep(self, shared):
        entry = shared["history"][-1]
        content = entry.get("result", {}).get("content", "")
        params = entry.get("params", {})
        instructions = params.get("instructions", "")
        code_edit = params.get("code_edit", "")
        return content, instructions, code_edit

    def exec(self, inputs):
        content, instructions, code_edit = inputs
        prompt = (
            "Given the file content, plan edits as JSON list of operations with"
            " start_line, end_line, replacement.\n"
            f"Instructions: {instructions}\nCode Edit: {code_edit}\n"
            f"File Content:\n{content[:8000]}"
        )
        plan = call_llm(prompt)
        return plan

    def post(self, shared, prep_res, exec_res):
        import json
        try:
            ops = json.loads(exec_res)
            assert isinstance(ops, list)
        except Exception:
            ops = []
        shared["edit_operations"] = ops
        logging.info("AnalyzeAndPlanChangesNode planned ops=%s", len(ops))
        return "apply_changes"


class ApplyChangesBatchNode(BatchNode):
    def prep(self, shared):
        ops = shared.get("edit_operations", [])
        # Sort descending by start_line per design
        try:
            ops_sorted = sorted(ops, key=lambda x: int(x["start_line"]), reverse=True)
        except Exception:
            ops_sorted = ops
        # Include working_dir and target_file from history
        entry = shared["history"][-1]
        target = entry.get("params", {}).get("target_file", "")
        self._working_dir = shared["working_dir"]
        self._target = target
        return ops_sorted

    def exec(self, op):
        try:
            ok, err = util_replace_range(
                self._working_dir,
                self._target,
                int(op["start_line"]),
                int(op["end_line"]),
                str(op["replacement"]),
            )
            return {"success": ok, "error": err}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post(self, shared, prep_res, exec_res_list):
        shared["history"][-1]["result"] = exec_res_list
        shared["edit_operations"] = []
        logging.info("ApplyChangesBatchNode applied count=%s", len(exec_res_list))
        return "decide_next"


class FormatResponseNode(Node):
    def prep(self, shared):
        return shared.get("history", [])

    def exec(self, history):
        prompt = (
            "Format a concise response for the user summarizing actions taken and key results.\n"
            f"History: {history}"
        )
        return call_llm(prompt)

    def post(self, shared, prep_res, exec_res):
        shared["response"] = exec_res
        logging.info("FormatResponseNode produced response length=%s", len(exec_res) if exec_res else 0)
        return "done"