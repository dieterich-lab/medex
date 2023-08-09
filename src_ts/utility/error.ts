class UserError extends Error {}

class HTTPError extends Error {}

let set_error_message: ((x: string|null) => void) | null = null;

function report_error(error: unknown) {
    const message =
        error instanceof Error    ? error.message :
        typeof error === 'string' ? error       :
        JSON.stringify(error);
    if ( !(error instanceof UserError) && !(error instanceof HTTPError) && error instanceof Error ) {
        console.log(error.stack)
    }
    if ( set_error_message == null ) {
        console.log('report_error() called before initialization!');
        console.log(message);
    } else {
        set_error_message(message);
    }
}

function clear_error() {
    console.log(`set_error_message: ${set_error_message}`);
    if ( set_error_message == null ) {
        console.log('clear_error() called before initialization!');
    } else {
        set_error_message(null);
    }
}

function init_error_handling(new_set_error_message: (x: string|null) => void) {
    set_error_message = new_set_error_message;
}

export {init_error_handling, report_error, clear_error, UserError, HTTPError};