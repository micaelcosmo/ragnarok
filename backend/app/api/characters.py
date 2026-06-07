"""Endpoints de Personagens (ficha 5E). Ownership por jogador; mestre vê os da sua mesa."""
from flask import Blueprint, Response, request

from app.extensions import db
from app.models.campaign import Mesa
from app.models.character import Personagem
from app.utils.auth import auth_required, current_user
from app.utils.errors import Forbidden, NotFound, ValidationError
from app.utils.responses import corpo_json, created, ok

bp = Blueprint("characters", __name__)

# Mapa atributo curto -> coluna do model.
_ATRIBUTOS = Personagem.ATRIBUTOS_COLUNAS

# Campos simples atualizáveis diretamente do corpo.
_CAMPOS_TEXTO = (
    "nome", "nome_jogador", "raca_slug", "subraca_slug", "classe_slug", "antecedente_slug",
    "tendencia", "deslocamento", "dado_vida", "outras_proficiencias",
    "classe_conjuradora", "atributo_conjuracao", "tracos_personalidade",
    "ideais", "vinculos", "fraquezas", "historia", "caracteristicas",
    "idiomas", "equipamento", "ataques", "dinheiro", "avatar_url",
    "idade", "altura", "peso", "olhos", "pele", "cabelo", "faccao",
    "aparencia", "aliados", "tesouro", "simbolo_faccao_url",
)
_CAMPOS_INT = (
    "nivel", "xp", "ca", "ca_ajuste", "iniciativa_bonus", "pv_max", "pv_atual", "pv_temp",
)
_CAMPOS_LISTA = (
    "pericias_proficientes", "salvaguardas_proficientes", "truques", "magias", "talentos",
    "tracos_extras",
)


def _personagem_acessivel(personagem, usuario):
    """Dono, ADMIN ou mestre da mesa do personagem podem acessar."""
    if usuario.is_admin or personagem.user_id == usuario.id:
        return True
    if personagem.mesa_id is not None:
        mesa = Mesa.query.get(personagem.mesa_id)
        if mesa is not None and mesa.mestre_id == usuario.id:
            return True
    return False


def _aplicar_campos(personagem, dados):
    """Aplica os campos enviados ao personagem (POO: encapsula a atribuição)."""
    for campo in _CAMPOS_TEXTO:
        if campo in dados:
            setattr(personagem, campo, dados[campo])
    for campo in _CAMPOS_INT:
        if campo in dados and dados[campo] is not None:
            try:
                setattr(personagem, campo, int(dados[campo]))
            except (TypeError, ValueError):
                pass
    for campo in _CAMPOS_LISTA:
        if campo in dados and isinstance(dados[campo], list):
            setattr(personagem, campo, dados[campo])
    if "inspiracao" in dados:
        personagem.inspiracao = bool(dados["inspiracao"])

    atributos = dados.get("atributos")
    if isinstance(atributos, dict):
        for chave, coluna in _ATRIBUTOS.items():
            if chave in atributos and atributos[chave] is not None:
                try:
                    setattr(personagem, coluna, int(atributos[chave]))
                except (TypeError, ValueError):
                    pass

    # ASI: valida/clampa a pool contra o orçamento do nível e o teto 20 (após nível/atributos acima).
    if "bonus_atributos_manuais" in dados and isinstance(dados["bonus_atributos_manuais"], dict):
        from app.rules import dnd5e

        pontos = dnd5e.asi_pontos_por_nivel(personagem.nivel)
        personagem.bonus_atributos_manuais = dnd5e.sanear_asi(
            dados["bonus_atributos_manuais"], pontos, personagem.atributos_dict()
        )

    # Recursos de classe: valida/clampa a lista (nome/max/atual/recarga).
    if "recursos" in dados and isinstance(dados["recursos"], list):
        from app.rules import dnd5e

        personagem.recursos = dnd5e.sanear_recursos(dados["recursos"])

    # Estado de combate (E31): clampa morte (0–3) e exaustão (0–6).
    from app.rules import dnd5e as _regras
    if "mortes_sucesso" in dados:
        personagem.mortes_sucesso = _regras.clamp_morte(dados["mortes_sucesso"])
    if "mortes_falha" in dados:
        personagem.mortes_falha = _regras.clamp_morte(dados["mortes_falha"])
    if "exaustao" in dados:
        personagem.exaustao = _regras.clamp_exaustao(dados["exaustao"])

    # Moedas estruturadas (E33).
    if "moedas" in dados and isinstance(dados["moedas"], dict):
        personagem.moedas = _regras.sanear_moedas(dados["moedas"])

    # Galeria de imagens (E34).
    if "imagens" in dados and isinstance(dados["imagens"], list):
        personagem.imagens = _regras.sanear_imagens(dados["imagens"])

    # Multiclasse (E35).
    if "classes_extras" in dados and isinstance(dados["classes_extras"], list):
        personagem.classes_extras = _regras.sanear_classes_extras(dados["classes_extras"])


@bp.get("/characters")
@auth_required
def listar():
    """Lista personagens do usuário; mestre pode filtrar por `?mesa_id=`."""
    usuario = current_user()
    mesa_id = request.args.get("mesa_id")

    if mesa_id:
        mesa = Mesa.query.get(int(mesa_id))
        if mesa is None:
            raise NotFound("Mesa não encontrada.")
        if not (usuario.is_admin or mesa.mestre_id == usuario.id or mesa.tem_membro(usuario.id)):
            raise Forbidden("Você não participa desta mesa.")
        personagens = Personagem.query.filter_by(mesa_id=mesa.id).all()
    else:
        personagens = Personagem.query.filter_by(user_id=usuario.id).all()

    return ok(
        [personagem.to_dict(incluir_derivados=False) for personagem in personagens],
        meta={"total": len(personagens)},
    )


@bp.post("/characters")
@auth_required
def criar():
    """Cria um personagem para o usuário atual."""
    dados = corpo_json(["nome"])
    personagem = Personagem(user_id=current_user().id, nome=dados["nome"])
    _aplicar_campos(personagem, dados)
    # PV inicial coerente se não enviado.
    if personagem.pv_atual in (None, 0):
        personagem.pv_atual = personagem.pv_max
    db.session.add(personagem)
    db.session.commit()
    return created(personagem.to_dict())


@bp.get("/characters/<int:personagem_id>")
@auth_required
def obter(personagem_id):
    """Retorna a ficha completa com campos derivados."""
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not _personagem_acessivel(personagem, current_user()):
        raise Forbidden("Você não pode ver este personagem.")
    return ok(personagem.to_dict())


@bp.get("/characters/<int:personagem_id>/pdf")
@auth_required
def exportar_pdf(personagem_id):
    """Exporta a ficha em PDF (estilo oficial 5E). Dono/ADMIN/mestre da mesa."""
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not _personagem_acessivel(personagem, current_user()):
        raise Forbidden("Você não pode exportar este personagem.")

    from app.services.ficha_pdf import FichaPDF

    gerador = FichaPDF(personagem)
    pdf = gerador.render_pdf()
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{gerador.nome_arquivo()}"'},
    )


@bp.put("/characters/<int:personagem_id>")
@auth_required
def atualizar(personagem_id):
    """Atualiza a ficha (somente dono ou ADMIN)."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode editar este personagem.")
    dados = corpo_json()
    _aplicar_campos(personagem, dados)
    db.session.commit()
    return ok(personagem.to_dict())


def _usavel_pelo_personagem(modelo, item_id, personagem):
    """Item é usável se for global (sem dono) ou pertencer a este personagem."""
    item = modelo.query.get(int(item_id))
    if item is None:
        return None
    ehGlobal = item.personagem_id is None and item.mesa_id is None
    if ehGlobal or item.personagem_id == personagem.id:
        return item
    return None


@bp.post("/characters/<int:personagem_id>/equipar")
@auth_required
def equipar(personagem_id):
    """Equipa uma arma (adiciona) ou armadura (substitui) — aplica CA/ataque na ficha."""
    from app.models.items import Arma, Armadura

    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode equipar itens deste personagem.")
    dados = corpo_json(["tipo", "item_id"])

    if dados["tipo"] == "armadura":
        if _usavel_pelo_personagem(Armadura, dados["item_id"], personagem) is None:
            raise NotFound("Armadura indisponível para este personagem.")
        personagem.armadura_equipada_id = int(dados["item_id"])
    elif dados["tipo"] == "arma":
        if _usavel_pelo_personagem(Arma, dados["item_id"], personagem) is None:
            raise NotFound("Arma indisponível para este personagem.")
        equipadas = list(personagem.armas_equipadas or [])
        if int(dados["item_id"]) not in equipadas:
            equipadas.append(int(dados["item_id"]))
        personagem.armas_equipadas = equipadas
    else:
        raise ValidationError("tipo deve ser 'arma' ou 'armadura'.")

    db.session.commit()
    return ok(personagem.to_dict())


@bp.post("/characters/<int:personagem_id>/desequipar")
@auth_required
def desequipar(personagem_id):
    """Remove uma arma equipada ou tira a armadura."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode alterar este personagem.")
    dados = corpo_json(["tipo"])
    if dados["tipo"] == "armadura":
        personagem.armadura_equipada_id = None
    elif dados["tipo"] == "arma":
        equipadas = [a for a in (personagem.armas_equipadas or []) if a != int(dados.get("item_id", -1))]
        personagem.armas_equipadas = equipadas
    db.session.commit()
    return ok(personagem.to_dict())


def _editavel_ou_403(personagem_id):
    """Carrega o personagem e exige dono/ADMIN (helper para ações de ficha)."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode alterar este personagem.")
    return personagem


@bp.post("/characters/<int:personagem_id>/recursos/ajustar")
@auth_required
def ajustar_recurso(personagem_id):
    """Gasta/recupera um uso de um recurso (atual += delta, clampado a [0, max])."""
    personagem = _editavel_ou_403(personagem_id)
    dados = corpo_json(["indice", "delta"])
    recursos = list(personagem.recursos or [])
    try:
        indice = int(dados["indice"])
        delta = int(dados["delta"])
    except (TypeError, ValueError):
        raise ValidationError("indice e delta devem ser inteiros.")
    if not (0 <= indice < len(recursos)):
        raise NotFound("Recurso não encontrado.")
    recurso = dict(recursos[indice])
    maximo = int(recurso.get("max", 0) or 0)
    recurso["atual"] = max(0, min(maximo, int(recurso.get("atual", 0) or 0) + delta))
    recursos[indice] = recurso
    personagem.recursos = recursos
    db.session.commit()
    return ok(personagem.to_dict())


@bp.post("/characters/<int:personagem_id>/descanso")
@auth_required
def descanso(personagem_id):
    """Descanso curto/longo: recarrega recursos por tipo; o longo também restaura o PV."""
    from app.rules import dnd5e

    personagem = _editavel_ou_403(personagem_id)
    dados = corpo_json(["tipo"])
    tipo = dados["tipo"]
    if tipo not in ("curto", "longo"):
        raise ValidationError("tipo deve ser 'curto' ou 'longo'.")
    personagem.recursos = dnd5e.aplicar_descanso(personagem.recursos or [], tipo)
    if tipo == "longo":
        personagem.pv_atual = personagem.pv_max
    db.session.commit()
    return ok(personagem.to_dict())


@bp.delete("/characters/<int:personagem_id>")
@auth_required
def remover(personagem_id):
    """Remove a ficha (somente dono ou ADMIN)."""
    usuario = current_user()
    personagem = Personagem.query.get(personagem_id)
    if personagem is None:
        raise NotFound("Personagem não encontrado.")
    if not (usuario.is_admin or personagem.user_id == usuario.id):
        raise Forbidden("Você não pode remover este personagem.")
    db.session.delete(personagem)
    db.session.commit()
    return ok({"removido": personagem_id})
