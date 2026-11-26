from typing import List, Optional
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
    nome: str = Field(min_length=1, max_length=255)
    identificador: Optional[str] = Field(default= None, max_length=255)
    ip: Optional[str] = None
    sistema_operacional: Optional[str] = None
    cpu: Optional[CpuSchema] = None
    ram: Optional[RamSchema] = None
    armazenamento: Optional[ArmazenamentoSchema] = None
    tempo_ligado: Optional[TempoLigadoSchema] = None
    interfaces_rede: List[InterfaceRedeSchema] = Field(default_factory=list, max_length=100)
    aplicativos: List[AplicativoSchema] = Field(default_factory=list, max_length=2000)
    navegacao: List[NavegacaoSchema] = Field(default_factory=list, max_length=500)
    arquivos: List[ArquivoAbertoSchema] = Field(default_factory=list, max_length=1000)
    arquivos_abertos: Optional[List[ArquivoAbertoSchema]] = Field(default=None, max_length=1000)
    ultima_atividade: Optional[str] = None
    status: Optional[str] = None