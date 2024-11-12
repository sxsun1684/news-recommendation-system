// import { useState } from 'react'
import './App.scss'
import Navbar from "./components/Navbar/Narbar";
import Searchbar from './components/Searchbar/Searchbar'


function App() {
  // const [count, setCount] = useState(0)

  return (
    <>
      <h1>News Recommendation System</h1>
      <div className="card">
          <Navbar />
          <Searchbar />

      </div>
      <p className="read-the-docs">
        Stay informed with personalized news tailored to your interests.@NewsHub
      </p>
    </>
  )
}

export default App
