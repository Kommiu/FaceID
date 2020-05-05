import React, {Component} from 'react';
// import './App.css';
import FileUpload from './components/file_upload';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row"
import Col from "react-bootstrap/Col"
import 'bootstrap/dist/css/bootstrap.min.css';
import NameDropdown from "./components/dropdown";
import {IdentityList, IdentityForm } from './components/IdentityList'
class App extends Component{

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleDropdownClick = this.handleDropdownClick.bind(this);
        this.handleXClick = this.handleXClick.bind(this);
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
    handleFormSubmit(event){
        fetch('/api/add_identity',{
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({identity: event.target.value}),
        })
            .then(response => response.json())
            .then(data => console.log(data));
    }
    handleXClick(event){
        fetch('/api/delete_identity',{
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({identity: event.target.value}),
        })
            .then(response => response.json())
            .then(data => console.log(data));
    }

    handleDropdownClick(event){
        console.log(event.target.innerText);
        this.setState({currentIdentity: event.target.innerText});
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

                <Col>
                    <NameDropdown
                        identities={identities}
                        onClick={this.handleDropdownClick}
                        onXClick={this.handleXClick}
                    />
                </Col>
                <Col>
                    <div>{currentIdentity}</div>
                </Col>
            </Row>
            <Row>
                {/*<Col> <IdentityList identities={identities} onClick={this.handleClick}/> </Col>*/}
               <Col>
                   <IdentityForm onClick={this.handleFormSubmit}/>
                </Col>
                <Col><FileUpload identity={currentIdentity}/></Col>
            </Row>
        </Container>
        </div>
    );
    }
}

export default App;
