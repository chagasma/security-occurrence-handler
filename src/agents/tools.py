from typing import Literal, Annotated

from langchain.tools import tool
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId

from langchain_core.messages import ToolMessage

from src.agents.states import ResponsibleInfo


@tool
def set_final_status(
        tool_call_id: Annotated[str, InjectedToolCallId],
        status: Literal["ESCALADO", "RESOLVIDO"],
        reason: str = ""
) -> Command:
    """
    Define o status final do atendimento.

    Returns:
        Command atualizando o status final
    """
    try:
        valid_statuses = ["ESCALADO", "RESOLVIDO"]

        if status not in valid_statuses:
            error_msg = f"Status inválido. Use: {', '.join(valid_statuses)}"
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=error_msg,
                            name="set_final_status",
                            tool_call_id=tool_call_id
                        )
                    ]
                }
            )

        success_msg = f"Status definido como {status}. Atendimento finalizado."

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=success_msg,
                        name="set_final_status",
                        tool_call_id=tool_call_id
                    )
                ],
                "status_final": status
            }
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Erro: {str(e)}",
                        name="set_final_status",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )


@tool
def validate_security_keyword(
        responsible_info: Annotated[ResponsibleInfo, InjectedState("responsible_info")],
        tool_call_id: Annotated[str, InjectedToolCallId],
        client_response: str
) -> Command:
    """
    Valida a palavra-chave de segurança fornecida pelo cliente.

    Returns:
        Command com resultado da validação
    """
    try:
        correct_answer = responsible_info.correct_answer
        panic_answer = responsible_info.panic_answer

        correct_clean = correct_answer.strip().lower()
        panic_clean = panic_answer.strip().lower()
        response_clean = client_response.strip().lower()

        if response_clean == correct_clean:
            result = "CORRECT"
            message = "Palavra-chave correta. Prosseguindo com atendimento."
        elif response_clean == panic_clean:
            result = "PANIC"
            message = "Palavra de pânico detectada. Escalando imediatamente."
        else:
            result = "INCORRECT"
            message = "Palavra-chave incorreta. Escalando por segurança."

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f'{{"validation_result": "{result}", "message": "{message}"}}',
                        name="validate_security_keyword",
                        tool_call_id=tool_call_id
                    )
                ],
                "validation_result": result
            }
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f'{{"validation_result": "ERROR", "message": "Erro na validação: {str(e)}"}}',
                        name="validate_security_keyword",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )
