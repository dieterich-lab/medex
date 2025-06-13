import {get_message} from "../../services/message_catalog.ts";
import {useEffect, useState} from "react";

interface Props {
    id: string
    custom?: string
}

function M(props: Props) {
    const [text, set_text] = useState<string>('')
    useEffect(() => {
        async function setup() {
            set_text(await get_message(props.id))
        }
        if ( props.custom ) {
            set_text(props.custom)
        } else {
            setup().catch(() => {})
        }
    }, [props]);
    return <span>{text}</span>
}

export {M};