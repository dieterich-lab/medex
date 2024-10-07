import {PropsWithChildren} from "react";

export function ResultFrame(props: PropsWithChildren<object>) {
    return (
        <div className="card">
            <div className="card-body">
                {props.children}
            </div>
        </div>
    );
}