import {PropsWithChildren} from "react";

function TabFrame(props: PropsWithChildren<object>) {
    return (
        <div className="tab-frame">
            {props.children}
        </div>
    );
}

export {TabFrame};
