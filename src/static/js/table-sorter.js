(function(){
  if(window.TableSorterLoaded) return;
  window.TableSorterLoaded = true;

  function normalizeCell(cell){
    if(!cell) return '';
    if(cell.dataset && cell.dataset.sort) return cell.dataset.sort;
    const badges = cell.querySelectorAll && cell.querySelectorAll('.badge');
    if(badges && badges.length) return Array.from(badges).map(b=>b.textContent.trim()).join(', ');
    const strong = cell.querySelector && cell.querySelector('strong');
    if(strong) return strong.textContent.trim() + ' ' + cell.textContent.replace(strong.textContent,'').trim();
    return cell.textContent.trim();
  }

  function attachToTables(){
    document.querySelectorAll('table.sortable-table').forEach(table=>{
      const tbody = table.tBodies[0];
      if(!tbody) return;
      table.querySelectorAll('.sort-btn').forEach(btn=>{
        const col = parseInt(btn.dataset.col,10);
        const type = btn.dataset.type || 'text';
        btn.addEventListener('click', (ev)=>{
          ev.stopPropagation();
          const current = table.dataset.sortCol === String(col) ? table.dataset.sortDir : null;
          const asc = current !== 'asc';
          const rows = Array.from(tbody.rows);
          rows.sort((a,b)=>{
            let A = normalizeCell(a.cells[col]), B = normalizeCell(b.cells[col]);
            if(type==='num'){A = parseFloat(A)||0; B = parseFloat(B)||0; return asc?A-B:B-A}
            if(type==='date'){A = Date.parse(A)||Date.parse(a.cells[col].dataset.sort||'')||0; B = Date.parse(B)||Date.parse(b.cells[col].dataset.sort||'')||0; return asc?A-B:B-A}
            A=(A||'').toLowerCase(); B=(B||'').toLowerCase();
            if(A<B) return asc?-1:1; if(A>B) return asc?1:-1; return 0;
          });
          rows.forEach(r=>tbody.appendChild(r));
          table.dataset.sortCol = String(col); table.dataset.sortDir = asc ? 'asc' : 'desc';
          table.querySelectorAll('.sort-indicator').forEach(ind=>ind.classList.remove('asc','desc'));
          const ind = btn.querySelector('.sort-indicator'); if(ind) ind.classList.add(asc ? 'asc' : 'desc');
          table.querySelectorAll('thead th').forEach(th => th.removeAttribute('aria-sort'));
          const th = btn.closest('th'); if(th) th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
        });

        const th = btn.closest('th');
        if(th){ th.classList.add('sortable'); th.tabIndex = 0;
          th.addEventListener('click', (ev) => { if(!ev.target.closest('button')) btn.click(); });
          th.addEventListener('keydown', (ev) => { if(ev.key==='Enter' || ev.key===' ') { ev.preventDefault(); btn.click(); }});
        }
      });

      table.querySelectorAll('button.row-action-toggle').forEach(toggle=>{
        toggle.addEventListener('click', (ev)=>{
          ev.stopPropagation();
          document.querySelectorAll('.context-menu').forEach(m=>m.style.display='none');
          const menu = toggle.parentElement.querySelector('.context-menu');
          if(menu){ menu.style.display = menu.style.display === 'block' ? 'none' : 'block'; const rect = toggle.getBoundingClientRect(); menu.style.left = (rect.right - 160) + 'px'; menu.style.top = (rect.bottom + 6) + 'px'; }
        });
      });

      document.addEventListener('click', ()=>document.querySelectorAll('.context-menu').forEach(m=>m.style.display='none'));
    });
  }

  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', attachToTables); } else { attachToTables(); }
})();