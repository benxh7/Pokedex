/* Traducción a español */
const TYPE_ES = {
    fire: 'Fuego', water: 'Agua', grass: 'Planta', electric: 'Eléctrico',
    bug: 'Bicho', normal: 'Normal', poison: 'Veneno', flying: 'Volador',
    rock: 'Roca', ground: 'Tierra', psychic: 'Psíquico', fighting: 'Lucha',
    ghost: 'Fantasma', ice: 'Hielo', dragon: 'Dragón', dark: 'Siniestro',
    steel: 'Acero', fairy: 'Hada'
};

async function nombreES(url) {
    /*  Devuelve el nombre en español del recurso (ability, egg‑group…)
        o el inglés si no existe                           */
    const data = await fetchJSON(url);
    const es = data.names?.find(n => n.language.name === 'es');
    return es ? es.name : data.name;
}

/* ANIMACION DE CARGA PARA LA PAGINA */
document.addEventListener('DOMContentLoaded', () => {
    const loader = document.querySelector('.loader-wrapper');
    if (loader) loader.style.display = 'block';

    initDetailPage()
        .catch(err => console.error('Error en initDetailPage:', err))
        .finally(() => {
            document.body.classList.add('loaded');
        });
});

async function initDetailPage() {
    /* Extraemos ID desde /pokemon/<id>/ */
    const segments = window.location.pathname.split('/').filter(Boolean);
    const id = parseInt(segments.pop(), 10);
    if (isNaN(id)) throw new Error('ID de Pokémon inválido en URL');

    /* ───────── 2) Configuración de recursos ───────── */
    const pokeball = `/static/core/img/pokemon/icons/default/pokeball.svg`;
    const colors = {
        fire: '#e03a3a', grass: '#50C878', electric: '#fad343', water: '#1E90FF',
        ground: '#735139', rock: '#63594f', fairy: '#EE99AC', poison: '#b34fb3',
        bug: '#A8B820', dragon: '#fc883a', psychic: '#882eff', flying: '#87CEEB',
        fighting: '#bf5858', normal: '#D2B48C', ghost: '#7B62A3', dark: '#414063',
        steel: '#808080', ice: '#98D8D8'
    };
    const mainTypes = Object.keys(colors);
    const icon = t => `/static/core/img/pokemon/icons/${t}.svg`;

    /* ───────── 3) Descarga de datos (Pokémon, especie, tipos) ───────── */
    const [data, species] = await Promise.all([
        fetchJSON(`https://pokeapi.co/api/v2/pokemon/${id}/`),
        fetchJSON(`https://pokeapi.co/api/v2/pokemon-species/${id}/`)
    ]);

    /*  ⬇  NUEVO: habilidades y grupos‑huevo en español  */
    const abilityNames = await Promise.all(
        data.abilities.map(a => nombreES(a.ability.url))
    );
    const eggGroupNames = await Promise.all(
        species.egg_groups.map(g => nombreES(g.url))
    );

    const typeNames = data.types.map(t => t.type.name);
    const typeDetails = await Promise.all(
        typeNames.map(n => fetchJSON(`https://pokeapi.co/api/v2/type/${n}/`))
    );

    /* ───────── 4) Renderizado ───────── */
    displayHeader({data, species, id, pokeball, colors, mainTypes});
    displayTab1({
        data, species, icon, id,
        abilityNames, eggGroupNames           // ← pasa los arrays
    });
    await displayTab2({data, typeDetails});
    await displayTab3({species});
}

/* ────────────────────────── UTILIDADES ─────────────────────────── */

async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Fetch ${url} failed (${res.status})`);
    return res.json();
}

/* ─────────────────────── SECCIÓN: HEADER ─────────────────────── */

function displayHeader({data, species, id, pokeball, colors, mainTypes}) {
    const esName = species.names.find(n => n.language.name === 'es')?.name;
    const name = esName || data.name[0].toUpperCase() + data.name.slice(1);
    const jp = species.names.find(n => n.language.name === 'ja')?.name || name;
    const types = data.types.map(t => t.type.name);
    const bg = colors[types.find(t => mainTypes.includes(t))] || '#fff';
    document.body.style.backgroundColor = bg;

    document.getElementById('pokemon-details').innerHTML = `
    <div class="btn">
      <button onclick="backButton()"><i class="fas fa-chevron-left"></i></button>
      <button onclick="nextPokemon()"><i class="fas fa-chevron-right"></i></button>
    </div>
    <div class="names">
      <div class="japaneseName">${jp}</div>
      <div class="name">${name}</div>
    </div>
    <div class="top">
      <div class="image">
        <img class="imgFront"
             src="${data.sprites.other.dream_world.front_default || data.sprites.front_default}"
             alt="${name}">
        <img class="imgBack" src="${pokeball}" alt="pokeball">
      </div>
    </div>`;
}

/* ─────────────────────── SECCIÓN: TAB 1 ─────────────────────── */

function displayTab1({data, species, icon, id, abilityNames, eggGroupNames}) {
    const esText = species.flavor_text_entries.find(e => e.language.name === 'es');
    const text = esText?.flavor_text.replace(/\f/g, ' ') || 'Sin descripción.';
    const genus = species.genera.find(g => g.language.name === 'es')?.genus || '—';

    const height = (data.height / 10).toFixed(1) + ' m';
    const weight = (data.weight / 10).toFixed(1) + ' kg';
    const types = data.types.map(t => t.type.name);

    const friendship = species.base_happiness;
    const catchRate = species.capture_rate;
    const ratePct = ((catchRate / 255) * 100).toFixed(2);

    document.getElementById('tab_1').innerHTML = `
  <div class="overview">
    <p><span class="genus">${genus}</span><br>${text}</p>
    <div class="heightWeight">
      <div>Peso - Altura<br><b>${weight} - ${height}</b></div>
    </div>
    <div class="types">
      ${types.map(t => `
        <div class="poke__type__bg ${t}" title="${TYPE_ES[t]}">
          <img src="${icon(t)}" alt="${TYPE_ES[t]}">
        </div>`).join('')}
    </div>
  </div>

  <div class="about">
    <div>ID: <b class="id">#${String(id).padStart(3, '0')}</b></div>
    <div>Habilidades: <b>${abilityNames.join(', ')}</b></div>
    <div>Grupos‑huevo: <b>${eggGroupNames.join(', ')}</b></div>
    <div>Ratio de captura: <b>${catchRate} (${ratePct} %)</b></div>
    <div>Amistad base: <b>${friendship}</b></div>
  </div>`;
    activateTab('tab_1');
}

/* ─────────────────────── SECCIÓN: TAB 2 ─────────────────────── */

async function displayTab2({data, typeDetails}) {
    const statsHtml = data.stats.map(s => `
    <div class="stat">
      <div>
        <span>${s.stat.name.toUpperCase()}:</span><span>${s.base_stat}</span>
      </div>
      <meter value="${s.base_stat}" min="0" max="255" low="70" high="120" optimum="150"></meter>
    </div>`).join('');

    /* calcular relaciones de tipo Weak / Strong */
    const weak = new Set();
    const strong = new Set();

    typeDetails.forEach(t => {
        t.damage_relations.no_damage_to.forEach(x => weak.add(x.name));
        t.damage_relations.double_damage_to.forEach(x => strong.add(x.name));
    });

    const iconImg = name => `<img src="/static/core/img/pokemon/icons/${name}.svg"
       class="poke__type__bg ${name}"
       title="${TYPE_ES[name]}"
       alt="${TYPE_ES[name]}">`;

    document.getElementById('tab_2').innerHTML = `
    <div class="stats">${statsHtml}</div>

    <div class="statTypes">
      <div class="statTypeText">Débil Contra</div>
      <div class="statIconHolder">
        ${weak.size ? [...weak].map(iconImg).join('') : 'None'}
      </div>
    </div>
    <div class="statTypes">
      <div class="statTypeText">Fuerte Contra</div>
      <div class="statIconHolder">
        ${strong.size ? [...strong].map(iconImg).join('') : 'None'}
      </div>
    </div>`;
}

/* ─────────────────────── SECCIÓN: TAB 3 ─────────────────────── */

async function displayTab3({species}) {
    const evoData = await fetchJSON(species.evolution_chain.url);
    const evoChain = [];
    (function walk(node) {
        evoChain.push(node);
        if (node.evolves_to[0]) walk(node.evolves_to[0]);
    })(evoData.chain);

    const evoHtml = evoChain.map(n => {
        const pid = n.species.url.split('/').slice(-2, -1)[0];
        return `
      <div class="evolution__pokemon" onclick="window.location.href='/pokemon/${pid}/';">
        <h1>${n.species.name}</h1>
        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${pid}.png"
             alt="${n.species.name}">
      </div>`;
    }).join('<i class="fa-solid fa-caret-right fa-2x fa-beat"></i>');

    /* variedades */
    const varieties = species.varieties.filter(v => !v.is_default);
    const varHtml = await Promise.all(
        varieties.map(async v => {
            const vid = v.pokemon.url.split('/').slice(-2, -1)[0];
            return `
        <div class="varieties__pokemon">
          <h1>${v.pokemon.name}</h1>
          <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${vid}.png"
               alt="${v.pokemon.name}">
        </div>`;
        })
    );

    document.getElementById('tab_3').innerHTML = `
    <div class="evolution">${evoHtml}</div>
    <div class="varieties">${varHtml.join('')}</div>`;
}

/* ──────────────────── Navegación entre tabs ─────────────────── */

function activateTab(tabId) {
    document.querySelectorAll('[data-tab-info]').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

document.querySelectorAll('[data-tab-value]').forEach(tab =>
    tab.addEventListener('click', () => {
        activateTab(tab.dataset.tabValue.slice(1));
        document.getElementById(tab.dataset.tabValue.slice(1))
            .scrollIntoView({behavior: 'smooth'});
    })
);

/* ──────────────────── Navegación Prev / Next global ─────────────────── */

window.nextPokemon = e => {
    e?.preventDefault();
    const seg = window.location.pathname.split('/').filter(Boolean);
    window.location.href = `/pokemon/${parseInt(seg.pop(), 10) + 1}/`;
};

window.backButton = e => {
    e?.preventDefault();
    window.history.back();
};