import React, {Component} from 'react';
import Button from 'react-bootstrap/Button';

function Identity(props){
    return <Button
        variant='primary'
        onClick={props.onClick}
        block
        value={props.name}
    >
        {props.name}
    </Button>
}

function IdentityList(props){
    const identities = props.identities;
    return (
        <ul>
            {identities.map((identity) =>
                <li key={identity}>
                    <Identity name={identity} onClick={props.onClick}/>
                </li>
            )}
        </ul>
    );
}

export default IdentityList;
