from dotenv import load_dotenv
from pathlib import Path
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import logging
import uuid
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Literal

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict

# =====================================================
# DB
# =====================================================
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = "HS256"
JWT_TTL_MIN = 60 * 24 * 7  # 7 days

app = FastAPI(title="Pit Stop API")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pitstop")


# =====================================================
# Auth helpers
# =====================================================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MIN),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


bearer = HTTPBearer(auto_error=False)


async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> dict:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="Autenticação necessária")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "senha_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return user


# =====================================================
# Models (Pydantic)
# =====================================================
class RegisterIn(BaseModel):
    nome: str
    telefone: str
    senha: str


class LoginIn(BaseModel):
    telefone: str
    senha: str


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    nome: str
    telefone: str
    role: str
    pontos_fidelidade: int = 0


class AuthOut(BaseModel):
    token: str
    user: UserOut


class VeiculoIn(BaseModel):
    placa: str
    modelo: str
    cor: str
    ano: int
    categoria: Literal["Pequeno", "Médio", "Grande"]


class Veiculo(VeiculoIn):
    id: str
    usuario_id: str


class UnidadeIn(BaseModel):
    nome: str
    endereco: str
    is_ativa: bool = True


class Unidade(UnidadeIn):
    id: str


class ServicoIn(BaseModel):
    nome: str
    descricao: str
    preco_base: float


class Servico(ServicoIn):
    id: str


class OSCreate(BaseModel):
    veiculo_id: str
    unidade_id: str
    servico_ids: List[str]
    logistica_entrada: Optional[str] = "Entrega no local"
    logistica_saida: Optional[str] = "Retirada no local"
    enderecos: Optional[str] = ""


class OSStatusIn(BaseModel):
    status: Literal["Na Fila", "Preparação", "Execução", "Pronto", "Finalizado"]


class OSOverrideIn(BaseModel):
    valor_total: float


class OSPagamentoIn(BaseModel):
    status_pagamento: Literal["Pendente", "Pago"]


class OrdemServico(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    usuario_id: str
    veiculo_id: str
    unidade_id: str
    servico_ids: List[str]
    status: str
    logistica_entrada: str
    logistica_saida: str
    enderecos: str
    status_pagamento: str
    valor_total: float
    override_preco: bool = False
    created_at: str
    updated_at: str


# =====================================================
# Business logic
# =====================================================
CATEGORIA_MULTIPLIER = {"Pequeno": 1.0, "Médio": 1.3, "Grande": 1.6}
STATUS_FLOW = ["Na Fila", "Preparação", "Execução", "Pronto", "Finalizado"]


async def calc_valor_total(servico_ids: List[str], categoria: str) -> float:
    servicos = await db.servicos.find({"id": {"$in": servico_ids}}, {"_id": 0}).to_list(100)
    base = sum(float(s["preco_base"]) for s in servicos)
    mult = CATEGORIA_MULTIPLIER.get(categoria, 1.0)
    return round(base * mult, 2)


# =====================================================
# Auth routes
# =====================================================
@api.post("/auth/register", response_model=AuthOut)
async def register(data: RegisterIn):
    tel = data.telefone.strip()
    existing = await db.users.find_one({"telefone": tel})
    if existing:
        raise HTTPException(status_code=400, detail="Telefone já cadastrado")
    user = {
        "id": str(uuid.uuid4()),
        "nome": data.nome.strip(),
        "telefone": tel,
        "senha_hash": hash_password(data.senha),
        "role": "cliente",
        "pontos_fidelidade": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user)
    token = create_token(user["id"], user["role"])
    return AuthOut(token=token, user=UserOut(**user))


@api.post("/auth/login", response_model=AuthOut)
async def login(data: LoginIn):
    user = await db.users.find_one({"telefone": data.telefone.strip()})
    if not user or not verify_password(data.senha, user["senha_hash"]):
        raise HTTPException(status_code=401, detail="Telefone ou senha inválidos")
    token = create_token(user["id"], user["role"])
    return AuthOut(token=token, user=UserOut(**user))


@api.get("/auth/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    return UserOut(**user)


# =====================================================
# Veículos
# =====================================================
@api.get("/veiculos", response_model=List[Veiculo])
async def list_veiculos(user: dict = Depends(get_current_user)):
    docs = await db.veiculos.find({"usuario_id": user["id"]}, {"_id": 0}).to_list(500)
    return docs


@api.post("/veiculos", response_model=Veiculo)
async def create_veiculo(data: VeiculoIn, user: dict = Depends(get_current_user)):
    doc = {"id": str(uuid.uuid4()), "usuario_id": user["id"], **data.model_dump()}
    doc["placa"] = doc["placa"].upper().replace("-", "").strip()
    await db.veiculos.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.get("/veiculos/consulta-placa/{placa}")
async def consulta_placa(placa: str):
    """Mock preparado para integração externa (Sinesp/consulta real).
    Retorna dados fictícios baseados na placa."""
    placa = placa.upper().replace("-", "").strip()
    if len(placa) < 7:
        raise HTTPException(status_code=400, detail="Placa inválida")
    # Mock determinístico
    modelos = ["Volkswagen Gol", "Fiat Uno", "Chevrolet Onix", "Toyota Corolla", "Honda Civic", "Jeep Compass"]
    cores = ["Prata", "Preto", "Branco", "Vermelho", "Azul"]
    seed = sum(ord(c) for c in placa)
    categorias = ["Pequeno", "Médio", "Grande"]
    return {
        "placa": placa,
        "modelo": modelos[seed % len(modelos)],
        "cor": cores[seed % len(cores)],
        "ano": 2015 + (seed % 10),
        "categoria": categorias[seed % len(categorias)],
        "fonte": "mock",
    }


# =====================================================
# Unidades
# =====================================================
@api.get("/unidades", response_model=List[Unidade])
async def list_unidades():
    return await db.unidades.find({}, {"_id": 0}).to_list(100)


@api.get("/unidades/status")
async def unidades_status():
    docs = await db.unidades.find({}, {"_id": 0}).to_list(100)
    # Count OSs em execução por unidade para dar sensação de lotação
    out = []
    for u in docs:
        em_fila = await db.ordens.count_documents({
            "unidade_id": u["id"],
            "status": {"$in": ["Na Fila", "Preparação", "Execução"]},
        })
        out.append({**u, "ordens_ativas": em_fila, "disponivel": u.get("is_ativa", True)})
    return out


@api.post("/unidades", response_model=Unidade)
async def create_unidade(data: UnidadeIn, _: dict = Depends(require_admin)):
    doc = {"id": str(uuid.uuid4()), **data.model_dump()}
    await db.unidades.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.patch("/unidades/{uid}", response_model=Unidade)
async def update_unidade(uid: str, data: UnidadeIn, _: dict = Depends(require_admin)):
    await db.unidades.update_one({"id": uid}, {"$set": data.model_dump()})
    doc = await db.unidades.find_one({"id": uid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Unidade não encontrada")
    return doc


# =====================================================
# Serviços
# =====================================================
@api.get("/servicos", response_model=List[Servico])
async def list_servicos():
    return await db.servicos.find({}, {"_id": 0}).to_list(200)


@api.post("/servicos", response_model=Servico)
async def create_servico(data: ServicoIn, _: dict = Depends(require_admin)):
    doc = {"id": str(uuid.uuid4()), **data.model_dump()}
    await db.servicos.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api.patch("/servicos/{sid}", response_model=Servico)
async def update_servico(sid: str, data: ServicoIn, _: dict = Depends(require_admin)):
    await db.servicos.update_one({"id": sid}, {"$set": data.model_dump()})
    doc = await db.servicos.find_one({"id": sid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Serviço não encontrado")
    return doc


# =====================================================
# Ordens de Serviço
# =====================================================
async def _hydrate_os(os_doc: dict) -> dict:
    veic = await db.veiculos.find_one({"id": os_doc["veiculo_id"]}, {"_id": 0})
    unid = await db.unidades.find_one({"id": os_doc["unidade_id"]}, {"_id": 0})
    user = await db.users.find_one({"id": os_doc["usuario_id"]}, {"_id": 0, "senha_hash": 0})
    servs = await db.servicos.find({"id": {"$in": os_doc.get("servico_ids", [])}}, {"_id": 0}).to_list(50)
    return {**os_doc, "veiculo": veic, "unidade": unid, "cliente": user, "servicos": servs}


@api.post("/ordens-servico")
async def criar_os(data: OSCreate, user: dict = Depends(get_current_user)):
    unidade = await db.unidades.find_one({"id": data.unidade_id}, {"_id": 0})
    if not unidade:
        raise HTTPException(404, "Unidade não encontrada")
    # Kill-switch
    if not unidade.get("is_ativa", True):
        raise HTTPException(status_code=403, detail="Unidade operando na capacidade máxima")

    veic = await db.veiculos.find_one({"id": data.veiculo_id, "usuario_id": user["id"]}, {"_id": 0})
    if not veic:
        raise HTTPException(404, "Veículo não encontrado")

    valor = await calc_valor_total(data.servico_ids, veic["categoria"])
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": str(uuid.uuid4()),
        "usuario_id": user["id"],
        "veiculo_id": data.veiculo_id,
        "unidade_id": data.unidade_id,
        "servico_ids": data.servico_ids,
        "status": "Na Fila",
        "logistica_entrada": data.logistica_entrada or "Entrega no local",
        "logistica_saida": data.logistica_saida or "Retirada no local",
        "enderecos": data.enderecos or "",
        "status_pagamento": "Pendente",
        "valor_total": valor,
        "override_preco": False,
        "created_at": now,
        "updated_at": now,
    }
    await db.ordens.insert_one(doc)
    doc.pop("_id", None)
    return await _hydrate_os(doc)


@api.get("/ordens-servico")
async def listar_os(user: dict = Depends(get_current_user)):
    query = {} if user["role"] == "admin" else {"usuario_id": user["id"]}
    docs = await db.ordens.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    return [await _hydrate_os(d) for d in docs]


@api.get("/ordens-servico/{oid}")
async def get_os(oid: str, user: dict = Depends(get_current_user)):
    doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "OS não encontrada")
    if user["role"] != "admin" and doc["usuario_id"] != user["id"]:
        raise HTTPException(403, "Acesso negado")
    return await _hydrate_os(doc)


@api.patch("/ordens-servico/{oid}/status")
async def mudar_status_os(oid: str, data: OSStatusIn, _: dict = Depends(require_admin)):
    doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "OS não encontrada")
    # Bloqueio de saída
    if data.status == "Finalizado" and doc.get("status_pagamento") != "Pago":
        raise HTTPException(status_code=400, detail="Não é possível liberar: pagamento pendente")
    update = {"status": data.status, "updated_at": datetime.now(timezone.utc).isoformat()}
    await db.ordens.update_one({"id": oid}, {"$set": update})

    # Signal: fidelidade automática ao finalizar
    if data.status == "Finalizado" and doc.get("status") != "Finalizado":
        pontos_add = max(1, int(doc["valor_total"] / 10))  # 1 ponto a cada R$10
        await db.users.update_one(
            {"id": doc["usuario_id"]}, {"$inc": {"pontos_fidelidade": pontos_add}}
        )
        logger.info(f"[FIDELIDADE] +{pontos_add} pts para user {doc['usuario_id']}")

    new_doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    return await _hydrate_os(new_doc)


@api.patch("/ordens-servico/{oid}/preco")
async def override_preco_os(oid: str, data: OSOverrideIn, _: dict = Depends(require_admin)):
    if data.valor_total < 0:
        raise HTTPException(400, "Valor inválido")
    doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "OS não encontrada")
    await db.ordens.update_one(
        {"id": oid},
        {"$set": {"valor_total": round(data.valor_total, 2), "override_preco": True,
                  "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    new_doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    return await _hydrate_os(new_doc)


@api.patch("/ordens-servico/{oid}/pagamento")
async def marcar_pagamento(oid: str, data: OSPagamentoIn, _: dict = Depends(require_admin)):
    doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "OS não encontrada")
    await db.ordens.update_one(
        {"id": oid},
        {"$set": {"status_pagamento": data.status_pagamento,
                  "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    new_doc = await db.ordens.find_one({"id": oid}, {"_id": 0})
    return await _hydrate_os(new_doc)


# =====================================================
# Pix - gerador de BR Code (Copia e Cola)
# =====================================================
def _crc16(payload: str) -> str:
    poly = 0x1021
    result = 0xFFFF
    for b in payload.encode("utf-8"):
        result ^= b << 8
        for _ in range(8):
            if result & 0x8000:
                result = ((result << 1) ^ poly) & 0xFFFF
            else:
                result = (result << 1) & 0xFFFF
    return format(result, "04X")


def _tlv(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"


def _sanitize(txt: str, maxlen: int) -> str:
    import unicodedata
    nkfd = unicodedata.normalize("NFKD", txt)
    ascii_txt = "".join(c for c in nkfd if not unicodedata.combining(c))
    return ascii_txt.upper()[:maxlen]


def gerar_brcode(pix_key: str, nome: str, cidade: str, valor: float, txid: str) -> str:
    gui = _tlv("00", "br.gov.bcb.pix") + _tlv("01", pix_key)
    merchant_account = _tlv("26", gui)
    payload = (
        _tlv("00", "01")
        + merchant_account
        + _tlv("52", "0000")
        + _tlv("53", "986")
        + _tlv("54", f"{valor:.2f}")
        + _tlv("58", "BR")
        + _tlv("59", _sanitize(nome, 25))
        + _tlv("60", _sanitize(cidade, 15))
        + _tlv("62", _tlv("05", _sanitize(txid, 25)))
    )
    payload += "6304"
    crc = _crc16(payload)
    return payload + crc


class PixIn(BaseModel):
    ordem_id: str


@api.post("/pagamentos/pix")
async def gerar_pix(data: PixIn, user: dict = Depends(get_current_user)):
    doc = await db.ordens.find_one({"id": data.ordem_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "OS não encontrada")
    if user["role"] != "admin" and doc["usuario_id"] != user["id"]:
        raise HTTPException(403, "Acesso negado")
    if doc["status_pagamento"] == "Pago":
        raise HTTPException(400, "Pedido já está pago")

    txid = doc["id"].replace("-", "")[:25]
    brcode = gerar_brcode(
        pix_key=os.environ.get("PIX_KEY", "pitstop@pix.com.br"),
        nome=os.environ.get("PIX_RECEIVER_NAME", "PIT STOP"),
        cidade=os.environ.get("PIX_RECEIVER_CITY", "SAO PAULO"),
        valor=float(doc["valor_total"]),
        txid=txid,
    )
    return {
        "ordem_id": doc["id"],
        "valor": doc["valor_total"],
        "pix_copia_cola": brcode,
        "txid": txid,
        "expires_in_minutes": 15,
    }


# =====================================================
# Admin: lista de clientes
# =====================================================
@api.get("/admin/clientes")
async def admin_clientes(_: dict = Depends(require_admin)):
    docs = await db.users.find(
        {"role": "cliente"}, {"_id": 0, "senha_hash": 0}
    ).to_list(1000)
    return docs


# =====================================================
# Seed
# =====================================================
async def seed():
    # Admin
    if not await db.users.find_one({"telefone": os.environ["ADMIN_PHONE"]}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "nome": "Admin Pit Stop",
            "telefone": os.environ["ADMIN_PHONE"],
            "senha_hash": hash_password(os.environ["ADMIN_PASSWORD"]),
            "role": "admin",
            "pontos_fidelidade": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("[SEED] admin criado")

    # Cliente demo
    demo = await db.users.find_one({"telefone": os.environ["DEMO_PHONE"]})
    if not demo:
        demo_id = str(uuid.uuid4())
        await db.users.insert_one({
            "id": demo_id,
            "nome": "Cliente Demo",
            "telefone": os.environ["DEMO_PHONE"],
            "senha_hash": hash_password(os.environ["DEMO_PASSWORD"]),
            "role": "cliente",
            "pontos_fidelidade": 120,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        # Veículos demo
        await db.veiculos.insert_many([
            {"id": str(uuid.uuid4()), "usuario_id": demo_id, "placa": "ABC1D23",
             "modelo": "Honda Civic", "cor": "Preto", "ano": 2022, "categoria": "Médio"},
            {"id": str(uuid.uuid4()), "usuario_id": demo_id, "placa": "XYZ4E56",
             "modelo": "Jeep Compass", "cor": "Prata", "ano": 2021, "categoria": "Grande"},
        ])
        logger.info("[SEED] cliente demo + veículos criados")

    # Unidades
    if await db.unidades.count_documents({}) == 0:
        await db.unidades.insert_many([
            {"id": str(uuid.uuid4()), "nome": "Pit Stop Vila Olímpia",
             "endereco": "Rua Fradique Coutinho, 123 - Vila Olímpia, SP", "is_ativa": True},
            {"id": str(uuid.uuid4()), "nome": "Pit Stop Pinheiros",
             "endereco": "Av. Rebouças, 1500 - Pinheiros, SP", "is_ativa": True},
        ])
        logger.info("[SEED] unidades criadas")

    # Serviços
    if await db.servicos.count_documents({}) == 0:
        await db.servicos.insert_many([
            {"id": str(uuid.uuid4()), "nome": "Lavagem Simples",
             "descricao": "Lavagem externa com cera", "preco_base": 40.0},
            {"id": str(uuid.uuid4()), "nome": "Lavagem Completa",
             "descricao": "Externa + interna + aspiração", "preco_base": 80.0},
            {"id": str(uuid.uuid4()), "nome": "Enceramento Premium",
             "descricao": "Polimento + cera de carnaúba", "preco_base": 180.0},
            {"id": str(uuid.uuid4()), "nome": "Detalhamento Completo",
             "descricao": "Estética automotiva full detail", "preco_base": 350.0},
        ])
        logger.info("[SEED] serviços criados")


@app.on_event("startup")
async def on_startup():
    await db.users.create_index("telefone", unique=True)
    await db.veiculos.create_index([("usuario_id", 1)])
    await db.ordens.create_index([("usuario_id", 1), ("status", 1)])
    await seed()
    logger.info("Pit Stop API iniciada")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()


# health
@api.get("/")
async def root():
    return {"service": "Pit Stop API", "status": "ok"}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
