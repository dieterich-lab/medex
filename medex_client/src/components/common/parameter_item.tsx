import {PropsWithChildren} from "react";

interface ParameterItemProps {
    show?: boolean,
}

function ParameterItem(props: PropsWithChildren<ParameterItemProps>) {
    if ( props?.show === false ) {
        return <div/>;
    }
    return (
        <div className="sub-card">
            {props.children}
        </div>
    );
}

export {ParameterItem};
