import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import Gallery from "./Gallery";
import ImageRecog from "./components/ImageRecog";

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/gallery">Gallery</Link>
            </li>
            <li>
              <Link to="/image_recognition">Image Recogntion</Link>
            </li>
            <li>
              <Link to="/video_recognition">Video Recognition</Link>
            </li>
          </ul>
        </nav>

        {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Switch>
          <Route path="/gallery">
            <Gallery />
          </Route>
          <Route path="/image_recognition">
            <ImageRecog />
          </Route>
          <Route path="/video_recognition">
            <VideoRecog />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}


function VideoRecog() {
  return <h2>Users</h2>;
}
export default App;