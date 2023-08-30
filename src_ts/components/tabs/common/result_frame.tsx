import {PropsWithChildren} from "react";

interface ResultFrameProps {}

export function ResultFrame(props: PropsWithChildren<ResultFrameProps>) {
    return (
        <div className="card">
            <div className="card-body">
                {props.children}
            </div>
        </div>
    );
}