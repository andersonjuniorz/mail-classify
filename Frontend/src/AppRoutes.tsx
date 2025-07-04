import { BrowserRouter, Route, Routes } from "react-router";

// Pages
import Home from "./pages/Home";

const AppRoutes = () => {
    return(
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
            </Routes>
        </BrowserRouter>
    );
}

export default AppRoutes;