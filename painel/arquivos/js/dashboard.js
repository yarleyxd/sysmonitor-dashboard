"use strict";
const INTERVALO_ATUALIZACAO_MS = 5000;
const CHAVE_TEMA = "sysmonitor-tema";

const lista = document.getElementById("lista-computadores");
const totalComputadores = document.getElementById("total-computadores");
const computadoresOnline = document.getElementById("computadores-online");
const computadoresOffline = document.getElementById("computadores-offline");
const cpuMedia = document.getElementById("cpu-media");
const ramMedia = document.getElementById("ram-media");
const barraOnline = document.getElementById("barra-online");
const statusServidor = document.getElementById("status-servidor");
const ultimaAtualizacao = document.getElementById("ultima-atualizacao");
const indicadorConexao = document.getElementById("indicador-conexao");
const avisoConexao = document.getElementById("aviso-conexao");
const contagemResultados = document.getElementById("contagem-resultados");
const campoBusca = document.getElementById("busca");
const seletorOrdenacao = document.getElementById("ordenacao");
const botoesFiltro = document.querySelectorAll(".filtro");
const botaoTema = document.getElementById("botao-tema");

const detalhesAbertos = new Set();
const abaAtiva = new Map();
const posicoesRolagem = new Map();
const estado = {busca: "", filtro: "todos", ordem: "nome"};
let desktopsAtuais = [];


function criarElemento(tag, classe, texto) {
    const elemento = document.createElement(tag);

    if (classe) {
        elemento.className = classe;
    }

    if (texto !== undefined) {
        elemento.textContent = texto;
    }

    return elemento;
}

function listaSegura(valor) {
    return Array.isArray(valor)
    ? valor
    : [];
}

function numeroOuNulo(valor) {
    const numero = Number(valor);
    return valor !== null && valor !== undefined && Number.isFinite(numero)
    ? numero
    : null
}

function formatarPercentual(valor) {
    const numero = numeroOuNulo(valor);

    if (numero === null) {
        return "N/D";
    }

    return numero.toLocaleString("pt-BR", {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
    }) + "%";
}

function formatarGb(valor) {
    const numero = numeroOuNulo(valor);

    if (numero === null) {
        return "N/D";
    }

    return numero.toLocaleString("pt-BR", {maximumFractionDigits: 1}) + "GB";
}

function formatarData(data) {
    if (!data) {
        return "Não informado";
    }

    const dataConvertida = new Date(data);

    if (Number.isNaN(dataConvertida.getTime())) {
        return "Não informado";
    }

    return dataConvertida.toLocaleString("pt-BR");
}

function formatarTempoLigado(tempo) {
    if (!tempo) {
        return "Não informado";
    }

    const horas = Number(tempo.horas);
    const minutos = Number(tempo.minutos);

    if (!Number.isFinite(horas) || !Number.isFinite(minutos)) {
        return "Não informado";
    }

    return `${horas}h ${minutos}min`;
}

function tempoRelativo(data) {
    if(!data) {
        return "sem registro";
    }

    const instante = new Date(data).getTime();

    if (Number.isNaN(instante)) {
        return "sem registro";
    }

    const segundos = Math.max(0, Math.round((Date.now() - instante) / 1000 ));

    if (segundos < 10) return "agora";
    if (segundos < 60) return `há ${segundos} s`;

    const minutos = Math.floor(segundos / 60);
    if (minutos < 60) return `há ${minutos} min`;

    const horas = Math.floor(minutos / 60);
    if (horas < 24) return `há ${horas} h`;

    return `há ${Math.floor(horas / 24)} d`;
}

function nivelUso(valor) {
    const numero = numeroOuNulo(valor);

    if (numero === null) return "nd";
    if (numero >= 90) return "critico";
    if (numero >= 70) return "alerta";
    return "normal";
}

function chaveDesktop(desktop) {
    return desktop.identificador || desktop.nome || "";
}

function estaOnline(desktop) {
    return desktop.status === "Online";
}

function aplicarTema(tema) {
    document.documentElement.dataset.tema = tema;
    botaoTema.setAttribute("aria-pressed", String(tema === "escuro"));
    
    try {
        localStorage.setItem(CHAVE_TEMA, tema);
    } catch (erro) {

    }
}

botaoTema.addEventListener("click", () => {
    const atual = document.documentElement.dataset.tema;
    aplicarTema(atual === "escuro" ? "claro" : "escuro");
});

botaoTema.setAttribute(
    "aria-pressed", 
    String(document.documentElement.dataset.tema === "escuro")
);

function linhaInfo(rotulo, valor, titulo) {
    const linha = criarElemento("div", "info-linha");
    linha.appendChild(criarElemento("span", "info-rotulo", rotulo));

    const conteudo = criarElemento("span", "info-valor", valor);
    if (titulo) {
        conteudo.title = titulo;
    }

    linha.appendChild(conteudo);
    return linha;
}

function criarIndicador(titulo, percentual, detalhe) {
    const nivel = nivelUso(percentual);
    const numero = numeroOuNulo(percentual);

    const indicador = criarElemento("div", "indicador-hardware");

    indicador.appendChild(criarElemento("span", "nome-indicador", titulo));
    indicador.appendChild(
        criarElemento("span",`valor-indicador nivel-${nivel}`, formatarPercentual(percentual))
    );

    const barra = criarElemento("div", "barra");
    barra.setAttribute("role", "progressbar");
    barra.setAttribute("aria-label", titulo);
    barra.setAttribute("aria-valuemin", "0");
    barra.setAttribute("aria-valuemax", "100");

    const preenchimento = criarElemento("div", `preenchimento nivel-${nivel}`);

    if (numero !== null) {
        const largura = Math.min(100, Math.max(0, numero));
        preenchimento.style.width = `${largura}%`;
        barra.setAttribute("aria-valuenow", String(Math.round(largura)));
    }

    barra.appendChild(preenchimento);
    indicador.appendChild(barra);

    if (detalhe) {
        indicador.appendChild(criarElemento("span", "detalhe-indicador", detalhe));
    }

    return indicador;
}

function detalheRam(ram) {
    const total = numeroOuNulo(ram?.total_gb);
    const disponivel = numeroOuNulo(ram?.disponivel_gb);

    if (total === null || disponivel === null) {
        return "";
    }

    return `${formatarGb(total - disponivel)} de ${formatarGb(total)} em uso`;
}

function detalheDisco(armazenamento) {
    const total = numeroOuNulo(armazenamento?.total_gb);
    const livre = numeroOuNulo(armazenamento?.livre_gb);

    if (total === null || livre === null) {
        return "";
    }

    return `${formatarGb(livre)} livres de ${formatarGb(total)}`;
}

function detalheCpu(cpu) {
    const nucleos = numeroOuNulo(cpu?.nucleos);
    const threads = numeroOuNulo(cpu?.threads);

    if (nucleos === null || threads === null) {
        return `${nucleos} núcleos / ${threads}`;
    }
}

function criarItemAplicativo(aplicativo) {
    const item = criarElemento("div", "item-lista");
    const linha = criarElemento("div", "item-linha");

    linha.appendChild(criarElemento("span", "item-principal", aplicativo.nome || "Desconhecido"));
    linha.appendChild(criarElemento("span", "item-pid", `PID ${aplicativo.pid ?? "N/D"}`));

    item.appendChild(linha);
    return item;
}

function criarItemNavegacao(registro) {
    const item = criarElemento("div", "item-lista");

    const url = criarElemento("span", "item-principal", registro.url || "N/D");
    url.title = registro.url || "";

    item.appendChild(url);
    item.appendChild(
        criarElemento(
            "span",
            "item-secundario",
            `${registro.navegador || "N/D"} • ${formatarData(registro.acessado_em)}`
        )
    );

    return item;
}

function criarItemArquivo(arquivo) {
    const item = criarElemento("div", "item-lista");

    const caminho = criarElemento("span", "item-principal", arquivo.caminho || "N/D");
    caminho.title = arquivo.caminho || "";

    item.appendChild(caminho);
    item.appendChild(
        criarElemento(
            "span",
            "item-secundario",
            `${arquivo.processo || "N/D"} (PID ${arquivo.pid ?? "N/D"})`
        )
    );

    return item;
}

function criarAbas(desktop, chave) {
    const abas = [
        {
            id: "aplicativos",
            titulo: "Aplicativos",
            itens: listaSegura(desktop.aplicativos),
            criarItem: criarItemAplicativo,
            vazio: "Nenhum aplicativo identificado.",
        },
        {
            id: "navegacao",
            titulo: "Navegação",
            itens: listaSegura(desktop.navegacao),
            criarItem: criarItemNavegacao,
            vazio: "Nenhum registro de navegação recente.",
        },
        {
            id: "arquivos",
            titulo: "Arquivos abertos",
            itens: listaSegura(desktop.arquivos),
            criarItem: criarItemArquivo,
            vazio: "Nenhum arquivo aberto identificado.",
        },
    ];

    const salva = abaAtiva.get(chave);
    const ativa = abas.some(aba => aba.id === salva) ? salva : abas[0].id;

    const container = criarElemento("div", "abas");
    const barra = criarElemento("div", "abas-lista");
    barra.setAttribute("role", "tablist");

    const botoes = [];
    const paineis= [];

    abas.forEach(aba =>{
        const selecionada = aba.id === ativa;

        const botao = criarElemento("button", "aba" + (selecionada ? " ativa" : ""))
        botao.type = "button";
        botao.setAttribute("role", "tab");
        botao.setAttribute("aria-selected", String(selecionada));
        botao.appendChild(document.createTextNode(aba.titulo));
        botao.appendChild(criarElemento("span", "aba-contagem", String(aba.itens.length)));

        const painel = criarElemento("div", "aba-painel");
        painel.setAttribute("role", "tabpanel");
        painel.hidden = !selecionada;

        if (aba.itens.length === 0) {
            painel.appendChild(criarElemento("p", "sem-registros", aba.vazio));
        } else {
            const itens = criarElemento("div", "lista-itens");
            itens.dataset.scrollKey = `${chave}:${aba.id}`;
            aba.itens.forEach(item => itens.appendChild(aba.criarItem(item)));
            painel.appendChild(itens);
        }

        botao.addEventListener("click", () => {
            abaAtiva.set(chave, aba.id);

            botoes.forEach((outro, indice) => {
                const marcada = abas[indice].id === aba.id;
                outro.classList.toggle("ativa", marcada);
                outro.setAttribute("aria-selected", String(marcada));
                paineis[indice].hidden = !marcada;
        });
    });

    botoes.push(botao);
    paineis.push(painel);
    barra.appendChild(botao);
});

    container.appendChild(barra);
    paineis.forEach(painel => container.appendChild(painel));

    return container;
}

function criarRedes(desktop) {
    const vistos = new Set();
    const rotulos = [];

    listaSegura(desktop.interfaces_rede).forEach(interfaceRede => {
        listaSegura(interfaceRede.enderecos).forEach(endereco => {
            const chave = `${interfaceRede.nome}|${endereco.endereco}`;

            if (!endereco.endereco || vistos.has(chave)) {
                return;
            }

            vistos.add(chave);
            rotulos.push(`${interfaceRede.nome}: ${endereco.endereco}`);
        });
    });

    if (rotulos.length === 0) {
        return null;
    }

    const chips = criarElemento("div", "rede-chips");
    rotulos.forEach(rotulo => chips.appendChild(criarElemento("span", "chip", rotulo)));
    return chips;
}

function criarDetalhes(desktop, chave) {
    const detalhes = criarElemento("div", "detalhes-computador");
    detalhes.hidden = !detalhesAbertos.has(chave);

    const redes = criarRedes(desktop);
    if (redes) {
        detalhes.appendChild(redes);
    }

    detalhes.appendChild(criarAbas(desktop, chave));
    return detalhes;
}

function criarComputador(desktop) {
    const chave = chaveDesktop(desktop);
    const online = estaOnline(desktop);

    const computador = criarElemento(
        "article",
        "computador " + (online ? "is-online" : "is-offline")
    );

    const cabecalho = criarElemento("div", "computador-cabecalho");
    cabecalho.appendChild(criarElemento("h3", "", desktop.nome || "Nome desconhecido"));
    cabecalho.appendChild(
        criarElemento(
            "span",
            "status " + (online ? "online" : "offline"),
            desktop.status || "Desconhecido"
        )
    );
    computador.appendChild(cabecalho);

    const informacoes = criarElemento("div", "informacoes-computador");
    informacoes.appendChild(linhaInfo("IP", desktop.ip || "Não informado"));
    informacoes.appendChild(linhaInfo("Sistema", desktop.sistema_operacional || "Não informado"));
    informacoes.appendChild(linhaInfo("Tempo ligado", formatarTempoLigado(desktop.tempo_ligado)));
    informacoes.appendChild(
        linhaInfo(
            "Última comunicação",
            tempoRelativo(desktop.ultima_atividade),
            formatarData(desktop.ultima_atividade)
        )
    );
    computador.appendChild(informacoes);

    const indicadores = criarElemento("div", "indicadores-hardware");
    indicadores.appendChild(criarIndicador("CPU", desktop.cpu?.uso, detalheCpu(desktop.cpu)));
    indicadores.appendChild(criarIndicador("RAM", desktop.ram?.uso_percentual, detalheRam(desktop.ram)));
    indicadores.appendChild(
        criarIndicador("Armazenamento", desktop.armazenamento?.uso_percentual, detalheDisco(desktop.armazenamento))
    );
    computador.appendChild(indicadores);

    const detalhes = criarDetalhes(desktop, chave);

    const botao = criarElemento(
        "button",
        "botao-detalhes",
        detalhesAbertos.has(chave) ? "Ocultar detalhes" : "Ver detalhes"
    );
    botao.type = "button";
    botao.setAttribute("aria-expanded", String(detalhesAbertos.has(chave)));

    botao.addEventListener("click", () => {
        const abrir = detalhes.hidden;

        detalhes.hidden = !abrir;
        botao.textContent = abrir ? "Ocultar detalhes" : "Ver detalhes";
        botao.setAttribute("aria-expanded", String(abrir));

        if (abrir) {
            detalhesAbertos.add(chave);
        } else {
            detalhesAbertos.delete(chave);
        }
    });
    
    computador.appendChild(botao);
    computador.appendChild(detalhes);

    return computador;
}


function media(valores) {
    const validos = valores.map(numeroOuNulo).filter(valor => valor !== null);

    if (validos.length === 0) {
        return null;
    }

    return validos.reduce((soma, valor) => soma + valor, 0) / validos.length;
}

function atualizarResumo(desktops) {
    const total = desktops.length;
    const online = desktops.filter(estaOnline).length;

    const mediaCpu = media(desktops.map(d => d.cpu?.uso));
    const mediaRam = media(desktops.map(d => d.ram?.uso_percentual));

    totalComputadores.textContent = total;
    computadoresOnline.textContent = online;
    computadoresOffline.textContent = total - online;

    cpuMedia.textContent = mediaCpu === null ? "-": formatarPercentual(mediaCpu);
    cpuMedia.dataset.nivel = nivelUso(mediaCpu);

    ramMedia.textContent = mediaRam === null? "-": formatarPercentual(mediaRam);
    ramMedia.dataset.nivel = nivelUso(mediaRam);

    barraOnline.style.width = total ? `${(online / total) * 100}%` : "0%"
}

function valorOrdenacao(valor){
    const numero = numeroOuNulo(valor);
    return numero === null ? -1 : numero;
}

function compararNome(a, b) {
    return (a.nome || "").localeCompare(b.nome || "", "pt-BR", {numeric: true});
}

const ordenadores = {
    nome: compararNome,
    status: (a, b) => (Number(estaOnline(a)) - Number(estaOnline(b))) || compararNome(a, b),
    cpu: (a, b) => valorOrdenacao(b.cpu?.uso) - valorOrdenacao(a.cpu?.uso),
    ram: (a, b) => valorOrdenacao(b.ram?.uso_percentual) - valorOrdenacao(a.ram?.uso_percentual),
    disco: (a, b) =>
        valorOrdenacao(b.armazenamento?.uso_percentual) - valorOrdenacao(a.armazenamento?.uso_percentual),
};

function filtrarDesktops(desktops) {
    const termo = estado.busca.trim().toLowerCase();

    return desktops.filter(desktop =>{
        if (estado.filtro === "online" && !estaOnline(desktop)) return false;
        if (estado.filtro === "offline" && estaOnline(desktop)) return false;

        if(!termo) return true;

        const texto = [desktop.nome, desktop.ip, desktop.sistema_operacional]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        return texto.includes(termo);
    });
}

function salvarRolagem() {
    lista.querySelectorAll("[data-scroll-key]").forEach(elemento => {
        if (elemento.offsetParent !==null) {
            posicoesRolagem.set(elemento.dataset.scrollKey, elemento.scrollTop);
        }
    });
}

function restaurarRolagem() {
    lista.querySelectorAll("[data-scroll-key]").forEach(elemento => {
        const posicao = posicoesRolagem.get(elemento.dataset.scrollKey);

        if (posicao) {
            elemento.scrollTop = posicao;
        }
    });
}

function criarMensagemVazia(titulo,text) {
    const mensagem = criarElemento("div", "mensagem-vazia");
    mensagem.appendChild(criarElemento("strong", "", titulo));
    mensagem.appendChild(document.createTextNode(texto));
    return mensagem;
}

function renderizar() {
    const total = desktopsAtuais.length;
    const exibidos = filtrarDesktops(desktopsAtuais).sort(ordenadores[estado.ordem] || compararNome);

    salvarRolagem();
    lista.replaceChildren();

    if (total === 0) {
        lista.appendChild(
            criarMensagemVazia(
                "Nenhum computador registrado",
                "Assim que o agente for iniciado em um terminal, aparece aqui."
            )
        ); 
        contagemResultados.textContent = "Monitoramento dos terminais registrados";
        return;
    }
    
    contagemResultados.textContent =
        exibidos.length === total
            ? `${total} ${total === 1 ? "terminal registrado" : "terminais registrados"}`
            : `Mostrando ${exibidos.length} de ${total} terminais`;

    if (exibidos.length === 0) {
        lista.appendChild(
            criarMensagemVazia(
                "Nenhum resultado",
                "Ajuste a busca ou o filtro de status para ver outros terminais."
            )
        );
        return;
    }

    exibidos.forEach(desktop => lista.appendChild(criarComputador(desktop)));
    restaurarRolagem();
}

function marcarConexao(conectado) {
    statusServidor.textContent= conectado ? "Servidor conectado" : "Sem conexão com o servidor";
    indicadorConexao.classList.toggle("conectado", conectado);
    indicadorConexao.classList.toggle("erro", !conectado);
    avisoConexao.hidden = conectado;

    ultimaAtualizacao.textContent = conectado
        ? `Atualizado às ${new Date().toLocaleTimeString("pt-BR")}`
        : "Falha ao atualizar os dados";
}

async function carregarComputadores() {
    try {
        const resposta = await fetch("/desktops/", { cache: "no-store"});

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados.Desktops)) {
            throw new Error("Formato de resposta inválido.");
        }

        desktopsAtuais = dados.Desktops;

        atualizarResumo(desktopsAtuais);
        renderizar();
        marcarConexao(true);

    } catch (erro) {
        console.error("Erro ao carregar computadores:", erro);

        marcarConexao(false);
    }
}

campoBusca.addEventListener("input", () => {
    estado.busca = campoBusca.value;
    renderizar ();
});

seletorOrdenacao.addEventListener("change", () => {
    estado.ordem = seletorOrdenacao.value;
    renderizar();
});

botoesFiltro.forEach(botao => {
    botao.addEventListener("click", () => {
        estado.filtro = botao.dataset.filtro;

        botoesFiltro.forEach(outro => {
            const ativo = outro === botao;
            outro.classList.toggle("ativo", ativo);
            outro.setAttribute("aria-pressed", String(ativo));
        });

        renderizar();
    });
});

carregarComputadores();
setInterval(carregarComputadores, INTERVALO_ATUALIZACAO_MS);