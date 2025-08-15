from typing import Dict, Literal, Annotated

from langchain.tools import tool
from langgraph.prebuilt import InjectedState

from src.agents.states import ResponsibleInfo


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


@tool
def validate_security_keyword(responsible_info: Annotated[ResponsibleInfo, InjectedState("responsible_info")], client_response: str) -> Dict:
    """
    Valida a palavra-chave de segurança fornecida pelo cliente.

    Returns:
        Dict com resultado da validação
    """
    try:
        correct_answer = responsible_info.correct_answer
        panic_answer = responsible_info.panic_answer

        correct_clean = correct_answer.strip().lower()
        panic_clean = panic_answer.strip().lower()

        response_clean = client_response.strip().lower()

        if response_clean == correct_clean:
            return {
                "validation_result": "CORRECT",
                "message": "Palavra-chave correta. Prosseguindo com atendimento."
            }
        elif response_clean == panic_clean:
            return {
                "validation_result": "PANIC",
                "message": "Palavra de pânico detectada. Escalando imediatamente."
            }
        else:
            return {
                "validation_result": "INCORRECT",
                "message": "Palavra-chave incorreta. Escalando por segurança."
            }
    except Exception as e:
        return {
            "validation_result": "ERROR",
            "message": f"Erro na validação: {str(e)}"
        }
