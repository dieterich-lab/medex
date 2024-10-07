import {PropsWithChildren} from "react";


function TText(props: PropsWithChildren<object>) {
    return (
        <div className="col mt-2">
            {props.children}
        </div>
    )
}

export {TText};
