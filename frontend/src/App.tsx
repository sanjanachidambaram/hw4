import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar";
import ChatWidget from "./components/ChatWidget";
import HomePage from "./pages/HomePage";
import ProductsPage from "./pages/ProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import AboutPage from "./pages/AboutPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import NotFoundPage from "./pages/NotFoundPage";
import FavoritesPage from "./pages/FavoritesPage";
import QuizPage from "./pages/QuizPage";

export default function App() {
  return (
    <>
      <NavBar />
      <main className="page">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:productId" element={<ProductDetailPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer className="footer">© 2026 Campus Customs · New Haven, CT</footer>
      <ChatWidget />
    </>
  );
}
