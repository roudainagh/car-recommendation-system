import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom"
import Home from "./pages/Home"
import Form from "./pages/Form"
import Loading from "./pages/Loading"
import Result from "./pages/Result"

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Home />} />

        <Route path="/form" element={<Form />} />

        <Route path="/loading" element={<Loading />} />

        <Route path="/result" element={<Result />} />

      </Routes>

    </BrowserRouter>
  )
}

export default App