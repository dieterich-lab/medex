"use client"

import { useEffect } from "react";

function BootstrapClient() {
    useEffect(() => {
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        require("bootstrap/dist/js/bootstrap.bundle.js");
    }, []);

    return <div/>;
}

export default BootstrapClient;