import {PropsWithChildren} from "react";
import {ButtonProps} from "./common/props";

interface NavigationButtonProps extends ButtonProps {
    id: string,
    key: string,
    is_active: boolean,
}

function NavigationButton(props: PropsWithChildren<NavigationButtonProps>) {
    const classes = props.is_active ? "nav-link active" : "nav-link";
    return <li id={`li_${props.id}`} className="nav-item">
        <button id={props.id} className={classes} onClick={props.on_click}>
            {props.children}
        </button>
    </li>;
}

export {NavigationButton, NavigationButtonProps};
