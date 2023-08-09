import {PropsWithChildren} from "react";

interface NoProps {}

function TutorialFrame(props: PropsWithChildren<NoProps>) {
    return (
        <div className="container">
            {props.children}
        </div>
    )
}

export {TutorialFrame};
