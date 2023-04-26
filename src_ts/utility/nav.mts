
function switch_nav_item(name) {
    const active_id = `${name}_nav`;
    let nav_links = Array.from(document.querySelectorAll("#nav_bar .nav-link"));
    for ( let element of nav_links ) {
        if ( element.id === active_id ) {
            element.classList.add('active');
        } else {
            element.classList.remove('active');
        }
    }
}

export {switch_nav_item};