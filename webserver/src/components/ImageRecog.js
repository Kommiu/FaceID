import React, {Component} from 'react';
// import './App.css';
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row"
import Col from "react-bootstrap/Col"
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Image from 'react-bootstrap/Image';
import Form from 'react-bootstrap/Form';

class ImageRecog extends Component {

    constructor(props) {
        super(props);
        this.handleUploadChange = this.handleUploadChange.bind(this);
        this.handleUploadClick = this.handleUploadClick.bind(this);
        this.state = {
            imageURL: null,
            selectedFile: null,
        }
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
        fetch('/api/detect_face', {
            method: 'POST',
            body: data,
        })
            .then(response => {
                this.setState({pred: response.headers.get('X-Extra-Info-JSON')})
                response.blob()
                    .then(blob => {
                        const imageUrl = URL.createObjectURL(blob);
                        const img = document.querySelector('img');
                        img.addEventListener('load', () => URL.revokeObjectURL(imageUrl));
                        document.querySelector('img').src = imageUrl;
                        this.setState({imageURL: imageUrl});
                    });
            });
    }


    render() {
        return (
            <div className="App">
                <Container>
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
                        <Row>
                            {this.state.pred}
                        </Row>
                    </Col>
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
export default ImageRecog;
