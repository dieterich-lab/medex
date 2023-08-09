import {PropsWithChildren} from "react";

interface Props {
    headline: string;
}

function TSection(props: PropsWithChildren<Props>) {
    return <div>
        <div className="row">
            <h2>{props.headline}</h2>
        </div>
        <div className="d-flex flex-wrap">
            {props.children}
        </div>
    </div>
}

export {TSection};
