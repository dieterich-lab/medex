interface DownloadLinkProps {
    url: string,
    filename?: string
}

function DownloadLink(props: DownloadLinkProps) {
    return (
        <a href={props.url} className="btn btn-outline-info" download={props.filename}>Download</a>
    );
}

export {DownloadLink};