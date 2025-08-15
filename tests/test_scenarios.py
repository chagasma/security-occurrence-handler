import json
import time
import requests
from typing import Dict

API_BASE = "http://localhost:8000"


def load_test_data():
    with open("../data/occurrence_event_alarm.json", "r") as f:
        return json.load(f)


def test_scenario(scenario_name: str, expected_status: str, test_data: Dict) -> Dict:
    print(f"\n🧪 Testando: {scenario_name}")
    print(f"📊 Status esperado: {expected_status}")

    payload = test_data.copy()
    payload["scenario"] = scenario_name

    try:
        response = requests.post(f"{API_BASE}/handle_occurrence", json=payload)
        response.raise_for_status()
        hash_id = response.json()["hash"]
        print(f"🔑 Hash gerado: {hash_id}")

        print("⏳ Aguardando processamento...")
        time.sleep(8)

        status_response = requests.get(f"{API_BASE}/status_occurrence", params={"hash": hash_id})
        status_response.raise_for_status()
        result = status_response.json()

        actual_status = result["status_final"]
        success = actual_status == expected_status

        print(f"✅ Status obtido: {actual_status}" if success else f"❌ Status obtido: {actual_status}")

        print("💬 Conversação:")
        for msg in result["mensagens"]:
            print(f"  {msg['de']}: {msg['mensagem']}")

        return {
            "scenario": scenario_name,
            "expected": expected_status,
            "actual": actual_status,
            "success": success,
            "messages": result["mensagens"]
        }

    except Exception as e:
        print(f"❌ Erro: {e}")
        return {
            "scenario": scenario_name,
            "expected": expected_status,
            "actual": "ERROR",
            "success": False,
            "error": str(e)
        }


def main():
    print("🚀 Iniciando bateria de testes de cenários")
    print("=" * 60)

    # Carrega dados de teste
    test_data = load_test_data()

    scenarios = [
        ("correct_password_ok", "RESOLVIDO"),
        ("wrong_password", "ESCALADO"),
        ("correct_password_danger", "ESCALADO"),
        ("panic_word", "ESCALADO"),
        ("who_is_auria", "RESOLVIDO")
    ]

    results = []

    for scenario_name, expected_status in scenarios:
        result = test_scenario(scenario_name, expected_status, test_data)
        results.append(result)
        time.sleep(2)

    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL")
    print("=" * 60)

    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)

    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['scenario']:25} | Esperado: {result['expected']:10} | Obtido: {result['actual']:10}")

    print(f"\n🎯 Sucessos: {success_count}/{total_count}")
    print(f"📈 Taxa de sucesso: {(success_count / total_count) * 100:.1f}%")

    if success_count == total_count:
        print("🎉 TODOS OS CENÁRIOS PASSARAM!")
    else:
        print("⚠️  Alguns cenários falharam. Verifique os logs acima.")


if __name__ == "__main__":
    main()
