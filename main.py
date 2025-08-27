import logging
import os
from flow import create_qa_flow, coding_agent_flow
from nodes import get_initial_shared

# Example main function
# Please replace this with your own main function
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # Example: run coding agent flow
    working_dir = os.path.abspath(os.path.dirname(__file__))
    user_query = input("Describe your coding request: ")
    shared = get_initial_shared(working_dir=working_dir, user_query=user_query)

    flow = coding_agent_flow
    flow.run(shared)

    print("\n=== Final Response ===")
    print(shared.get("response", ""))
    print("\n=== Action History ===")
    for i, h in enumerate(shared.get("history", []), start=1):
        print(f"{i}. tool={h.get('tool')} reason={h.get('reason')}\n   params={h.get('params')}\n   result_keys={list((h.get('result') or {}).keys()) if isinstance(h.get('result'), dict) else type(h.get('result'))}")

if __name__ == "__main__":
    main()
