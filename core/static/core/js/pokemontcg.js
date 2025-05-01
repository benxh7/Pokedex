(() => {
    const container = document.getElementById("cards-container");
    const input = document.getElementById("tcg-search");
    const btnClear = document.getElementById("btn-clear");

    const translate = {
        hp: "PS",
        types: "Tipos",
        rarity: "Rareza",
        name: "Nombre"
    };

    // Renderiza una sola carta
    function renderCard(card) {
        const col = document.createElement("div");
        col.className = "col-12 col-sm-6 col-md-4 col-lg-3";

        const typesBadges = (card.types || []).map(t =>
            `<span class="badge bg-warning text-dark me-1">${t}</span>`
        ).join("");

        const html = `
      <div class="card h-100 shadow-sm">
        <img src="${card.images.small}" class="card-img-top" alt="${card.name}">
        <div class="card-body">
          <h5 class="card-title">${translate.name}: ${card.name}</h5>
          <p class="card-text"><strong>${translate.hp}:</strong> ${card.hp || "—"}</p>
          <p class="card-text"><strong>${translate.types}:</strong> ${typesBadges}</p>
          <p class="card-text"><strong>${translate.rarity}:</strong> ${card.rarity || "—"}</p>
        </div>
      </div>
    `;
        col.innerHTML = html;
        container.appendChild(col);
    }

    // Limpia y muestra cartas según término
    function fetchAndRender(q = "") {
        container.innerHTML = ""; // limpia
        const url = new URL("http://127.0.0.1:8001/tcg/cards/");
        if (q) url.searchParams.set("q", q);
        fetch(url)
            .then(res => res.json())
            .then(json => {
                if (!json.cards.length) {
                    container.innerHTML = `<p class="text-muted">No se encontraron cartas.</p>`;
                } else {
                    json.cards.forEach(renderCard);
                }
            })
            .catch(err => {
                container.innerHTML = `<p class="text-danger">Error al recuperar cartas.</p>`;
                console.error(err);
            });
    }

    // Eventos
    input.addEventListener("keyup", e => {
        const term = e.target.value.trim();
        if (term.length >= 2 || term.length === 0) {
            fetchAndRender(term);
        }
    });

    btnClear.addEventListener("click", () => {
        input.value = "";
        fetchAndRender();
    });

    // Al cargar la página
    document.addEventListener("DOMContentLoaded", () => fetchAndRender());
})();
