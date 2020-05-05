import React, {useState, useEffect, Component} from 'react';
import logo from './logo.svg';
// import './App.css';
import FileUpload from './components/file_upload';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row"
import Col from "react-bootstrap/Col"
import 'bootstrap/dist/css/bootstrap.min.css';
import NameDropdown from "./components/dropdown";
import IdentityList from "./components/IdentityList";
class App extends Component{

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.state = {
            identities: Array(1).fill(1),
            currentIdentity: null,
        }
    }
    componentDidMount() {
        fetch('/api/identities').
        then((response) => response.json()).
        then(data => {
            this.setState({identities: data.identities})
        });
    }

    handleClick(event){
        this.setState({currentIdentity: event.target.value});
    }
    render() {
        const identities = this.state.identities;
        const currentIdentity = this.state.currentIdentity;
    return (
        <div className="App">
        {/*<header className="App-header">*/}
        {/*  <img src={logo} className="App-logo" alt="logo" />*/}
        {/*</header>*/}
        <Container>
            <Row>
                <Col> <IdentityList identities={identities} onClick={this.handleClick}/> </Col>
                <Col> {currentIdentity} </Col>
                <Col><FileUpload/></Col>
            </Row>
        </Container>
        </div>
    );
    }
}

export default App;
