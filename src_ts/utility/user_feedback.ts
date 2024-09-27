class UserError extends Error {}

class HTTPError extends Error {}

let set_error_message: ((x: string|null) => void) | null = null;
let set_busy_message: ((x: string|null) => void) | null = null;

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

function report_busy(message: string) {
    document.body.style.cursor = 'wait';
    if ( set_busy_message == null ) {
        console.log(`report_busy('${message}') called before initialization!`);
    } else {
        set_busy_message(message);
    }
}

function clear_busy() {
    document.body.style.cursor = '';
    if ( set_busy_message == null ) {
        console.log('clear_busy() called before initialization!');
    } else {
        set_busy_message(null);
    }
}

function init_user_feedback(
    new_set_error_message: (x: string|null) => void,
    new_set_busy_message: (x: string|null) => void,
) {
    set_error_message = new_set_error_message;
    set_busy_message = new_set_busy_message;
}

export {init_user_feedback, report_error, clear_error, report_busy, clear_busy, UserError, HTTPError};