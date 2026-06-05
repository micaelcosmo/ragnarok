"""
Smoke test E2E da stack dockerizada (via nginx em :8080).
Não usa dependências externas — apenas urllib da stdlib.

Uso: python scripts/smoke_e2e.py [base_url]
Default base_url: http://localhost:8080/api/v1
"""
import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/api/v1"

falhas = []
total = 0


def chamar(metodo, caminho, corpo=None, token=None, esperado=200):
    global total
    total += 1
    url = f"{BASE}{caminho}"
    dados = json.dumps(corpo).encode() if corpo is not None else None
    requisicao = urllib.request.Request(url, data=dados, method=metodo)
    requisicao.add_header("Content-Type", "application/json")
    if token:
        requisicao.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(requisicao) as resposta:
            status = resposta.status
            payload = json.loads(resposta.read().decode())
    except urllib.error.HTTPError as erro:
        status = erro.code
        payload = json.loads(erro.read().decode() or "{}")

    marca = "OK " if status == esperado else "XX "
    if status != esperado:
        falhas.append(f"{metodo} {caminho} -> {status} (esperado {esperado}): {payload}")
    print(f"  {marca}{metodo} {caminho} -> {status}")
    return payload.get("data")


def main():
    print(f"[smoke] base = {BASE}")

    print("\n[1] Healthcheck")
    chamar("GET", "/health", esperado=200)

    print("\n[2] Login do ADMIN (seed)")
    sessao_admin = chamar("POST", "/auth/login",
                          {"email": "admin@ragnarok.local", "password": "admin123"})
    token_admin = sessao_admin["access_token"] if sessao_admin else None

    print("\n[3] Catálogo SRD carregado pelo seed")
    racas = chamar("GET", "/reference/races", token=token_admin)
    magias = chamar("GET", "/reference/spells?nivel=3", token=token_admin)
    print(f"      raças={len(racas or [])}  magias_nivel3={len(magias or [])}")

    print("\n[4] Registro + login de um JOGADOR")
    chamar("POST", "/auth/register",
           {"email": "heroi@ragnarok.local", "name": "Herói E2E", "password": "senha123"},
           esperado=201)
    sessao_jog = chamar("POST", "/auth/login",
                        {"email": "heroi@ragnarok.local", "password": "senha123"})
    token_jog = sessao_jog["access_token"] if sessao_jog else None

    print("\n[5] Criação de personagem + ficha com derivados")
    personagem = chamar("POST", "/characters",
                       {"nome": "Aelar E2E", "nivel": 5,
                        "atributos": {"for": 16, "des": 14, "con": 14},
                        "pericias_proficientes": ["Atletismo"]},
                       token=token_jog, esperado=201)
    if personagem:
        ficha = chamar("GET", f"/characters/{personagem['id']}", token=token_jog)
        mod_for = ficha["derivados"]["modificadores"]["for"] if ficha else None
        print(f"      modificador FOR (16) = {mod_for} (esperado 3)")
        if mod_for != 3:
            falhas.append(f"derivados incorretos: mod FOR={mod_for}")

    print("\n[6] Jogador NÃO pode criar mesa (403)")
    chamar("POST", "/campaigns", {"nome": "Proibida"}, token=token_jog, esperado=403)

    print("\n[7] Registro de MESTRE + criação de mesa + ingresso do jogador")
    chamar("POST", "/auth/register",
           {"email": "mestre@ragnarok.local", "name": "Mestre E2E",
            "password": "senha123", "role": "MESTRE"}, esperado=201)
    sessao_mestre = chamar("POST", "/auth/login",
                          {"email": "mestre@ragnarok.local", "password": "senha123"})
    token_mestre = sessao_mestre["access_token"] if sessao_mestre else None
    mesa = chamar("POST", "/campaigns", {"nome": "A Mina Perdida E2E"},
                 token=token_mestre, esperado=201)
    if mesa:
        chamar("POST", "/campaigns/join", {"codigo": mesa["codigo_convite"]},
               token=token_jog, esperado=200)
        chamar("POST", f"/campaigns/{mesa['id']}/personagens",
               {"personagem_id": personagem["id"]}, token=token_jog, esperado=200)
        # Mestre enxerga a ficha do jogador da sua mesa.
        chamar("GET", f"/characters/{personagem['id']}", token=token_mestre, esperado=200)
        # Mestre cria um monstro na mesa.
        chamar("POST", "/bestiary",
               {"nome": "Goblin E2E", "mesa_id": mesa["id"], "ca": 15, "pv": 7},
               token=token_mestre, esperado=201)

    print("\n[8] Admin: métricas da plataforma")
    chamar("GET", "/admin/stats", token=token_admin, esperado=200)
    chamar("GET", "/admin/stats", token=token_jog, esperado=403)

    print("\n" + "=" * 50)
    if falhas:
        print(f"[smoke] {len(falhas)} FALHA(S) de {total} chamadas:")
        for falha in falhas:
            print(f"  - {falha}")
        sys.exit(1)
    print(f"[smoke] TODAS as {total} chamadas OK ✔")


if __name__ == "__main__":
    main()
