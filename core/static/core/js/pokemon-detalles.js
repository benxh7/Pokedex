/* Traducción a español */
const TYPE_ES = {
    fire: 'Fuego',
    water: 'Agua',
    grass: 'Planta',
    electric: 'Eléctrico',
    bug: 'Bicho',
    normal: 'Normal',
    poison: 'Veneno',
    flying: 'Volador',
    rock: 'Roca',
    ground: 'Tierra',
    psychic: 'Psíquico',
    fighting: 'Lucha',
    ghost: 'Fantasma',
    ice: 'Hielo',
    dragon: 'Dragón',
    dark: 'Siniestro',
    steel: 'Acero',
    fairy: 'Hada'
};

const STAT_ES = {
    hp: 'Vida',
    attack: 'Ataque',
    defense: 'Defensa',
    'special-attack': 'Atq. Esp',
    'special-defense': 'Def. Esp',
    speed: 'Velocidad'
};

async function nombreES(url) {
    const data = await fetchJSON(url);
    const es = data.names?.find(n => n.language.name === 'es');
    return es ? es.name : data.name;
}

/* Animacion de carga para la pagina */
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

    /* Configuración de recursos */
    const pokeball = `/static/core/img/pokemon/icons/default/pokeball.svg`;
    const colors = {
        fire: '#e03a3a',
        grass: '#50C878',
        electric: '#fad343',
        water: '#1E90FF',
        ground: '#735139',
        rock: '#63594f',
        fairy: '#EE99AC',
        poison: '#b34fb3',
        bug: '#A8B820',
        dragon: '#fc883a',
        psychic: '#882eff',
        flying: '#87CEEB',
        fighting: '#bf5858',
        normal: '#D2B48C',
        ghost: '#7B62A3',
        dark: '#414063',
        steel: '#808080',
        ice: '#98D8D8'
    };
    const mainTypes = Object.keys(colors);
    const icon = t => `/static/core/img/pokemon/icons/${t}.svg`;

    /* Descarga de datos (Pokémon, especie, tipos) */
    const [data, species] = await Promise.all([fetchJSON(`https://pokeapi.co/api/v2/pokemon/${id}/`), fetchJSON(`https://pokeapi.co/api/v2/pokemon-species/${id}/`)]);

    const nombreAbilidades = await Promise.all(data.abilities.map(a => nombreES(a.ability.url)));
    const nombreGrupoHuevos = await Promise.all(species.egg_groups.map(g => nombreES(g.url)));

    const tipoNombres = data.types.map(t => t.type.name);
    const tipoDetalles = await Promise.all(tipoNombres.map(n => fetchJSON(`https://pokeapi.co/api/v2/type/${n}/`)));

    /* Renderizado */
    mostrarHeader({data, species, id, pokeball, colors, mainTypes});
    detallesPokemon({
        data, species, icon, id, abilityNames: nombreAbilidades, eggGroupNames: nombreGrupoHuevos
    });
    await estadisticasPokemon({data, typeDetails: tipoDetalles});
    await evolucionesPokemon({species});
}

/* Utilidades */
async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Fetch ${url} failed (${res.status})`);
    return res.json();
}

function mostrarHeader({data, species, id, pokeball, colors, mainTypes}) {
    const esName = species.names.find(n => n.language.name === 'es')?.name;
    const name = esName || data.name[0].toUpperCase() + data.name.slice(1);
    const jp = species.names.find(n => n.language.name === 'ja')?.name || name;
    const types = data.types.map(t => t.type.name);
    const bg = colors[types.find(t => mainTypes.includes(t))] || '#fff';
    document.body.style.backgroundColor = bg;

    document.getElementById('pokemon-details').innerHTML = `
    <div class="btn">
      <button class="previousBtn" onclick="backButton()">
      <i class="fa-solid fa-chevron-left"></i>
        </button>
      <button class="nextBtn" onclick="nextPokemon()">
      <i class="fa-solid fa-chevron-right"></i>
      </button>
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

/* Detalles Pokémon */
function detallesPokemon({data, species, icon, id, abilityNames, eggGroupNames: grupoNombreHuevos}) {
    const esText = species.flavor_text_entries.find(e => e.language.name === 'es');
    const text = esText?.flavor_text.replace(/\f/g, ' ') || 'Sin descripción.';
    /* Estadísticas */
    const genero = species.genera.find(g => g.language.name === 'es')?.genus || '—';
    const altura = (data.height / 10).toFixed(1) + ' m';
    const peso = (data.weight / 10).toFixed(1) + ' kg';
    const tipos = data.types.map(t => t.type.name);

    const amistad = species.base_happiness;
    const tasaDeCaptura = species.capture_rate;
    const ratioDeCaptura = ((tasaDeCaptura / 255) * 100).toFixed(2);
    const experienciaBase = data.base_experience;

    const CRECIMIENTO_ES = {
        slow: 'Lento',
        medium: 'Medio',
        fast: 'Rápido',
        'medium-slow': 'Medio‑lento',
        fluctuating: 'Fluctuante',
        erratic: 'Errático'
    };
    const indiceDeCrecimiento = CRECIMIENTO_ES[species.growth_rate.name] || species.growth_rate.name;

    /* Calculo de % machos y hembras */
    const tasaDeGenero = species.gender_rate;
    let macho = '', hembra = '';
    if (tasaDeGenero === -1) {
        macho = hembra = '—';
    } else if (tasaDeGenero === 0) {
        macho = '100%';
        hembra = '0%';
    } else if (tasaDeGenero === 8) {
        macho = '0%';
        hembra = '100%';
    } else {
        hembra = (tasaDeGenero / 8 * 100).toFixed(0) + '%';
        macho = (100 - tasaDeGenero / 8 * 100).toFixed(0) + '%';
    }

    /* Renderizado */
    document.getElementById('tab_1').innerHTML = `
    <div class="overview">
      <p><span class="genus">${genero}</span><br>${text}</p>
      <div class="heightWeight">
        <div>Peso - Altura<br><b>${peso} - ${altura}</b></div>
      </div>
      <div class="types">
        ${tipos.map(t => `
          <div class="poke__type__bg ${t}" title="${TYPE_ES[t]}">
            <img src="${icon(t)}" alt="${TYPE_ES[t]}">
          </div>`).join('')}
      </div>
    </div>

    <div class="about">
      <div>ID: <b class="id">#${String(id).padStart(3, '0')}</b></div>
      <div>Género:
        <b><i class="fa-solid fa-mars" style="color:#1f71ff"></i> ${macho}
           <i class="fa-solid fa-venus" style="color:#ff5c74"></i> ${hembra}</b>
      </div>
      <div>Habilidades: <b>${abilityNames.join(', ')}</b></div>
      <div>Ratio de Captura: <b>${tasaDeCaptura} (${ratioDeCaptura}% Probabilidad) </b></div>
      <div>Amistad Base: <b>${amistad} (${amistad < 50 ? "Bajo" : amistad < 100 ? "Normal" : "Alto"})</b></div>
      <div>Exp. Base: <b>${experienciaBase}</b></div>
      <div>Ratio de crecimiento: <b>${indiceDeCrecimiento}</b></div>
      <div>Grupo de Huevos: <b>${grupoNombreHuevos.join(', ')}</b></div>
    </div>`;

    activarTabs('tab_1');
}

async function estadisticasPokemon({data, typeDetails}) {

    /* Tomamos los valores individuales y el total */
    const vida = data.stats[0].base_stat;
    const ataque = data.stats[1].base_stat;
    const defensa = data.stats[2].base_stat;
    const spAtaque = data.stats[3].base_stat;
    const spDefensa = data.stats[4].base_stat;
    const velocidad = data.stats[5].base_stat;
    const total = vida + ataque + defensa + spAtaque + spDefensa + velocidad;

    /* Construimos la lista de stats con el total */
    const statsHtml = data.stats.map(s => `
    <div class="stat">
      <div>
        <span>${STAT_ES[s.stat.name] || s.stat.name.toUpperCase()}:</span>
        <span>${s.base_stat}</span>
      </div>
      <meter value="${s.base_stat}" min="0" max="255"
             low="70" high="120" optimum="150"></meter>
    </div>`).join('') + `
    <div class="stat">
      <div>
        <span>Total:</span><span>${total}</span>
      </div>
      <meter value="${total}" min="0" max="1530"
             low="500" high="720" optimum="1000"></meter>
    </div>`;

    /* Debil y fuerte contra */
    const debil = new Set();
    const fuerte = new Set();
    typeDetails.forEach(t => {
        t.damage_relations.no_damage_to.forEach(x => debil.add(x.name));
        t.damage_relations.double_damage_to.forEach(x => fuerte.add(x.name));
    });

    const iconImg = name => `
    <img src="/static/core/img/pokemon/icons/${name}.svg"
         class="poke__type__bg ${name}"
         title="${TYPE_ES[name]}"
         alt="${TYPE_ES[name]}">`;

    document.getElementById('tab_2').innerHTML = `
    <div class="stats">${statsHtml}</div>

    <div class="statTypes">
      <div class="statTypeText">Débil contra</div>
      <div class="statIconHolder">
        ${debil.size ? [...debil].map(iconImg).join('') : '—'}
      </div>
    </div>
    <div class="statTypes">
      <div class="statTypeText">Fuerte contra</div>
      <div class="statIconHolder">
        ${fuerte.size ? [...fuerte].map(iconImg).join('') : '—'}
      </div>
    </div>`;
}

async function evolucionesPokemon({species}) {
    const evoData = await fetchJSON(species.evolution_chain.url);
    const evoCadena = [];
    (function walk(node) {
        evoCadena.push(node);
        if (node.evolves_to[0]) walk(node.evolves_to[0]);
    })(evoData.chain);

    const evoHtml = evoCadena.map(n => {
        const pid = n.species.url.split('/').slice(-2, -1)[0];
        return `
      <div class="evolution__pokemon" onclick="window.location.href='/pokemon/${pid}/';">
        <h1>${n.species.name}</h1>
        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${pid}.png"
             alt="${n.species.name}">
      </div>`;
    }).join('<i class="fa-solid fa-caret-right fa-2x fa-beat"></i>');

    /* Variedades */
    const variedades = species.varieties.filter(v => !v.is_default);
    const varHtml = await Promise.all(variedades.map(async v => {
        const vid = v.pokemon.url.split('/').slice(-2, -1)[0];
        return `
        <div class="varieties__pokemon">
          <h1>${v.pokemon.name}</h1>
          <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${vid}.png"
               alt="${v.pokemon.name}">
        </div>`;
    }));

    document.getElementById('tab_3').innerHTML = `
    <div class="evolution">${evoHtml}</div>
    <div class="varieties">${varHtml.join('')}</div>`;

    const evoContenedor = document.querySelector('.evolution');
    const primeraCarta = evoContenedor?.querySelector('.evolution__pokemon');

    if (primeraCarta && matchMedia('(min-width:601px)').matches) {
        const media = primeraCarta.getBoundingClientRect().width / 2;
        evoContenedor.style.scrollPaddingLeft = `calc(50vw - ${media}px)`;
    }
}

function activarTabs(tabId) {
    document.querySelectorAll('[data-tab-info]').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
}

document.querySelectorAll('[data-tab-value]').forEach(tab => tab.addEventListener('click', () => {
    activarTabs(tab.dataset.tabValue.slice(1));
    document.getElementById(tab.dataset.tabValue.slice(1))
        .scrollIntoView({behavior: 'smooth'});
}));

/* Navegación avance y siguiente */
window.nextPokemon = e => {
    e?.preventDefault();
    const seg = window.location.pathname.split('/').filter(Boolean);
    window.location.href = `/pokemon/${parseInt(seg.pop(), 10) + 1}/`;
};

window.backButton = e => {
    e?.preventDefault();
    window.history.back();
};