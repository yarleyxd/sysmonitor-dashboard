const lista = document.getElementById("lista-computadores");

const totalComputadores = document.getElementById("total-computadores");
const computadoresOnline = document.getElementById("computadores-online");
const computadoresOffline = document.getElementById("computadores-offline");
const cpuMedia = document.getElementById("cpu-media");
const ramMedia = document.getElementById("ram-media");
const statusServidor = document.getElementById("status-servidor");
const ultimaAtualizacao = document.getElementById("ultima-atualizacao");
const indicadorConexao = document.getElementById("indicador-conexao");

const detalhesAbertos = new Set();


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


function formatarPercentual(valor) {

    const numero = Number(valor);

    if (!Number.isFinite(numero)) {
        return "N/D";
    }

    return `${numero.toFixed(1)}%`;
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


function criarIndicador(titulo, valor) {

    const indicador = criarElemento(
        "div",
        "indicador-hardware"
    );

    const nome = criarElemento(
        "span",
        "nome-indicador",
        titulo
    );

    const porcentagem = criarElemento(
        "span",
        "valor-indicador",
        valor
    );

    const barra = criarElemento(
        "div",
        "barra"
    );

    const preenchimento = criarElemento(
        "div",
        "preenchimento"
    );

    const numero = Number.parseFloat(valor);

    if (Number.isFinite(numero)) {

        preenchimento.style.width =
            `${Math.min(100, Math.max(0, numero))}%`;
    }

    barra.appendChild(preenchimento);

    indicador.appendChild(nome);
    indicador.appendChild(porcentagem);
    indicador.appendChild(barra);

    return indicador;
}


function criarListaAplicativos(desktop) {

    const secao = criarElemento(
        "div",
        "secao-aplicativos"
    );

    const titulo = criarElemento(
        "h3",
        "",
        "Aplicativos em execução"
    );

    secao.appendChild(titulo);

    const aplicativos = Array.isArray(desktop.aplicativos)
        ? desktop.aplicativos
        : [];

    if (aplicativos.length === 0) {

        secao.appendChild(
            criarElemento(
                "p",
                "sem-aplicativos",
                "Nenhum aplicativo identificado."
            )
        );

        return secao;
    }

    const listaAplicativos = criarElemento(
        "div",
        "lista-aplicativos"
    );

    aplicativos.forEach(aplicativo => {

        const item = criarElemento(
            "div",
            "aplicativo"
        );

        const nome = criarElemento(
            "span",
            "aplicativo-nome",
            aplicativo.nome || "Desconhecido"
        );

        const pid = criarElemento(
            "span",
            "aplicativo-pid",
            `PID: ${aplicativo.pid || "N/D"}`
        );

        item.appendChild(nome);
        item.appendChild(pid);

        listaAplicativos.appendChild(item);
    });

    secao.appendChild(listaAplicativos);

    return secao;
}


function criarDetalhes(desktop) {

    const detalhes = criarElemento(
        "div",
        "detalhes-computador"
    );

    detalhes.style.display = "none";

    const titulo = criarElemento(
        "h3",
        "",
        "Detalhes do computador"
    );

    detalhes.appendChild(titulo);

    const informacoes = criarElemento(
        "div",
        "detalhes-informacoes"
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `IP: ${desktop.ip || "Não informado"}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `Sistema: ${desktop.sistema_operacional || "Não informado"}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `Tempo ligado: ${formatarTempoLigado(desktop.tempo_ligado)}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `Última comunicação: ${formatarData(desktop.ultima_atividade)}`
        )
    );

    detalhes.appendChild(informacoes);

    detalhes.appendChild(
        criarListaAplicativos(desktop)
    );

    return detalhes;
}


function criarComputador(desktop) {

    const computador = criarElemento(
        "article",
        "computador"
    );

    const cabecalho = criarElemento(
        "div",
        "computador-cabecalho"
    );

    const nome = criarElemento(
        "h3",
        "",
        desktop.nome || "Nome desconhecido"
    );

    const status = criarElemento(
        "span",
        "status " + (
            desktop.status === "Online"
                ? "online"
                : "offline"
        ),
        desktop.status || "Desconhecido"
    );

    cabecalho.appendChild(nome);
    cabecalho.appendChild(status);

    computador.appendChild(cabecalho);


    const informacoes = criarElemento(
        "div",
        "informacoes-computador"
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `IP: ${desktop.ip || "Não informado"}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `Sistema: ${desktop.sistema_operacional || "Não informado"}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "",
            `Tempo ligado: ${formatarTempoLigado(desktop.tempo_ligado)}`
        )
    );

    informacoes.appendChild(
        criarElemento(
            "p",
            "ultima-comunicacao",
            `Última comunicação: ${formatarData(desktop.ultima_atividade)}`
        )
    );

    computador.appendChild(informacoes);


    const indicadores = criarElemento(
        "div",
        "indicadores-hardware"
    );

    indicadores.appendChild(
        criarIndicador(
            "CPU",
            formatarPercentual(desktop.cpu?.uso)
        )
    );

    indicadores.appendChild(
        criarIndicador(
            "RAM",
            formatarPercentual(desktop.ram?.uso_percentual)
        )
    );

    indicadores.appendChild(
        criarIndicador(
            "Armazenamento",
            formatarPercentual(
                desktop.armazenamento?.uso_percentual
            )
        )
    );

    computador.appendChild(indicadores);

    const botaoDetalhes = criarElemento(
        "button",
        "botao-detalhes",
        detalhesAbertos.has(desktop.nome)
        ? "Ocultar detalhes"
        : "Ver detalhes"
    );

    computador.appendChild(botaoDetalhes);


    const detalhes = criarDetalhes(desktop);
    if (detalhesAbertos.has(desktop.nome)) {
        detalhes.style.display = "block";
    }

    computador.appendChild(detalhes);


    botaoDetalhes.addEventListener("click", function () {
        const aberto = detalhes.style.display === "none";
        
        detalhes.style.display = aberto ? "block" : "none";
        botaoDetalhes.textContent = aberto
        ? "Ocultar detalhes"
        : "Ver detalhes";

        if (desktop.nome) {
            if (aberto) {
                detalhesAbertos.add(desktop.nome);
            } else {
                detalhesAbertos.delete(desktop.nome);
            }
        }
    });

    return computador;
}


function atualizarResumo(desktops) {

    const total = desktops.length;

    const online = desktops.filter(
        desktop => desktop.status === "Online"
    ).length;

    const offline = total - online;


    const cpus = desktops
        .map(desktop => Number(desktop.cpu?.uso))
        .filter(valor => Number.isFinite(valor));


    const rams = desktops
        .map(desktop => Number(desktop.ram?.uso_percentual))
        .filter(valor => Number.isFinite(valor));


    const mediaCPU = cpus.length
        ? cpus.reduce(
            (soma, valor) => soma + valor,
            0
        ) / cpus.length
        : 0;


    const mediaRAM = rams.length
        ? rams.reduce(
            (soma, valor) => soma + valor,
            0
        ) / rams.length
        : 0;


    totalComputadores.textContent = total;
    computadoresOnline.textContent = online;
    computadoresOffline.textContent = offline;
    cpuMedia.textContent = formatarPercentual(mediaCPU);
    ramMedia.textContent = formatarPercentual(mediaRAM);
}


async function carregarComputadores() {

    try {

        const resposta = await fetch(
            "/desktops/",
            {
                cache: "no-store"
            }
        );


        if (!resposta.ok) {

            throw new Error(
                `Erro HTTP ${resposta.status}`
            );
        }


        const dados = await resposta.json();


        if (!Array.isArray(dados.Desktops)) {

            throw new Error(
                "Formato de resposta inválido."
            );
        }


        const desktops = dados.Desktops;


        lista.replaceChildren();


        atualizarResumo(desktops);


        if (desktops.length === 0) {

            lista.appendChild(
                criarElemento(
                    "p",
                    "mensagem-vazia",
                    "Nenhum computador registrado."
                )
            );

        } else {

            desktops.forEach(desktop => {

                lista.appendChild(
                    criarComputador(desktop)
                );

            });

        }


        if (statusServidor) {
            statusServidor.textContent = "Servidor Conectado";
        }

        if (indicadorConexao) {
            indicadorConexao.classList.add("conectado");
            indicadorConexao.classList.remove("erro");
        }

        if (ultimaAtualizacao) {
            ultimaAtualizacao.textContent = `Última atualização: ${new Date().toLocaleString("pt-BR")}`;
        }

    } catch (erro) {

        console.error(
            "Erro ao carregar computadores:",
            erro
        );

        if (statusServidor) {
            statusServidor.textContent = "Falha na conexão com o servidor";
        }

        if (indicadorConexao) {
            indicadorConexao.classList.add("erro");
            indicadorConexao.classList.remove("conectado");
        }

        if (ultimaAtualizacao) {
            ultimaAtualizacao.textContent = "Falha ao atualizar os dados";
        }
    }
}


carregarComputadores();

setInterval(
    carregarComputadores,
    5000
);