import { useContext, useEffect, useState } from "react";
import { TabsContext } from "../../contexts/tabsContext";

import { useNavigate } from "react-router-dom";
import IconComponent from "../../components/genericIconComponent";
import Header from "../../components/headerComponent";
import { AuthContext } from "../../contexts/authContext";

export default function InsourcePage(): JSX.Element {
    const { flows, setTabId, downloadFlows, uploadFlows, addFlow } =
        useContext(TabsContext);

    const {
        isAdmin,
        isAuthenticated,
        logout,
        getAuthentication,
        userData,
        autoLogin,
    } = useContext(AuthContext);

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
            {isAdmin ? (
                <div style={{ height: "100%" }}>
                    <iframe src={`${window.location.protocol}//${window.location.hostname}:8200`} style={{ width: "100%", height: "100%" }} />
                </div>
            ) : (
                <div style={{ textAlign: "center", marginTop: "50px" }}>
                    <h2>Only admins can access this page.</h2>
                </div>
            )}
        </>
    );
}
