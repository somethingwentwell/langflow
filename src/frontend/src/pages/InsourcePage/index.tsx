import { useContext, useEffect, useState } from "react";
import { TabsContext } from "../../contexts/tabsContext";

import { useNavigate } from "react-router-dom";
import IconComponent from "../../components/genericIconComponent";
import Header from "../../components/headerComponent";

export default function InsourcePage(): JSX.Element {
    const { flows, setTabId, downloadFlows, uploadFlows, addFlow } =
        useContext(TabsContext);

    // set null id
    useEffect(() => {
        setTabId("");
    }, []);

    const navigate = useNavigate();

    // Show community examples on page start
    useEffect(() => {
    }, []);

    return (
        <>
        <Header />
        <div style={{ height: "100%" }}>
            <iframe src={`${window.location.protocol}//${window.location.hostname}:8200`} style={{ width: "100%", height: "100%" }} />
        </div>
        </>
    );
}
