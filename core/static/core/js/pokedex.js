window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('poke-form');
    const input = form.querySelector('input[name="pokemon"]');
    const dataList = document.getElementById('pokemon-list');
    const pokeName = document.querySelector('[data-poke-name]');
    const pokeImg = document.querySelector('[data-poke-img]');
    const pokeId = document.querySelector('[data-poke-id]');
    const pokeTypes = document.querySelector('[data-poke-types]');
    const pokeStats = document.querySelector('[data-poke-stats]');

    const pokeAudio = document.getElementById('poke-sound');
    pokeAudio.volume = 0.5;
    pokeAudio.preload = 'auto';

    const statLabels = {
        hp: 'Vida',
        attack: 'Ataque',
        defense: 'Defensa',
        'special-attack': 'Ataque Especial',
        'special-defense': 'Defensa Especial',
        speed: 'Velocidad',
    };

    const type = {
        electric: 'Eléctrico',
        normal: 'Normal',
        fire: 'Fuego',
        water: 'Agua',
        ice: 'Hielo',
        rock: 'Roca',
        flying: 'Volador',
        grass: 'Hierba',
        psychic: 'Psíquico',
        ghost: 'Fantasma',
        bug: 'Bicho',
        poison: 'Veneno',
        ground: 'Tierra',
        dragon: 'Dragón',
        steel: 'Acero',
        fighting: 'Lucha',
        default: 'Desconocido'
    };

    const typeColors = {
        electric: '#eed365', normal: '#B09398', fire: '#FF675C',
        water: '#0596C7', ice: '#AFEAFD', rock: '#999799',
        flying: '#7AE7C7', grass: '#4A9681', psychic: '#FFC6D9',
        ghost: '#561D25', bug: '#A2FAA3', poison: '#795663',
        ground: '#D2B074', dragon: '#DA627D', steel: '#1D8A99',
        fighting: '#2F2F2F', default: '#2A1A1F',
    };

    // Función que hace el fetch y renderiza (o not found)
    function fetchPokemon(name) {
        if (!name) return renderNotFound();
        fetch(`http://127.0.0.1:8001/pokemon/${name}`)
            .then(res => {
                if (!res.ok) throw new Error(`Status ${res.status}`);
                return res.json();
            })
            .then(renderPokemonData)
            .catch(err => {
                console.error('Error al obtener Pokémon:', err);
                renderNotFound();
            });
    }

    document.getElementById('poke-form')
        .addEventListener('submit', e => {
            e.preventDefault();
            fetchPokemon(input.value.trim().toLowerCase());
        });

    let debounceTimer;
    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchPokemon(input.value.trim().toLowerCase());
        }, 400);
    });

    fetch('https://pokeapi.co/api/v2/pokemon?limit=100000')
        .then(res => res.json())
        .then(json => {
            json.results.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.name;
                dataList.appendChild(opt);
            });
        })
        .catch(err => console.error('Error cargando lista de Pokémon:', err));

    // 2) Asociamos el submit del formulario
    form.addEventListener('submit', searchPokemon);

    // 3) Función de búsqueda
    function searchPokemon(event) {
        event.preventDefault();
        const name = input.value.trim().toLowerCase();
        if (!name) return;

        fetch(`http://127.0.0.1:8001/pokemon/${name}`)
            .then(res => {
                if (!res.ok) throw new Error(`Status ${res.status}`);
                return res.json();
            })
            .then(data => renderPokemonData(data))
            .catch(err => {
                console.error('Error al obtener Pokémon:', err);
                renderNotFound();
            });
    }

    // 4) Renderizado de la tarjeta
    function renderPokemonData(data) {
        const {id, name, stats, types, sprite} = data;
        pokeName.textContent = name;
        pokeImg.src = sprite;
        pokeId.textContent = `Nº ${id}`;
        setCardColor(types);
        renderPokemonTypes(types);
        renderPokemonStats(stats);

        // ¡Reproducir sonido!
        pokeAudio.currentTime = 0;
        pokeAudio.play().catch(() => {
        });
    }

    function setCardColor(types) {
        const one = typeColors[types[0].name];
        const two = types[1] ? typeColors[types[1].name] : typeColors.default;
        pokeImg.style.background = `radial-gradient(${two} 33%, ${one} 33%)`;
        pokeImg.style.backgroundSize = '5px 5px';
    }

    function renderPokemonTypes(types) {
        pokeTypes.innerHTML = '';
        types.forEach(t => {
            const el = document.createElement('div');
            el.style.color = typeColors[t.name] || typeColors.default;
            el.textContent = type[t.name] ||
                (t.name.charAt(0).toUpperCase() + t.name.slice(1));

            pokeTypes.appendChild(el);
        });
    }

    function renderPokemonStats(stats) {
        pokeStats.innerHTML = '';
        stats.forEach(s => {
            const statEl = document.createElement('div');
            const nameEl = document.createElement('div');
            const valEl = document.createElement('div');

            nameEl.textContent = statLabels[s.name]
                || s.name.charAt(0).toUpperCase() + s.name.slice(1);
            valEl.textContent = s.base_stat;

            statEl.append(nameEl, valEl);
            pokeStats.appendChild(statEl);
        });
    }

    function renderNotFound() {
        pokeName.textContent = 'No encontrado';
        pokeImg.src = pokeImg.dataset.defaultSrc;
        pokeImg.style.background = '#fff';
        pokeTypes.innerHTML = '';
        pokeStats.innerHTML = '';
        pokeId.textContent = '';
    }
});