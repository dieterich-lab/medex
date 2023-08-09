import {JSX} from "react";
import {PropsWithChildren, useId} from "react";

interface RadioButtonProps<T> {
    value: T,
    onChange: (x: T) => void,
    labels_by_value: Map<T, JSX.Element>
}

function RadioButtons<T>(props: PropsWithChildren<RadioButtonProps<T>>): JSX.Element {
    let items: JSX.Element[] = [];
    props.labels_by_value.forEach((label, value) => {
        const id = useId();
        items.push(
            (<input
                type="radio"
                onClick={() => props.onChange(value)}
                checked={props.value == value}
                id={id}
                className="btn-check"
                autoComplete="off"
            />),
            (<label className="btn btn-outline-primary" htmlFor={id}>
                {label}
            </label>)
        );
    });

    return (<div className="btn-group" role="group" aria-label="Basic radio toggle button group">
        {items}
    </div>);
}

export {RadioButtons};
