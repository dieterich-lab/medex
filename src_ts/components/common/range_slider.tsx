import MultiRangeSlider from 'multi-range-slider-react';
import {ChangeEventHandler, FocusEventHandler, useEffect, useRef, useState} from 'react';

interface RangeSliderProps{
    from_value: number,
    to_value: number,
    min: number,
    max: number,
    on_change: (from_value: number, to_value: number) => void,
}

enum ValueType {
    From,
    To,
}

interface MyTextInputProps extends Omit<RangeSliderProps, 'on_change'> {
    value: number,
    value_type: ValueType,
    on_change: (x: number) => void,
    on_blur: (x: number) => void,
}

interface TextFieldState {
    from_value: number,
    to_value: number,
}

function RangeSlider(props: RangeSliderProps) {
    const [text_field_state, set_text_field_state] = useState<TextFieldState>({
        from_value: props.from_value,
        to_value: props.to_value,
    });

    const update_by_slider = (data: { minValue: number; maxValue: number; }) => {
        if (
            data.minValue != text_field_state.from_value
            || data.maxValue != text_field_state.to_value
        ) {
            set_text_field_state({
                from_value: data.minValue,
                to_value: data.maxValue,
            });
        }
        if (
            props.from_value != data.minValue
            || props.to_value != data.maxValue
        ) {
            props.on_change(data.minValue, data.maxValue);
        }
    }
    const step = Math.pow(10,Math.round(Math.log10(props.max - props.min)) - 1);

    return (
        <div>
            <MultiRangeSlider
                min={props.min}
                max={props.max}
                step={step}
                minValue={props.from_value}
                maxValue={props.to_value}
                onInput={update_by_slider}
            />
            <div className="rangs-slider-extra-controls">
                from&nbsp;
                <MyTextInput
                    {...props}
                    value={text_field_state.from_value}
                    value_type={ValueType.From}
                    on_change={(x) => on_change(props, {from_value: x, to_value: text_field_state.to_value}, set_text_field_state)}
                    on_blur={(x) => on_blur(props, {from_value: x, to_value: text_field_state.to_value}, set_text_field_state, ValueType.From)}
                />
                &nbsp;to&nbsp;
                <MyTextInput
                    {...props}
                    value={text_field_state.to_value}
                    value_type={ValueType.To}
                    on_change={(x) => on_change(props, {from_value: text_field_state.from_value, to_value: x}, set_text_field_state)}
                    on_blur={(x) => on_blur(props, {from_value: text_field_state.from_value, to_value: x}, set_text_field_state, ValueType.To)}
                />
            </div>
        </div>
    );
}

function MyTextInput(props: MyTextInputProps) {
    const ref = useRef<any>(null);

    useEffect(() => {
        if ( ref.current != null ) {
            ref.current.value = props.value;
        }
    }, [ref.current, props.value])

    const on_change: ChangeEventHandler<HTMLInputElement> = (e) => {
        const new_value_as_number = parseFloat(e.target.value);
        props.on_change(new_value_as_number);
    };

    const on_blur: FocusEventHandler<HTMLInputElement> = (e) => {
        const new_value_as_number = parseFloat(e.target.value);
        props.on_blur(new_value_as_number);
    }

    return (
        <input
            ref={ref}
            type="text"
            onChange={on_change}
            onBlur={on_blur}
            className="range-slider-text-input"
        />
    );
}

function on_change(
    props: RangeSliderProps,
    new_state: TextFieldState,
    set_text_field_state: (x: TextFieldState) => void
) {
    // During editing the user may enter out-of-range
    // values even if the final result is in range, e.g.
    //
    // Min: 10, Value: 12
    // User want to enter 15
    // Keys: Backspace (-> value=1, out of range!) 5 (value=15, OK)
    //
    // We don't want to overwrite such input after the backspace.
    // So we propagate the change only if reasonable.
    if ( is_sane_value_pair(new_state, props) ) {
        set_text_field_state(new_state)
        props.on_change(new_state.from_value, new_state.to_value);
    }
}

function is_sane_value_pair(state: TextFieldState, props: RangeSliderProps) {
    return (
        state.from_value != null
        && state.to_value != null
        && props.min <= state.from_value
        && state.from_value <= state.to_value
        && state.to_value <= props.max
    )
}

function on_blur(
    props: RangeSliderProps,
    new_state: TextFieldState,
    set_text_field_state: (x: TextFieldState) => void,
    value_type: ValueType,
) {
    // On "focus out" we force sane values - however we prefer
    // to only touch the field not edited by the user.
    let cooked_from = new_state.from_value >= props.min ? new_state.from_value : props.min;
    let cooked_to = new_state.to_value <= props.max ? new_state.to_value : props.max;
    if ( cooked_from > cooked_to ) {
        if ( value_type == ValueType.From ) {
            cooked_to = cooked_from;
        } else {
            cooked_from = cooked_to;
        }
    }
    props.on_change(cooked_from, cooked_to);
}

export {RangeSlider};
