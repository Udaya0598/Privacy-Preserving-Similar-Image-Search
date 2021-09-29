import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import Login from "./Login";
import UploadImage from "./UploadImage";
import SimilarImage from "./SimilarImage";
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";

const RootWrapper = (props) => {
  return (
    <Router>
      <Switch>
        <Route path="/login">
          <Login />
        </Route>
        <Route path="/upload">
          <UploadImage batch={false}/>
        </Route>
        <Route path="/batch-upload">
          <UploadImage batch={true}/>
        </Route>
        <Route exact path="/">
          <SimilarImage />
        </Route>
        <Route path="/similar">
          <SimilarImage />
        </Route>
      </Switch>
    </Router>
  );
};

ReactDOM.render(<RootWrapper />, document.getElementById("container"));
