import {PropsWithChildren} from "react";

interface Props {}

function TText(props: PropsWithChildren<Props>) {
    return (
        <div className="col mt-2">
            {props.children}
        </div>
    )
}

export {TText};
