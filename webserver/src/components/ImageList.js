import React, {Component, useState, useEffect} from 'react';
import {Carousel, Container, Row, Col, Image, Button} from 'react-bootstrap';

function Item(props) {
    const current_id = props.current_id;
    const file = props.file;
    const [image, setImage] = useState(null);
    useEffect(
        () => {
            fetch('/api/get_image/' + current_id + '/' + file)
                .then(response => response.blob())
                .then(blob => {
                    const imageUrl = URL.createObjectURL(blob);
                    const img = document.querySelector('img');
                    img.addEventListener('load', () => URL.revokeObjectURL(imageUrl));
                    document.querySelector('img').src = imageUrl;
                    setImage(imageUrl);
                });
        }
    );
    return (
        <Container>
            <Row>
                <Col>
                    <Image
                        src={image}
                    />
                </Col>
                <Col>
                    <Button>
                        X
                    </Button>
                </Col>
            </Row>
        </Container>
    )
}

function ImageCarousel(props){
    const current_id = props.current_id;
    const [files, setFiles] = useState(Array(0));

    useEffect(
        () => {
            fetch('/api/images/' + current_id)
                .then(res => res.json())
                .then(data => setFiles(data.files));
        }
    );

    return (
        <Carousel>
            {files.map(file =>{
                return (<Carousel.Item>
                    <Item
                        id={current_id}
                        file={file}
                    />
                </Carousel.Item>
                )
                }

            )}
        </Carousel>
    )
}

function ImageList(props){
   const current_id = props.current_id;
    const [files, setFiles] = useState(Array(0));

    useEffect(
        () => {
            fetch('/api/images/' + current_id)
                .then(res => res.json())
                .then(data => setFiles(data.files));
        }
    );

        return (
            <ul>
            {files.map((file) =>
                <li key={file}>
                    <Item current_id={current_id} file={file}/>
                </li>
            )}
        </ul>
        )
}

export  {ImageCarousel, ImageList};