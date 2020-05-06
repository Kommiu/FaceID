import React from 'react';
import Image from 'react-bootstrap/Image'


function FileUpload(props){
    const image_url = props.image_url;
   return (
      <form onSubmit={props.handleUploadImage}>
        <div>
          <input ref={(ref) => { props.uploadInput = ref; }} type="file" />
        </div>
        <br />
        <div>
          <button>Upload</button>
        </div>
        <div>
            <Image src={image_url}/>
        </div>
      </form>
)
}


export default FileUpload;