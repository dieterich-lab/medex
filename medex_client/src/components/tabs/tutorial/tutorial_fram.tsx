import {PropsWithChildren} from "react";


function TutorialFrame(props: PropsWithChildren<object>) {
    return (
        <div className="container">
            {props.children}
        </div>
    )
}

export {TutorialFrame};
