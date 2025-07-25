#!/usr/bin/env python3
"""
Script para testar diferentes hostnames do Supabase.
"""

import socket
import sys
from urllib.parse import urlparse

def test_hostname(hostname):
    """Testa se um hostname pode ser resolvido."""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ {hostname} -> Erro: {e}")
        return False

def main():
    print("=== Teste de Resolução DNS para Supabase ===")
    
    project_id = "fjrqrgjydsgkixmuowub"
    
    # Diferentes variações de hostname para testar
    hostnames_to_test = [
        f"{project_id}.supabase.co",
        f"db.{project_id}.supabase.co",
        f"aws-0-us-east-1.pooler.supabase.com",
        f"{project_id}.pooler.supabase.com",
        "google.com",  # Teste de controle
    ]
    
    print("\nTestando resolução DNS:")
    for hostname in hostnames_to_test:
        test_hostname(hostname)
    
    print("\n=== Testando conectividade TCP ===")
    
    # Testar conectividade TCP nas portas 5432 e 6543
    ports_to_test = [5432, 6543]
    
    for port in ports_to_test:
        print(f"\nTestando porta {port}:")
        for hostname in hostnames_to_test[:4]:  # Excluir google.com
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result == 0:
                    print(f"✅ {hostname}:{port} -> Conectável")
                else:
                    print(f"❌ {hostname}:{port} -> Não conectável (código: {result})")
            except Exception as e:
                print(f"❌ {hostname}:{port} -> Erro: {e}")

if __name__ == "__main__":
    main()