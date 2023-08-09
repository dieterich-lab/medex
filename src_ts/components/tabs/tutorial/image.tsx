interface Props {
    name: string,
    className?: string
}

function TImage(props: Props) {
    const url = `/static/images/${props.name}`;
    const size_class = props.className ? props.className : 'image-medium';
    return (<div className="col">
        <img src={url} className={`mt-2 ${size_class}`}/>
    </div>);
}

export {TImage};
