import {useState} from "react";

const SearchBar = ({setSearchResults}) => {
    const [query, setQuery] = useState("");

    const handleSearch = () => {
        fetch(`http://localhost:5000/search?query=${query}`)
            .then((res) => res.json())
            .then((data) => setSearchResults(data))
            .catch((err) => console.error("fail:", err));
    };

    return (
        <div className="flex items-center space-x-2 w-full bg-blue-100 text-white px-4 py-2 rounded">
            <input
                type="text"
                placeholder="Search keywords..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-grow h-[40px] px-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 box-border appearance-none"
            />
            <button
                onClick={handleSearch}
                className="flex-none h-[40px] bg-blue-500 text-white px-4 rounded-lg hover:bg-blue-600 transition-all"
            >
                Search
            </button>
        </div>
    );
};

export default SearchBar;


// import React, {useState} from "react";
//
// const SearchBar = ({setSearchResults}) => {
//     const [query, setQuery] = useState("");
//
//     const handleSearch = () => {
//         fetch(`http://localhost:5000/search?query=${query}`)
//             .then((res) => res.json())
//             .then((data) => setSearchResults(data))
//             .catch((err) => console.error("fail:", err));
//     };
//
//     return (
//         <div>
//             <input type="text" value={query} onChange={(e) => setQuery(e.target.value)}/>
//             <button onClick={handleSearch}>🔍 搜索</button>
//         </div>
//     );
// };
//
// export default SearchBar;
