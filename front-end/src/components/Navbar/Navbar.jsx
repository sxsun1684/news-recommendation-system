import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-gray-10 shadow-lg py-5"> {/* 增加阴影并调整导航栏高度 */}
      <ul className="flex justify-center items-center space-x-8 list-none"> {/* 增加间距 */}
        <li><Link to="/" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Home</Link></li> {/* 增加字体大小 */}
        <li><Link to="/category/business" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Business</Link></li>
        <li><Link to="/category/technology" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Technology</Link></li>
        <li><Link to="/category/sport" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Sport</Link></li>
        <li><Link to="/category/culture" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Culture</Link></li>
        <li><Link to="/category/arts" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Arts</Link></li>
        <li><Link to="/category/travel" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Travel</Link></li>
        <li><Link to="/category/earth" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Earth</Link></li>
        <li><Link to="/category/innovation" className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition">Innovation</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;

