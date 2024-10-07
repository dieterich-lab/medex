
interface ResultsButtonProps {
    onClick: () => void,
}

function ResultsButton(props: ResultsButtonProps) {
    return (
        <button type="button" className="btn btn-outline-info card-submit" onClick={props.onClick}
        >
            Result
        </button>
    );
}

export {ResultsButton};
