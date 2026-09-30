from typing import List, Optional, Any
from pydantic import BaseModel, Field


class EnderecoRedeSchema(BaseModel):
    endereco: Optional[str] = None
    mascara: Optional[str] = None
    broadcast: Optional[str] = None


class InterfaceRedeSchema(BaseModel):
    nome: Optional[str] = "Interface"
    enderecos: List[EnderecoRedeSchema] = Field(default_factory=list)


class CpuSchema(BaseModel):
    uso: Optional[float] = 0.0
    nucleos: Optional[int] = None
    threads: Optional[int] = None


class RamSchema(BaseModel):
    total_gb: Optional[float] = None
    uso_percentual: Optional[float] = 0.0
    disponivel_gb: Optional[float] = None


class ArmazenamentoSchema(BaseModel):
    total_gb: Optional[float] = None
    uso_percentual: Optional[float] = 0.0
    livre_gb: Optional[float] = None


class TempoLigadoSchema(BaseModel):
    horas: Optional[int] = 0
    minutos: Optional[int] = 0


class AplicativoSchema(BaseModel):
    pid: Optional[int] = None
    nome: Optional[str] = ""
    usuario: Optional[str] = None
    caminho_executavel: Optional[str] = None


class NavegacaoSchema(BaseModel):
    url: Optional[str] = ""
    titulo: Optional[str] = ""
    acessado_em: Optional[str] = None
    navegador: Optional[str] = None


class ArquivoAbertoSchema(BaseModel):
    caminho: Optional[str] = ""
    processo: Optional[str] = None
    pid: Optional[int] = None
    usuario: Optional[str] = None


class DesktopRegistroSchema(BaseModel):
    nome: str
    identificador: Optional[str] = None
    ip: Optional[str] = None
    sistema_operacional: Optional[str] = None
    cpu: Optional[CpuSchema] = None
    ram: Optional[RamSchema] = None
    armazenamento: Optional[ArmazenamentoSchema] = None
    tempo_ligado: Optional[TempoLigadoSchema] = None
    interfaces_rede: List[InterfaceRedeSchema] = Field(default_factory=list)
    aplicativos: List[AplicativoSchema] = Field(default_factory=list)
    navegacao: List[NavegacaoSchema] = Field(default_factory=list)
    arquivos: List[ArquivoAbertoSchema] = Field(default_factory=list)
    arquivos_abertos: Optional[List[ArquivoAbertoSchema]] = None
    ultima_atividade: Optional[str] = None
    status: Optional[str] = None