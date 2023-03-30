
function switch_nav_item(name) {
    const active_id = `${name}_nav`;
    let elements = document.getElementsByClassName("nav-link");

    for (let i = 0; i < elements.length; i++) {
        if ( elements[i].id === active_id ) {
            elements[i].classList.add('active');
        } else {
            elements[i].classList.remove('active');
        }
    }
}

export {switch_nav_item};