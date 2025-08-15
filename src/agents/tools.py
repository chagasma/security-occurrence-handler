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


@tool
def validate_security_keyword(client_response: str, correct_answer: str, panic_answer: str) -> Dict:
    """
    Valida a palavra-chave de segurança fornecida pelo cliente.

    Args:
        client_response: Resposta do cliente
        correct_answer: Resposta correta esperada
        panic_answer: Resposta que indica situação de pânico

    Returns:
        Dict com resultado da validação
    """
    try:
        response_clean = client_response.strip().lower()
        correct_clean = correct_answer.strip().lower()
        panic_clean = panic_answer.strip().lower()

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
