async function carregarComputadores() {

    try {

        const resposta = await fetch("/desktops/");

        const dados = await resposta.json();

        const lista = document.getElementById("lista-computadores");

        lista.innerHTML = "";


        if (dados.Desktops.length === 0) {

            lista.innerHTML = `
                <p>Nenhum computador conectado.</p>
            `;

            return;
        }


        dados.Desktops.forEach(desktop => {

            const computador = document.createElement("div");

            computador.classList.add("computador");


            computador.innerHTML = `

                <h3>${desktop.nome}</h3>

                <p>
                    <strong>Status:</strong>
                    ${desktop.status}
                </p>

                <p>
                    <strong>IP:</strong>
                    ${desktop.ip}
                </p>

                <p>
                    <strong>Sistema:</strong>
                    ${desktop.sistema_operacional}
                </p>

                <p>
                    <strong>CPU:</strong>
                    ${desktop.cpu.uso}%
                </p>

                <p>
                    <strong>RAM:</strong>
                    ${desktop.ram.uso_percentual}%
                </p>

                <p>
                    <strong>Armazenamento:</strong>
                    ${desktop.armazenamento.uso_percentual}%
                </p>

            `;


            lista.appendChild(computador);

        });

    }

    catch (erro) {

        console.error("Erro ao carregar computadores:", erro);

    }

}


carregarComputadores();


setInterval(carregarComputadores, 5000);