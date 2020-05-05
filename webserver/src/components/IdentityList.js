import React, {useState} from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

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

function IdentityForm(props){
    const [identity, setIdentity] = useState('');
    return <Form>
        <Form.Label>New identity </Form.Label>
        <Form.Control as='textarea' onChange={(event)=>setIdentity(event.target.value)}></Form.Control>
        <Button variant="primary" type="submit" onClick={props.onClick} value={identity}>
            Submit
        </Button>
    </Form>
}

export {IdentityList, IdentityForm};
