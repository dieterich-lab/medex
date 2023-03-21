
class UserError extends Error {}

class HTTPError extends Error {}

function report_error(error) {
    const message = error instanceof Error ? error.message : error;
    if ( !(error instanceof UserError) && !(error instanceof HTTPError) && error instanceof Error ) {
        console.log(error.stack)
    }
    let div = document.getElementById('error_div');
    div.innerHTML = `
        <div class="alert alert-danger mt-2" role="alert">
            ${message}
            <span id="error_close_button" class="close" aria-label="Close"> &times;</span>
        </div>
    `;
    let close_button = document.getElementById('error_close_button');
    close_button.addEventListener('click', clear_error);
}

function clear_error() {
    let div = document.getElementById('error_div');
    div.innerHTML = null;
}

export {report_error, clear_error, UserError, HTTPError};