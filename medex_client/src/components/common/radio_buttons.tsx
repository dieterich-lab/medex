import {JSX} from "react";
import {PropsWithChildren, useId} from "react";


interface RadioButtonProps<T> {
    value: T,
    onChange: (x: T) => void,
    label_by_value: Map<T, JSX.Element>
}

function RadioButtons<T>(props: PropsWithChildren<RadioButtonProps<T>>): JSX.Element {
    const items: JSX.Element[] = [];
    for ( const value of props.label_by_value.keys() ) {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const id = useId();
        const label = props.label_by_value.get(value);

        items.push(
            (<input
                type="radio"
                onChange={() => props.onChange(value)}
                checked={props.value == value}
                id={id}
                className="btn-check"
                autoComplete="off"
                key={`input_${id}`}
            />),
            (<label className="btn btn-outline-primary" htmlFor={id} key={`label_${id}`}>
                {label}
            </label>)
        );
    }

    return (<div className="btn-group" role="group" aria-label="Basic radio toggle button group">
        {items}
    </div>);
}


export {RadioButtons};
