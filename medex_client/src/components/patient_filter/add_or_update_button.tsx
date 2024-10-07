import {ButtonProps} from '../common/props';

function AddOrUpdateButton(props: ButtonProps) {
    return (
        <button type='button' className='btn btn-outline-info card-submit'
            onClick={props.on_click}
        >
            Add or Update Filter
        </button>
    );
}

export {AddOrUpdateButton};
