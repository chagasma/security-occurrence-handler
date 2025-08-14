from typing import Dict

from langchain.tools import tool


@tool
def set_final_status() -> Dict:
    """
    Define o status final do atendimento.
    """
    try:
        pass
    except Exception as e:
        return {"error": str(e)}
