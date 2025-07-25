#!/usr/bin/env python3
"""
Script para investigar a classe RunResponse correta do framework AGNO
"""

import inspect
from agno.workflow import Workflow, RunResponse

print("=== INVESTIGAÇÃO DA CLASSE RUNRESPONSE ===\n")

# 1. Verificar o construtor da classe RunResponse
print(f"RunResponse class: {RunResponse}")
print(f"RunResponse.__doc__: {RunResponse.__doc__}")
print(f"RunResponse.__init__ signature: {inspect.signature(RunResponse.__init__)}")

# 2. Verificar métodos e atributos
print(f"\nMétodos da classe RunResponse:")
for method in dir(RunResponse):
    if not method.startswith('_') or method == '__init__':
        print(f"  - {method}")

# 3. Tentar criar uma instância para ver os parâmetros necessários
print("\n=== TESTANDO CONSTRUTOR ===\n")

try:
    # Testar com apenas content
    response1 = RunResponse(content="Teste de conteúdo")
    print("✅ RunResponse(content='...') funcionou")
    print(f"   response1.content: {response1.content}")
except Exception as e:
    print(f"❌ RunResponse(content='...') falhou: {e}")

try:
    # Testar sem parâmetros
    response2 = RunResponse()
    print("✅ RunResponse() funcionou")
except Exception as e:
    print(f"❌ RunResponse() falhou: {e}")

try:
    # Testar com parâmetros nomeados
    response3 = RunResponse(content="Teste", agent_id="test_agent")
    print("✅ RunResponse(content='...', agent_id='...') funcionou")
except Exception as e:
    print(f"❌ RunResponse(content='...', agent_id='...') falhou: {e}")

print("\n=== VERIFICAÇÃO DE ATRIBUTOS OBRIGATÓRIOS ===\n")

# 4. Verificar quais atributos são obrigatórios
try:
    response = RunResponse(content="Teste")
    print("Atributos disponíveis na instância:")
    for attr in dir(response):
        if not attr.startswith('_'):
            try:
                value = getattr(response, attr)
                if not callable(value):
                    print(f"  - {attr}: {value} (tipo: {type(value)})")
            except:
                print(f"  - {attr}: <não acessível>")
except Exception as e:
    print(f"Erro ao criar instância: {e}")

print("\n=== INVESTIGAÇÃO COMPLETA ===\n")