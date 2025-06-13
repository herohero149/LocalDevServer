document.addEventListener('DOMContentLoaded', () => {
    // Add loading bar
    const loading = document.createElement('div');
    loading.className = 'loading';
    document.body.appendChild(loading);

    // Sort functionality with enhanced animations
    const table = document.querySelector('table');
    const headers = table.querySelectorAll('th');
    const tbody = table.querySelector('tbody');
    let currentSort = { column: -1, asc: true };

    // Stagger animation for initial load
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.forEach((row, i) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';
        setTimeout(() => {
            row.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            row.style.opacity = '1';
            row.style.transform = 'none';
        }, i * 50);
    });

    headers.forEach((header, index) => {
        header.addEventListener('click', () => {
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Remove previous sort indicators
            headers.forEach(h => h.classList.remove('asc', 'desc'));

            // Determine sort direction
            if (currentSort.column === index) {
                currentSort.asc = !currentSort.asc;
            } else {
                currentSort.column = index;
                currentSort.asc = true;
            }

            // Add sort indicator with animation
            header.classList.add(currentSort.asc ? 'asc' : 'desc');

            // Animate rows out with stagger
            rows.forEach((row, i) => {
                setTimeout(() => {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(20px)';
                }, i * 30);
            });

            // Sort rows
            setTimeout(() => {
                rows.sort((a, b) => {
                    const aCol = a.querySelectorAll('td')[index].textContent;
                    const bCol = b.querySelectorAll('td')[index].textContent;
                    
                    let comparison;
                    if (index === 1) { // Size column
                        comparison = parseSizeToBytes(aCol) - parseSizeToBytes(bCol);
                    } else {
                        comparison = aCol.localeCompare(bCol, undefined, {numeric: true, sensitivity: 'base'});
                    }
                    
                    return currentSort.asc ? comparison : -comparison;
                });

                // Clear tbody
                while (tbody.firstChild) {
                    tbody.removeChild(tbody.firstChild);
                }

                // Add sorted rows back with staggered animation
                rows.forEach((row, i) => {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(-20px)';
                    tbody.appendChild(row);
                    
                    // Trigger animation with stagger
                    setTimeout(() => {
                        row.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                        row.style.opacity = '1';
                        row.style.transform = 'none';
                    }, i * 50);
                });
            }, rows.length * 30 + 100);
        });
    });

    // Enhance link interactions
    document.querySelectorAll('a').forEach(link => {
        // Create and add hover effect element
        const hoverEffect = document.createElement('div');
        hoverEffect.className = 'hover-effect';
        
        link.addEventListener('mouseenter', (e) => {
            link.style.transform = 'translateX(4px)';
        });

        link.addEventListener('mouseleave', (e) => {
            link.style.transform = 'none';
        });

        link.addEventListener('click', () => {
            loading.style.display = 'block';
            loading.style.opacity = '1';
        });
    });

    function parseSizeToBytes(sizeStr) {
        if (sizeStr === 'N/A') return -1;
        const num = parseFloat(sizeStr);
        if (sizeStr.includes('MB')) return num * 1024 * 1024;
        if (sizeStr.includes('KB')) return num * 1024;
        return num;
    }

    // Enhanced loading bar behavior
    window.addEventListener('load', () => {
        loading.style.opacity = '0';
        setTimeout(() => {
            loading.style.display = 'none';
        }, 500);
    });

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});
