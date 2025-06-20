import {useEffect, useState} from "react";
import {get_message} from "../services/message_catalog.ts";

function HeadlineTitle() {
    const [headline, set_headline] = useState<string>('None')

    useEffect(() => {
        async function setup() {
            set_headline(await get_message('headline_title'))
        }
        setup().catch(() => {})
    }, []);

    if ( headline == 'None' ) {
        return <div />
    } else {
        return <h1 className={'text-center'}>{headline}</h1>
    }
}

export {HeadlineTitle};