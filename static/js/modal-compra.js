// =======================
// ✅ VARIÁVEIS
// =======================
let produtoSelecionado = null;
let qtdModal = 1;

// =======================
// ✅ ABRIR MODAL
// =======================
function abrirModalCompra(btn) {

    qtdModal = 1;

    document.getElementById("modalQtd").innerText = "1";

    const data = JSON.parse(
        btn.getAttribute("data-precos")
    );

    produtoSelecionado = {

        id: btn.getAttribute("data-id"),

        nome: btn.getAttribute("data-nome"),

        img: btn.getAttribute("data-img"),

        precos: data
    };

    document.getElementById(
        "modalNome"
    ).innerText = produtoSelecionado.nome;

    document.getElementById(
        "modalImagem"
    ).src = produtoSelecionado.img;

    const select =
        document.getElementById("modalSelect");

    select.innerHTML = "";

    produtoSelecionado.precos.forEach(p => {

        let option =
            document.createElement("option");

        option.value = p.id;

        option.setAttribute(
            "data-disponivel",
            p.disponivel
        );

        // ✅ TEXO NORMAL
        if(parseInt(p.disponivel) > 0){

            option.innerText =
                `${p.tamanho} - R$ ${p.valor}`;

        }

        // ✅ ESGOTADO
        else{

            option.innerText =
                `${p.tamanho} - ESGOTADO`;

        }

        select.appendChild(option);
    });

    // ✅ BOTÃO COMPRAR
    const btnComprar =
        document.getElementById("btnModalComprar");

    // ✅ CONTROLE ESTOQUE
    function atualizarEstoqueModal(){

        const option =
            select.options[
                select.selectedIndex
            ];

        const disponivel =
            parseInt(
                option.getAttribute(
                    "data-disponivel"
                )
            );

        // ✅ SEM ESTOQUE
        if(disponivel <= 0){

            btnComprar.disabled = true;

            btnComprar.innerText =
                "INDISPONÍVEL";

            btnComprar.style.opacity =
                "0.6";

            btnComprar.style.cursor =
                "not-allowed";

        }

        // ✅ COM ESTOQUE
        else{

            btnComprar.disabled = false;

            btnComprar.innerText =
                "COMPRAR";

            btnComprar.style.opacity =
                "1";

            btnComprar.style.cursor =
                "pointer";

            // ✅ AJUSTA QUANTIDADE
            if(qtdModal > disponivel){

                qtdModal = disponivel;

                document.getElementById(
                    "modalQtd"
                ).innerText = qtdModal;
            }
        }
    }

    // ✅ TROCA VOLUME
    select.onchange = atualizarEstoqueModal;

    // ✅ INICIALIZA
    atualizarEstoqueModal();

    document.getElementById(
        "modalCompra"
    ).classList.add("active");
}

// =======================
// ✅ FECHAR MODAL
// =======================
function fecharModalCompra() {
    document.getElementById("modalCompra").classList.remove("active");
}

// =======================
// ✅ QTD MODAL
// =======================
function alterarQtdModal(delta) {

    const select =
        document.getElementById("modalSelect");

    const option =
        select.options[
            select.selectedIndex
        ];

    const disponivel =
        parseInt(
            option.getAttribute(
                "data-disponivel"
            )
        );

    qtdModal += delta;

    // ✅ MÍNIMO
    if (qtdModal < 1){

        qtdModal = 1;
    }

    // ✅ LIMITE GLOBAL
    if (qtdModal > 10){

        qtdModal = 10;
    }

    // ✅ LIMITE ESTOQUE
    if (qtdModal > disponivel){

        qtdModal = disponivel;

        alert(
            `Máximo disponível: ${disponivel} unidade(s).`
        );
    }

    document.getElementById(
        "modalQtd"
    ).innerText = qtdModal;
}


function confirmarCompra() {

    if (!produtoSelecionado) {
        return;
    }

    const select = document.getElementById("modalSelect");

    if (!select) {
        return;
    }

    const preco_id = select.value;

    if (!preco_id) {
        alert("Selecione um tamanho.");
        return;
    }

    fetch("/carrinho/adicionar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCSRF()
        },

        body: `perfume_id=${produtoSelecionado.id}&preco_id=${preco_id}&quantidade=${qtdModal}`

    })
    .then(res => res.json())
    .then(data => {

        if (data.success) {

            // ✅ fecha o modal
            fecharModalCompra();

            // ✅ atualiza badge imediatamente
            const badges = document.querySelectorAll(".cart-badge");

            badges.forEach(badge => {

                if (data.quantidade_total > 0) {

                    badge.innerText = data.quantidade_total;
                    badge.style.display = "flex";

                } else {

                    badge.innerText = "";
                    badge.style.display = "none";

                }

            });

            console.log("✅ Badge atualizada para:", data.quantidade_total);

            // ✅ toast
            mostrarToastProduto(data);

            // ✅ se o drawer estiver aberto, atualiza o conteúdo
            const drawer = document.getElementById("drawer-carrinho");

            if (drawer && drawer.classList.contains("ativo")) {
                atualizarCarrinhoDrawer();
            }

        } else {

            alert("⚠ Estoque insuficiente");

            console.log("❌ resposta inesperada:", data);

        }

    })
    .catch(error => {

        console.error("❌ ERRO NO FETCH:", error);

    });

}

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".preco").forEach(function (bloco) {

        let precoTexto = bloco.getAttribute("data-preco");

        if (!precoTexto) return;

        let preco = parseFloat(precoTexto);

        if (isNaN(preco)) return;

        let parcela = (preco / 3).toFixed(2);

        let card = bloco.closest(".card");

        if (!card) return;

        let parcelaEl = card.querySelector(".valor-parcela");

        if (parcelaEl) {
            parcelaEl.innerText = "R$ " + parcela.replace(".", ",");
        }

    });

});