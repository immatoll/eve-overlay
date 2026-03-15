const contentEl = document.getElementById('content');
const navLinksEl = document.getElementById('nav-links');
const searchEl = document.getElementById('search');

let handbookData = [];

// Load JSON via fetch
fetch('data/handbook.json')
  .then(res => res.json())
  .then(data => {
    handbookData = data;
    renderSidebar(data);
    handleNavigation();
  })
  .catch(err => console.error('Error loading JSON:', err));

// Render sidebar
function renderSidebar(data, parentEl = navLinksEl) {
  parentEl.innerHTML = '';

  data.forEach(item => {
    const link = document.createElement('a');
    link.href = `#${item.id}`;
    link.textContent = item.title;
    link.classList.add('sidebar-link');
    parentEl.appendChild(link);

    if (item.children && item.children.length > 0) {
      const subList = document.createElement('div');
      subList.classList.add('subsection');
      renderSidebar(item.children, subList);
      parentEl.appendChild(subList);
    }
  });
}

// Search filter
searchEl.addEventListener('input', () => {
  const term = searchEl.value.toLowerCase();

  function filterItems(items) {
    return items
      .map(item => {
        const matchSelf = item.title.toLowerCase().includes(term);
        const matchChildren = item.children ? filterItems(item.children) : [];
        if (matchSelf || matchChildren.length) {
          return { ...item, children: matchChildren };
        }
        return null;
      })
      .filter(Boolean);
  }

  const filtered = filterItems(handbookData);
  renderSidebar(filtered);
});

// Hash navigation & load markdown via fetch
function handleNavigation() {
  window.addEventListener('hashchange', () => {
    const id = location.hash.slice(1);
    const entry = findEntryById(handbookData, id);
    if (entry) {
      fetch(entry.file)
        .then(res => res.text())
        .then(md => {
          contentEl.innerHTML = marked.parse(md);

          // intercept internal links
          contentEl.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', e => {
              e.preventDefault();
              location.hash = link.getAttribute('href').slice(1);
            });
          });
        })
        .catch(err => {
          contentEl.innerHTML = `<p style="color:red;">Error loading file: ${err}</p>`;
        });

      updateActiveSidebar(id);
    }
  });

  if (location.hash) window.dispatchEvent(new HashChangeEvent("hashchange"));
}

// Recursive search
function findEntryById(data, id) {
  for (const item of data) {
    if (item.id === id) return item;
    if (item.children) {
      const child = findEntryById(item.children, id);
      if (child) return child;
    }
  }
  return null;
}

// Highlight active sidebar link
function updateActiveSidebar(id) {
  navLinksEl.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
  });
}