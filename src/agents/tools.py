from typing import Dict, Literal

from langchain.tools import tool


@tool
def set_final_status(status: Literal["ESCALADO", "RESOLVIDO"], reason: str = "") -> Dict:
    """
    Define o status final do atendimento.

    Args:
        status: Status final - "ESCALADO" ou "RESOLVIDO"
        reason: Motivo opcional para o status

    Returns:
        Dict confirmando a definição do status
    """
    try:
        valid_statuses = ["ESCALADO", "RESOLVIDO"]

        if status not in valid_statuses:
            return {
                "error": f"Status inválido. Use: {', '.join(valid_statuses)}"
            }

        return {
            "status_final": status,
            "reason": reason,
            "message": f"Status definido como {status}. Atendimento finalizado."
        }
    except Exception as e:
        return {"error": str(e)}
