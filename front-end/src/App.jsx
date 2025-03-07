import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import './App.scss';
import Navbar from "./components/Navbar/Navbar";
import Searchbar from './components/Searchbar/Searchbar';
import CategoryPage from './pages/CategoryPage';
import HomePage from './pages/HomePage';

function App() {
    return (
        <Router>
            <Navbar/>
            <Searchbar/>
            <Routes>
                <Route path="/" element={<HomePage/>}/> {/* 主页 */}
                <Route path="/category/:categoryName" element={<CategoryPage/>}/> {/* 分类页面 */}
            </Routes>
        </Router>
    );
}

export default App;
