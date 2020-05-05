import React from 'react';
import Image from 'react-bootstrap/Image'
class File_upload extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      image: 'None',
      identity: props.identity,
    };

    this.handleUploadImage = this.handleUploadImage.bind(this);
  }

  handleUploadImage(ev) {
    ev.preventDefault();

      const data = new FormData();
      const identity = this.state.identity;
      data.append('file', this.uploadInput.files[0]);
      data.append('identity', identity)

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
              console.log(identity);
              this.setState({image: imageUrl});
          });

  }

  render() {
      const response = this.state.image;
    return (
      <form onSubmit={this.handleUploadImage}>
        <div>
          <input ref={(ref) => { this.uploadInput = ref; }} type="file" />
        </div>
        <br />
        <div>
          <button>Upload</button>
        </div>
        <div>
            <Image src={response}/>
        </div>
      </form>
    );
  }
}

export default File_upload;