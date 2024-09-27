import {JSX, useEffect, useState} from "react";
import {clear_error, init_user_feedback} from "../utility/user_feedback";


function StatusBar(): JSX.Element {
    const [error_message, set_error_message] = useState<string | null>(null);
    const [busy_message, set_busy_message] = useState<string | null>(null);

    useEffect(() => {
        init_user_feedback(set_error_message, set_busy_message);
    }, [set_error_message, set_busy_message])

    const error = error_message == null ? <div/> :
        <div className="alert alert-danger mt-2" role="alert">
            {error_message}
            <button type="button" className="btn-close" aria-label="Close" onClick={clear_error}/>
        </div>;

    const busy = busy_message == null ? <div/> :
        <div className="busy-bar mt-2">
            <div className="spinner-border busy-spinner" role="status">
                <span className="visually-hidden">Busy ...</span>
            </div>
            <div className="busy-message ml-2" role="status">
                {busy_message}
            </div>
        </div>

    return (
        <div>
            {error}
            {busy}
        </div>
    );
}

export {StatusBar};