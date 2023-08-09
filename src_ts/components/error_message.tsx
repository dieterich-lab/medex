import {JSX} from "react";
import {clear_error} from "../utility/error";

interface ErrorMessageProps {
    message: string | null,
}

function ErrorMessage(props: ErrorMessageProps): JSX.Element {
    if ( props.message == null ) {
        return <div />;
    }
    return (
         <div className="alert alert-danger mt-2" role="alert">
             {props.message}
             <button type="button" className="btn-close" aria-label="Close" onClick={clear_error}/>
         </div>
    );
}

export {ErrorMessage};