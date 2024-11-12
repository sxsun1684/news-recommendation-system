import { useState } from 'react';
import "./Searchbar.scss"

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    onSearch(query);
  };

  return (
      <div>
          <input
              type="text"
              placeholder="Search keywords..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
          />
          {/*<button onClick={handleSearch} style={styles.button}>Search</button>*/}
          <button onClick={handleSearch}>Search</button>
      </div>
  );
};

export default SearchBar
