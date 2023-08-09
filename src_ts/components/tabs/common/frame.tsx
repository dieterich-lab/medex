import {PropsWithChildren, useEffect, useState} from "react";

interface TabFrameProps {}

function TabFrame(props: PropsWithChildren<TabFrameProps>) {
    return (
        <div className="tab-frame">
            {props.children}
        </div>
    );
}

export {TabFrame};
