import React, {useState, useEffect} from 'react';
import logo from './logo.svg';
// import './App.css';
import FileUpload from './components/file_upload';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row"
import Col from "react-bootstrap/Col"
import 'bootstrap/dist/css/bootstrap.min.css';
import NameDropdown from "./components/dropdown";

function App() {
    const [names, setNames] = useState([0]);
    useEffect(() => {
            fetch('/persons').then(res => res.json()).then(data => {
                setNames(data.names);
            });
        },
        []
    );
    return (
        <div className="App">
            {/*<header className="App-header">*/}
            {/*  <img src={logo} className="App-logo" alt="logo" />*/}
            {/*</header>*/}
            <Container>
                <Row>
                    <Col><NameDropdown options={() => names}/></Col>
                    <Col>{names}</Col>
                    <Col><FileUpload/></Col>
                </Row>
            </Container>
        </div>
    );
}

export default App;
