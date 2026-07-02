const Frete = {

    // =========================
    // CONFIG
    // =========================

    limiteSulSudeste: 199,
    limiteNorteNordeste: 300,

    taxaPadrao: 6,
    taxaContingencia: 10,

    // Acre, Amapá, Amazonas e Roraima
    cepsContingencia: [
        "68",
        "69"
    ],

    norteNordeste: [
        "50","51","52","53","54","55","56","57","58","59",
        "60","61","62","63","64","65","66","67","68","69"
    ],

    // =========================
    // CONSULTA API
    // =========================

    async consultar(cep) {

        try {

            const cepLimpo = String(cep || "")
                .replace(/\D/g, "");

            if (cepLimpo.length < 8) {

                return {
                    success: false,
                    fretes: [],
                    erro: "CEP inválido"
                };
            }

            const response = await fetch(
                `/entrega/frete/?cep=${cepLimpo}`,
                {
                    credentials: "same-origin"
                }
            );

            const data = await response.json();

            return data;

        } catch (erro) {

            console.error(
                "Erro consulta frete:",
                erro
            );

            return {
                success: false,
                fretes: []
            };
        }
    },

    // =========================
    // FRETES VÁLIDOS
    // =========================

    obterValidos(fretes) {

        return (fretes || [])
            .filter(f => !f.error);
    },

    // =========================
    // ORDENAÇÃO
    // =========================

    ordenar(fretes) {

        return [...fretes].sort(
            (a, b) =>
                parseFloat(a.price || 0)
                -
                parseFloat(b.price || 0)
        );
    },

    // =========================
    // FRETE GRÁTIS
    // =========================

    calcularGratis(subtotal, cep) {

        const prefixo =
            String(cep || "")
            .substring(0, 2);

        let limite =
            this.limiteSulSudeste;

        if (
            this.norteNordeste.includes(
                prefixo
            )
        ) {
            limite =
                this.limiteNorteNordeste;
        }

        return subtotal >= limite;
    },

    // =========================
    // TAXA POR REGIÃO
    // =========================

    obterTaxaFrete(cep) {

        const prefixo =
            String(cep || "")
            .substring(0, 2);

        if (
            this.cepsContingencia.includes(
                prefixo
            )
        ) {

            return this.taxaContingencia;
        }

        return this.taxaPadrao;
    },

    // =========================
    // APLICA FRETE
    // =========================

    aplicar({
        subtotal,
        frete,
        cep,
        totalId,
        freteId,
        parcelamentoId
    }) {

        let valorFrete =
            parseFloat(frete);

        let textoFrete =
            `R$ ${valorFrete.toFixed(2)}`;

        if (
            this.calcularGratis(
                subtotal,
                cep
            )
        ) {

            valorFrete = 0;

            textoFrete =
                "GRÁTIS 🚚";
        }

        const totalFinal =
            subtotal +
            valorFrete;

        if (freteId) {

            const el =
                document.getElementById(
                    freteId
                );

            if (el) {
                el.innerText =
                    textoFrete;
            }
        }

        if (totalId) {

            const el =
                document.getElementById(
                    totalId
                );

            if (el) {

                el.innerText =
                    `R$ ${totalFinal.toFixed(2)}`;
            }
        }

        if (parcelamentoId) {

            const el =
                document.getElementById(
                    parcelamentoId
                );

            if (el) {

                const parcela =
                    totalFinal / 3;

                el.innerText =
                    `Ou até 3x de R$ ${parcela.toFixed(2)} sem juros`;
            }
        }

        localStorage.setItem(
            "frete_valor",
            frete
        );

        localStorage.setItem(
            "frete_total",
            totalFinal
        );

        localStorage.setItem(
            "frete_cep",
            cep
        );

        return totalFinal;
    },

// =========================
// RENDERIZA LISTA
// =========================

renderizar({
    fretes,
    listaId,
    cep,
    subtotal,
    totalId,
    freteId,
    parcelamentoId,
    callback,
    modo = "carrinho"
}) {

    const lista =
        document.getElementById(
            listaId
        );

    if (!lista) return;

lista.innerHTML = "";

fretes
    .forEach((f, index) => {

        const preco =
            parseFloat(
                f.price || 0
            ) + this.obterTaxaFrete(cep);

        const prazo =
            f.id === "contingencia"
                ? parseInt(f.delivery_time || 0)
                : parseInt(f.delivery_time || 0) + 2;

        const label =
            document.createElement(
                "label"
            );

        label.className =
            "frete-option";

        if (
            index === 0
        ) {
            label.classList.add(
                "melhor"
            );
        }


            // =========================
            // ✅ MODO PRODUTO
            // =========================

            if (
                modo === "produto"
            ) {

                label.innerHTML = `

                    <div class="frete-left">

                        <img
                            src="${f.company?.picture || ''}"
                        >

                        <span>
                            ${f.name || "Frete"}
                        </span>

                    </div>

                    <div class="frete-info">

                        <strong>
                            R$ ${preco.toFixed(2)}
                        </strong>

                        <br>

                        ${prazo} dias úteis

                    </div>

                `;

                lista.appendChild(
                    label
                );

                return;
            }

            // =========================
            // ✅ MODO CARRINHO/CHECKOUT
            // =========================

            label.innerHTML = `

                <div class="frete-left">

                    <input
                        type="radio"
                        name="frete"
                        ${index === 0 ? "checked" : ""}
                    >

                    <img
                        src="${f.company?.picture || ''}"
                    >

                    <span>
                        ${f.name || "Frete"}
                    </span>

                </div>

                <div class="frete-info">

                    <strong>
                        R$ ${preco.toFixed(2)}
                    </strong>

                    <br>

                    ${prazo} dias úteis

                </div>

            `;

            const radio =
                label.querySelector(
                    "input"
                );

            radio.addEventListener(
                "change",
                () => {

                    this.aplicar({

                        subtotal,
                        frete: preco,
                        cep,

                        totalId,
                        freteId,
                        parcelamentoId

                    });

                    const nomeCompletoFrete =
                        `${f.company?.name || ''} ${f.name || ''}`
                            .trim();

                    localStorage.setItem(
                        "frete_nome",
                        nomeCompletoFrete
                    );

                    localStorage.setItem(
                        "frete_prazo",
                        prazo
                    );

                    if (
                        callback
                    ) {

                        callback({

                            frete: preco,
                            prazo,
                            nome: nomeCompletoFrete

                        });
                    }
                }
            );

            lista.appendChild(
                label
            );

            if (index === 0) {

                radio.dispatchEvent(
                    new Event("change")
                );

            }

            });

            },

    // =========================
    // CONSULTAR + RENDERIZAR
    // =========================

    async carregar(config) {

        const dados =
            await this.consultar(
                config.cep
            );

        if (
            !dados.success ||
            !dados.fretes
        ) {

            const lista =
                document.getElementById(
                    config.listaId
                );

            if (lista) {

                lista.innerHTML =
                    "Erro ao carregar frete";
            }

            return;
        }

        let fretes =
            this.obterValidos(
                dados.fretes
            );

        fretes =
            this.ordenar(
                fretes
            );

        if (
            !fretes.length
        ) {

            document.getElementById(
                config.listaId
            ).innerHTML =
                "Nenhuma opção disponível";

            return;
        }

        this.renderizar({
            ...config,
            fretes
        });
    },

    // =========================
    // RESTAURAR CEP
    // =========================

    restaurar(inputId) {

        const cep =
            localStorage.getItem(
                "cep_carrinho"
            );

        const campo =
            document.getElementById(
                inputId
            );

        if (
            cep &&
            campo
        ) {

            campo.value =
                cep;
        }

        return cep;
    }

};

window.Frete = Frete;