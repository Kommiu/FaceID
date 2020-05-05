import React, {Component} from 'react'
import DropdownButton from 'react-bootstrap/DropdownButton'
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownToggle from "react-bootstrap/DropdownToggle";
import DropdownMenu from "react-bootstrap/DropdownMenu";
import {DropdownItem} from "react-bootstrap";


class NameDropdown extends Component{
    constructor(props) {
        super(props);
        this.toggle = this.toggle.bind(this);
        this.select = this.select.bind(this);
        this.state = {
            dropdownOpen: false,
            value : "Home",
            options: props.options,
        };
    }
    toggle(){
        this.setState({
            dropdownOpen: !this.state.dropdownOpen,
        });
    }
    select(event){
        this.setState({
            dropdownOpen: !this.state.dropdownOpen,
            value: event.target.innerText,
        });
    }
    render(){
        return <Dropdown isOpen={this.state.dropdownOpen} toglle={this.toggle}>
            <DropdownToggle>
                {this.state.value}
            </DropdownToggle>
            <DropdownMenu>
                {this.state.options.map(option => (
                    <DropdownItem onClick={this.select}>
                        {option}
                    </DropdownItem>
                ))}
            </DropdownMenu>
        </Dropdown>
    }
}

export default NameDropdown;
