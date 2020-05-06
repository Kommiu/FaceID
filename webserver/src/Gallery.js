import React, {Component} from 'react';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row"
import Col from "react-bootstrap/Col"
import 'bootstrap/dist/css/bootstrap.min.css';
import NameDropdown from "./components/dropdown";
import {IdentityForm} from './components/IdentityList'
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Form from 'react-bootstrap/Form';
import { ImageList} from './components/ImageList';
class Gallery extends Component {

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleDropdownClick = this.handleDropdownClick.bind(this);
        this.handleXClick = this.handleXClick.bind(this);
        this.handleUploadChange = this.handleUploadChange.bind(this);
        this.handleUploadClick = this.handleUploadClick.bind(this);
        this.state = {
            identities: Array(1).fill(1),
            currentIdentity: 'default',
            imageURL: null,
            selectedFile: null,
        }
    }
    componentDidMount() {
        fetch('/api/identities').then((response) => response.json()).then(data => {
            this.setState({identities: data.identities})
        });
    }

    handleClick(event) {
        this.setState({currentIdentity: event.target.value});
    }

    handleFormSubmit(event) {
        fetch('/api/add_identity', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({identity: event.target.value}),
        })
            .then(response => response.json())
            .then(data => console.log(data));
    }
    handleXClick(event) {
        fetch('/api/delete_identity', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({identity: event.target.value}),
        })
            .then(response => response.json())
            .then(data => console.log(data));
    }

    handleUploadChange(event) {
        this.setState({
            selectedFile: event.target.files[0],
            loaded: 0,
        })
    }
    handleUploadClick(event) {
        const data = new FormData()
        data.append('file', this.state.selectedFile)
        data.set('current_id', this.state.currentIdentity)
        fetch('/api/upload_image', {
            method: 'POST',
            body: data,
        })
            .then(response => response.blob())
            .then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                const img = document.querySelector('img');
                img.addEventListener('load', () => URL.revokeObjectURL(imageUrl));
                document.querySelector('img').src = imageUrl;
                this.setState({imageURL: imageUrl});
            });
    }

    handleUploadImage(ev) {
        ev.preventDefault();
        const data = new FormData();
        data.append('file', this.uploadInput.files[0]);
        data.append('identity', this.state.currentIdentity);
        fetch('/api/upload_image', {
            method: 'POST',
            body: data,
        })
            .then(response => response.blob())
            .then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                const img = document.querySelector('img');
                img.addEventListener('load', () => URL.revokeObjectURL(imageUrl));
                document.querySelector('img').src = imageUrl;
                this.setState({image: imageUrl});
            });

    }


    handleDropdownClick(event) {
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
                                current_id={currentIdentity}
                                onClick={this.handleDropdownClick}
                                onXClick={this.handleXClick}
                            />
                            <IdentityForm onClick={this.handleFormSubmit}/>
                        </Col>
                        <Col>
                            <ImageList current_id={currentIdentity} />
                        </Col>
 <Col>
                            <Row>
                                <Image src={this.state.imageURL}/>
                            </Row>
                            <Row>
                                <UploadImage
                                    selectedFile={this.state.selectedFile}
                                    onClick={this.handleUploadClick}
                                    onChange={this.handleUploadChange}
                                />
                            </Row>
                        </Col>
                    </Row>
                    <Row>
                        {/*<Col> <IdentityList identities={identities} onClick={this.handleClick}/> </Col>*/}

                    </Row>
                </Container>
            </div>
        );
    }
}

function UploadImage(props) {

    return (
        <Form.Group>
            <Form>
                <Form.File
                    id="custom-file"
                    label={props.selectedFile ? props.selectedFile.name : 'Select file'}
                    custom
                    onChange={props.onChange}
                />
            </Form>
            <Button
                onClick={props.onClick}
                block
            >
                Submit
            </Button>
        </Form.Group>
    )
}
export default Gallery;
