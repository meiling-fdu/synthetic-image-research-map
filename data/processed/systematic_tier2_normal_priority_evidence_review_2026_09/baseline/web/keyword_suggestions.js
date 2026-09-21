/* Suggestions assist navigation; the existing keyword predicate remains authoritative. */
(function (root) {
  const normalize = value => String(value || '').trim().toLocaleLowerCase();
  function build(entries) {
    const seen = new Set();
    return entries.filter(entry => {
      const key = `${entry.type}:${entry.type === 'Authors' ? normalize(entry.label) : entry.id}`;
      if (!entry.label || seen.has(key)) return false;
      seen.add(key);
      return true;
    }).map(entry => ({...entry, search: normalize(entry.label)}));
  }
  function find(index, query) {
    const term = normalize(query);
    if (term.length < 2) return [];
    return ['Papers', 'Authors', 'Institutions'].flatMap(type => index
      .filter(entry => entry.type === type && entry.search.includes(term))
      .sort((a, b) => Number(b.search.startsWith(term)) - Number(a.search.startsWith(term))
        || a.label.localeCompare(b.label))
      .slice(0, 3));
  }
  function mount(input, list, choose) {
    let index = [], matches = [], active = -1;
    function close() {
      list.hidden = true;
      active = -1;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
    }
    function update() {
      matches = find(index, input.value);
      active = -1;
      input.removeAttribute('aria-activedescendant');
      list.replaceChildren();
      let group;
      matches.forEach((entry, i) => {
        if (!i || matches[i - 1].type !== entry.type) {
          group = document.createElement('div');
          group.setAttribute('role', 'group');
          group.setAttribute('aria-label', entry.type);
          const heading = document.createElement('div');
          heading.className = 'keyword-suggestion-heading';
          heading.textContent = entry.type;
          heading.setAttribute('aria-hidden', 'true');
          group.append(heading);
          list.append(group);
        }
        const option = document.createElement('div');
        option.id = `keyword-suggestion-${i}`;
        option.setAttribute('role', 'option');
        option.setAttribute('aria-selected', 'false');
        option.dataset.suggestionIndex = i;
        const start = entry.search.indexOf(normalize(input.value));
        const length = input.value.trim().length;
        const mark = document.createElement('mark');
        mark.textContent = entry.label.slice(start, start + length);
        option.append(entry.label.slice(0, start), mark, entry.label.slice(start + length));
        group.append(option);
      });
      list.hidden = !matches.length;
      input.setAttribute('aria-expanded', String(matches.length > 0));
    }
    function select(i) {
      const entry = matches[i];
      close();
      if (entry) choose(entry);
    }
    input.addEventListener('input', event => { if (!event.isComposing) update(); });
    input.addEventListener('compositionstart', close);
    input.addEventListener('compositionend', update);
    input.addEventListener('focus', update);
    input.addEventListener('blur', close);
    input.addEventListener('keydown', event => {
      if (event.isComposing) return;
      if (event.key === 'Escape' && !list.hidden) {
        event.preventDefault();
        event.stopPropagation();
        close();
      } else if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
        if (list.hidden) update();
        if (!matches.length) return;
        event.preventDefault();
        active = (active + (event.key === 'ArrowDown' ? 1 : active < 0 ? 0 : -1) + matches.length) % matches.length;
        [...list.querySelectorAll('[role="option"]')].forEach((option, i) => {
          option.setAttribute('aria-selected', String(i === active));
          if (i === active) {
            input.setAttribute('aria-activedescendant', option.id);
            option.scrollIntoView({block: 'nearest'});
          }
        });
      } else if (event.key === 'Enter' && !list.hidden && active >= 0) {
        event.preventDefault();
        select(active);
      }
    });
    list.addEventListener('pointerdown', event => {
      const option = event.target.closest('[data-suggestion-index]');
      if (!option) return;
      event.preventDefault();
    });
    list.addEventListener('click', event => {
      const option = event.target.closest('[data-suggestion-index]');
      if (!option) return;
      select(Number(option.dataset.suggestionIndex));
    });
    document.addEventListener('pointerdown', event => {
      if (event.target !== input && !list.contains(event.target)) close();
    });
    return {close, setEntries(entries) { index = build(entries); close(); }};
  }
  const api = {build, find, mount};
  if (typeof module !== 'undefined') module.exports = api;
  else root.KeywordSuggestions = api;
})(globalThis);
