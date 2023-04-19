import {switch_nav_item} from './nav.mjs';

test('simple nav check', () => {
    document.body.innerHTML = `
        <nav id="nav_bar" class="navbar navbar-light bg-light">
            <ul class="nav nav-pills mx-auto">
                <li class="nav-item"><a class="nav-link" href="/item1/" id="item1_nav">Item 1</a></li>
                <li class="nav-item"><a class="nav-link" href="/item2/" id="item2_nav">Item 2</a></li>
                <li class="nav-item"><a class="nav-link active" href="/item3/" id="item3_nav">Item 3</a></li>
            </ul>
        </nav>
    `;
    switch_nav_item('item2');
    expect(document.getElementById('item2_nav').classList).toContain('active');
    expect(document.getElementById('item3_nav').classList).not.toContain('active');
});