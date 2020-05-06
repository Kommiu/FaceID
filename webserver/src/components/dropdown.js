import React, {Component} from 'react'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownToggle from "react-bootstrap/DropdownToggle";
import DropdownMenu from "react-bootstrap/DropdownMenu";
import {DropdownItem} from "react-bootstrap";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Row from 'react-bootstrap/Row';

function NameDropdown(props) {
    const identities = props.identities;
    return (<Dropdown >
        <Dropdown.Toggle block variant="success" id="dropdown-basic">
            {props.current_id}
        </Dropdown.Toggle>
        <DropdownMenu>
            {identities.map(option => (
                <DropdownItem as='button' onClick={props.onClick}>
                    <Row>
                       <Col><Button block>{option}</Button></Col>
                    <Col><Button value={option} onClick={props.onXClick}>X</Button></Col>
                    </Row>


                </DropdownItem>
            ))}
        </DropdownMenu>
    </Dropdown>
    );
}


export default NameDropdown;
